from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User,Invoice
from schemas import UserResponse,InvoiceResponse, UserUpdate, ForgotPasswordRequest, ResetPasswordRequest, ResetPasswordIDRequest
from utils.security import hash_password
from sqlalchemy.orm import joinedload
from sqlalchemy import func, case
from datetime import date, timedelta


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/invoices", response_model=list[InvoiceResponse])
def get_all_invoices(db: Session = Depends(get_db)):
    invoices = (
        db.query(Invoice)
        .options(joinedload(Invoice.user))
        .all()
    )
    return invoices


@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    today = date.today()
    week_end = today + timedelta(days=7)

    # 1️⃣ STATS CARDS
    total_pending = db.query(
        func.coalesce(func.sum(Invoice.amount), 0)
    ).filter(Invoice.status == "Pending").scalar()

    due_today = db.query(Invoice).filter(
        Invoice.due_date == today,
        Invoice.status == "Pending"
    ).count()

    completed_month = db.query(Invoice).filter(
        Invoice.status == "Paid",
        func.date_part("month", Invoice.issue_date) == today.month,
        func.date_part("year", Invoice.issue_date) == today.year
    ).count()

    overdue = db.query(Invoice).filter(
        Invoice.due_date < today,
        Invoice.status == "Pending"
    ).count()

    # 2️⃣ EXPECTED COLLECTION
    expected_collection = db.query(
        func.coalesce(func.sum(Invoice.amount), 0)
    ).filter(
        Invoice.due_date.between(today, week_end),
        Invoice.status == "Pending"
    ).scalar()

    # 3️⃣ TOP OVERDUE
    top_overdue = db.query(Invoice).filter(
        Invoice.due_date < today,
        Invoice.status == "Pending"
    ).order_by(Invoice.due_date.asc()).limit(3).all()

    # 4️⃣ MONTHLY PAYMENT TREND (BAR GRAPH)
    monthly_trend = db.query(
        func.to_char(Invoice.issue_date, 'Mon').label("month"),
        func.sum(
            case((Invoice.status == "Paid", Invoice.amount), else_=0)
        ).label("paid"),
        func.sum(
            case((Invoice.status == "Pending", Invoice.amount), else_=0)
        ).label("pending")
    ).group_by("month").order_by("month").all()

    # 5️⃣ PAYMENT STATUS (DONUT)
    paid_count = db.query(func.count()).filter(
        Invoice.status == "Paid"
    ).scalar()

    pending_count = db.query(func.count()).filter(
        Invoice.status == "Pending",
        Invoice.due_date >= today
    ).scalar()

    overdue_count = db.query(func.count()).filter(
        Invoice.status == "Pending",
        Invoice.due_date < today
    ).scalar()

    return {
        "stats": {
            "total_pending_amount": total_pending,
            "payments_due_today": due_today,
            "completed_this_month": completed_month,
            "overdue_payments": overdue
        },
        "expected_collection": {
            "amount": expected_collection,
            "period": "this_week",
            "change_percent": 15  # static for now
        },
        "top_overdue": [
            {
                "customer_name": inv.customer_name,
                "days_overdue": (today - inv.due_date).days,
                "amount": inv.amount
            }
            for inv in top_overdue
        ],
        "analytics": {
            "monthlyTrend": [
                {
                    "month": row.month.strip(),
                    "paid": row.paid,
                    "pending": row.pending
                }
                for row in monthly_trend
            ],
            "paymentStatus": {
                "paid": paid_count,
                "pending": pending_count,
                "overdue": overdue_count
            }
        }
    }
    
    
@router.put("/users/{user_id}")
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
    

