from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Reminder, User, Invoice
from schemas import ReminderCreate, ReminderResponse, ReminderCreateResponse

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.post("/reminders/create")
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db)):

    invoice = db.query(Invoice).filter(Invoice.id == payload.invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reminder = Reminder(
        user_id=user.id,
        invoice_id=invoice.id,
        reminder_type=payload.reminder_type,
        status="sent"
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    # 👇 THIS IS THE IMPORTANT PART
    return {
        "reminder_id": reminder.id,
        "user_email": user.email,
        "customer_name": invoice.customer_name,
        "invoice_number": invoice.invoice_number,
        "amount": invoice.amount,
        "due_date": invoice.due_date,
        "sent_at": reminder.sent_at
    }


@router.get("/user/{user_id}/reminders", response_model=list[ReminderResponse])
def get_user_reminders(user_id: int, db: Session = Depends(get_db)):
    return db.query(Reminder).filter(Reminder.user_id == user_id)\
        .order_by(Reminder.sent_at.desc()).all()

@router.get("/admin/reminders", response_model=list[ReminderResponse])
def get_all_reminders(db: Session = Depends(get_db)):
    return db.query(Reminder).order_by(Reminder.sent_at.desc()).all()
