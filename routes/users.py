from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, Invoice
from schemas import UserRegister, UserLogin, UserResponse,UserUpdate, ForgotPasswordRequest, ResetPasswordRequest
from utils.security import hash_password, verify_password
from sqlalchemy import func, case
from datetime import date

from database import get_db


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    hashed_pwd = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
        role=user.role
        # hashed_password=hash_password(user.password)
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # verify hashed password
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "message": "Login successful",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "user_type": db_user.role
        }
    }

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this email does not exist")
    
    # In a real app, you would send an email with a reset token here.
    return {"message": "If this email is registered, you will receive a password reset link shortly."}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password reset successful"}




@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()



@router.get("/{user_id}/dashboard")
def user_dashboard(
    user_id: int,
    db: Session = Depends(get_db)
):
    # ✅ Ensure user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1️⃣ Summary
    total_invoices = db.query(func.count(Invoice.id)).filter(
        Invoice.user_id == user_id
    ).scalar()

    pending_amount = db.query(func.coalesce(func.sum(Invoice.amount), 0)).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Pending"
    ).scalar()

    total_paid = db.query(func.coalesce(func.sum(Invoice.amount), 0)).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Paid"
    ).scalar()

    next_due = db.query(Invoice.due_date).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Pending",
        Invoice.due_date >= date.today()
    ).order_by(Invoice.due_date.asc()).first()

    # 2️⃣ Monthly Trend
    trend = db.query(
        func.to_char(Invoice.issue_date, 'Mon').label("month"),
        func.sum(
            case((Invoice.status == "Paid", Invoice.amount), else_=0)
        ).label("paid"),
        func.sum(
            case((Invoice.status == "Pending", Invoice.amount), else_=0)
        ).label("pending")
    ).filter(
        Invoice.user_id == user_id
    ).group_by("month").order_by("month").all()

    # 3️⃣ Payment Status
    paid_count = db.query(func.count()).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Paid"
    ).scalar()

    pending_count = db.query(func.count()).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Pending"
    ).scalar()

    overdue_count = db.query(func.count()).filter(
        Invoice.user_id == user_id,
        Invoice.status == "Pending",
        Invoice.due_date < date.today()
    ).scalar()

    total_amount = pending_amount + total_paid
    recovery_rate = int((total_paid / total_amount) * 100) if total_amount else 0

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        },
        "summary": {
            "totalInvoices": total_invoices,
            "pendingAmount": pending_amount,
            "totalPaid": total_paid,
            "nextDueDate": next_due[0] if next_due else None
        },
        "paymentTrend": [
            {
                "month": row.month.strip(),
                "paid": row.paid,
                "pending": row.pending
            } for row in trend
        ],
        "paymentStatus": {
            "paid": paid_count,
            "pending": pending_count,
            "overdue": overdue_count
        },
        "recoveryRate": recovery_rate
    }



# --- user update endpoint ---
@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 🔄 Update name
    if data.name is not None:
        user.name = data.name

    # 🔄 Update email (check uniqueness)
    if data.email is not None:
        existing = db.query(User).filter(
            User.email == data.email,
            User.id != user_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )

        user.email = data.email


    db.commit()
    db.refresh(user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }


