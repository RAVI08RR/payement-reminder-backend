from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, PasswordResetToken
from schemas import ForgotPasswordRequest, TokenValidationRequest, ResetPasswordFlowRequest
from utils.auth_utils import generate_secure_token, send_reset_email
from utils.security import hash_password
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

def handle_forgot_password(email: str, role: str, db: Session):
    # Verify email exists with the correct role
    user = db.query(User).filter(User.email == email, User.role == role).first()
    
    # We always return the same message to prevent email enumeration
    success_message = {"message": "If the email exists, a reset link has been sent"}
    
    if not user:
        return success_message

    # Generate token and set expiry (15 minutes)
    token = generate_secure_token()
    expiry = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Save token to DB
    reset_token = PasswordResetToken(
        email=email,
        token=token,
        role=role,
        expires_at=expiry
    )
    db.add(reset_token)
    db.commit()
    
    # Send email
    send_reset_email(email, token)
    
    return success_message

@router.post("/user/forgot-password")
def user_forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return handle_forgot_password(request.email, "user", db)

@router.post("/admin/forgot-password")
def admin_forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return handle_forgot_password(request.email, "admin", db)

@router.post("/validate-reset-token")
def validate_reset_token(request: TokenValidationRequest, db: Session = Depends(get_db)):
    token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == request.token).first()
    
    if not token_record:
        return {"valid": False, "message": "Invalid token"}
    
    if token_record.expires_at < datetime.now(timezone.utc):
        return {"valid": False, "message": "Token has expired"}
    
    return {"valid": True, "message": "Token is valid"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordFlowRequest, db: Session = Depends(get_db)):
    token_record = db.query(PasswordResetToken).filter(PasswordResetToken.token == request.token).first()
    
    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    if token_record.expires_at < datetime.now(timezone.utc):
        db.delete(token_record)
        db.commit()
        raise HTTPException(status_code=400, detail="Token has expired")
    
    # Find the user/admin
    user = db.query(User).filter(User.email == token_record.email, User.role == token_record.role).first()
    if not user:
        db.delete(token_record)
        db.commit()
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update password
    user.password = hash_password(request.new_password)
    
    # Delete token (one-time use)
    db.delete(token_record)
    
    db.commit()
    
    return {"message": "Password reset successful"}
