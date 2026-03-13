from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import secrets

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 0. Completely ignore OPTIONS requests to let CORSMiddleware handle them
        if request.method == "OPTIONS":
            return await call_next(request)

        # Generate CSP Nonce for this request
        nonce = secrets.token_urlsafe(16)
        request.state.csp_nonce = nonce

        # 1. CSRF Protection for mutable requests
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            path = request.url.path
            is_auth = "/auth/login" in path or "/auth/register" in path or "/auth/verify-otp" in path
            
            if not is_auth:
                csrf_token_header = request.headers.get("X-CSRF-Token")
                csrf_token_cookie = request.cookies.get("csrf_token")
                
                if not csrf_token_header or not csrf_token_cookie or csrf_token_header != csrf_token_cookie:
                    return Response(
                        content='{"detail": "CSRF token validation failed"}',
                        status_code=403,
                        media_type="application/json"
                    )

        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Enhanced CSP - Broadened connect-src for local dev stability
        # response.headers["Content-Security-Policy"] = (
        #     f"default-src 'self'; "
        #     f"img-src 'self' data: https:; "
        #     f"script-src 'self' 'unsafe-inline' 'nonce-{nonce}'; " 
        #     f"style-src 'self' 'unsafe-inline' 'nonce-{nonce}'; "
        #     f"font-src 'self' data: https://fonts.gstatic.com; "
        #     f"connect-src 'self' https: http: localhost:* 127.0.0.1:*;"
        # )
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (restrict powerful features)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        return response
