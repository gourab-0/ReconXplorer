from fastapi import APIRouter, Depends, HTTPException, Response, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.refresh_token import RefreshTokenStore
from app.core.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    create_refresh_token, 
    validate_password_complexity, 
    decode_token,
    generate_csrf_token,
    hash_token
)
from app.dependencies import get_current_user
from app.api.schemas.user import UserOut, UserUpdate
from app.core.verification import create_verification_token
from app.services.email_service import send_verification_email, send_admin_notification, send_security_alert
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str

class ResendEmail(BaseModel):
    email: EmailStr

# ---------------- REGISTER ----------------
@router.post("/register")
async def register(
    data: UserRegister, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    if not validate_password_complexity(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 10 characters long and contain a number, a letter, and a special character.",
        )

    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    token, expiry = create_verification_token()

    user = User(
        email=data.email,
        full_name=data.full_name,
        organization=data.organization,
        password_hash=hash_password(data.password),
        verification_token=token,
        verification_expiry=expiry,
        is_verified=False,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Use background tasks for better performance
    background_tasks.add_task(send_verification_email, user.email, token)
    background_tasks.add_task(send_admin_notification, user.email, user.full_name)

    return {"message": "User registered. Please enter the OTP sent to your email to verify your account."}


# ---------------- LOGIN ----------------
@router.post("/login")
async def login(
    data: UserLogin, 
    request: Request, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Check for lockout
    if user.locked_until:
        if user.locked_until.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to too many failed attempts. Try again later.",
            )
        else:
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    if not verify_password(data.password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)
            background_tasks.add_task(
                send_security_alert, 
                "Account Lockout", 
                f"User {user.email} has been locked out after 5 failed attempts.",
                user.email
            )
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # IP Tracking (No email alert per request)
    current_ip = request.client.host if request.client else "unknown"
    user.last_login_ip = current_ip

    # Reset on success
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended. Please contact support.",
        )

    token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token hash in DB
    db.add(RefreshTokenStore(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=7)
    ))
    db.commit()

    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": token
    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.SECURE_COOKIES,          # True in production
        samesite="lax",        # OK for same-site dev
        path="/",
    )
    
    # CSRF Token Cookie (JS-readable so frontend can send it back in headers)
    csrf_token = generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False, # MUST be False for frontend to read
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        path="/"
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        path="/api/auth/refresh", # More specific path for security
    )

    return response


# ---------------- CURRENT USER ----------------
@router.get("/me", response_model=UserOut)
def me(
    response: Response,
    user_payload=Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    user_id = user_payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Refresh CSRF token on session check
    csrf_token = generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=settings.SECURE_COOKIES,
        samesite="lax",
        path="/"
    )
    
    return user


# ---------------- UPDATE USER ----------------
@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    user_payload=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = user_payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        # Check if email is taken by another user
        existing = db.query(User).filter(User.email == data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = data.email
    if data.organization is not None:
        user.organization = data.organization

    db.commit()
    db.refresh(user)
    return user


# ---------------- LOGOUT ----------------
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

# ---------------- REFRESH TOKEN ----------------
@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        # 1. Decode token
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
             raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        
        # 2. Check DB for token hash (Rotation check)
        token_hash = hash_token(refresh_token)
        db_token = db.query(RefreshTokenStore).filter(
            RefreshTokenStore.token_hash == token_hash,
            RefreshTokenStore.user_id == user_id,
            RefreshTokenStore.is_revoked == False
        ).first()
        
        if not db_token:
            # If token hash not found but JWT was valid, it might be a replay attack (stolen old token)
            # Log security event and revoke all tokens for this user for safety
            db.query(RefreshTokenStore).filter(RefreshTokenStore.user_id == user_id).update({"is_revoked": True})
            db.commit()
            raise HTTPException(status_code=401, detail="Refresh token reused or revoked")

        # 3. Check expiration
        if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            db.delete(db_token)
            db.commit()
            raise HTTPException(status_code=401, detail="Refresh token expired")

        # 4. Verify user still exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
             raise HTTPException(status_code=401, detail="User not found")

        # 5. Issue new tokens (Rotation)
        new_access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Delete old token, store new one
        db.delete(db_token)
        db.add(RefreshTokenStore(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=7)
        ))
        db.commit()
        
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            path="/"
        )
        
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=settings.SECURE_COOKIES,
            samesite="lax",
            path="/api/auth/refresh"
        )
        
        return {"message": "Token rotated successfully"}
    except Exception:
         raise HTTPException(status_code=401, detail="Authentication failed")


# ---------------- VERIFY OTP ----------------
@router.post("/verify-otp")
def verify_otp(data: VerifyOTP, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(404, "User not found")

    if user.is_verified:
        return {"message": "Account already verified"}

    if user.verification_token != data.otp:
        raise HTTPException(400, "Invalid OTP")

    now = datetime.now(timezone.utc)
    expiry = user.verification_expiry
    if expiry and expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)

    if not expiry or expiry < now:
        raise HTTPException(400, "OTP expired")

    user.is_verified = True
    user.verification_token = None
    user.verification_expiry = None
    db.commit()

    return {"message": "Email verified successfully. You can now login."}


# ---------------- RESEND VERIFICATION ----------------
@router.post("/resend-verification")
async def resend_verification(
    data: ResendEmail,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        # Security: return success even if user not found to prevent user enumeration
        return {"message": "If this account exists and is unverified, a new OTP has been sent."}

    if user.is_verified:
        return {"message": "Account is already verified."}

    token, expiry = create_verification_token()
    user.verification_token = token
    user.verification_expiry = expiry
    db.commit()

    background_tasks.add_task(send_verification_email, user.email, token)

    return {"message": "New OTP sent to your email."}