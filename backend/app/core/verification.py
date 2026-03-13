import secrets
import string
from datetime import datetime, timedelta, timezone

def create_verification_token():
    # Generate a 6-digit numeric OTP
    otp = ''.join(secrets.choice(string.digits) for _ in range(6))
    # OTP expires in 10 minutes
    expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    return otp, expiry
