import secrets
from datetime import datetime, timedelta, timezone

def generate_secure_token() -> str:
    """Generate a cryptographically secure URL-safe token."""
    return secrets.token_urlsafe(32)

def send_reset_email(email: str, token: str):
    """
    Mock function to simulate sending a password reset email.
    In production, this would use an SMTP library or a service like SendGrid/Mailgun.
    """
    reset_link = f"https://frontend.com/reset-password?token={token}"
    print(f"--- EMAIL SERVICE ---")
    print(f"To: {email}")
    print(f"Subject: Password Reset Request")
    print(f"Body: Please click the link below to reset your password:\n{reset_link}")
    print(f"----------------------")
    # Here you would implement actual SMTP logic if creds were available.
