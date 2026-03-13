import os
from datetime import datetime
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)

async def send_verification_email(email: str, otp: str):
    message = MessageSchema(
        subject="Verify your ReconXplorer account",
        recipients=[email],
        body=f"""
Welcome to ReconXplorer.

Your verification code is: {otp}

This code expires in 10 minutes.
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_admin_notification(new_user_email: str, new_user_name: str):
    admin_email = settings.ADMIN_EMAIL
    message = MessageSchema(
        subject="New User Registration Alert - ReconXplorer",
        recipients=[admin_email],
        body=f"""
ADMIN ALERT: New User Registered

Name: {new_user_name}
Email: {new_user_email}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please review this user in the Admin Panel.
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_security_alert(event_type: str, details: str, user_email: str = "Unknown"):
    admin_email = settings.ADMIN_EMAIL
    message = MessageSchema(
        subject=f"SECURITY ALERT: {event_type} - ReconXplorer",
        recipients=[admin_email],
        body=f"""
URGENT SECURITY ALERT

Event: {event_type}
User: {user_email}
Details: {details}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action may be required. Please check audit logs.
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)

async def send_scan_notification(user_email: str, target: str, scan_type: str):
    admin_email = settings.ADMIN_EMAIL
    message = MessageSchema(
        subject=f"Scan Initiated: {target} - ReconXplorer",
        recipients=[admin_email],
        body=f"""
OPERATION ALERT: New Scan Started

User: {user_email}
Target: {target}
Type: {scan_type}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Monitor the progress in the Admin Panel.
""",
        subtype="plain",
    )

    fm = FastMail(conf)
    await fm.send_message(message)
