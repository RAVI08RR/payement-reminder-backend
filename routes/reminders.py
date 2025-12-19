from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Reminder, User, Invoice
from schemas import ReminderCreate, ReminderResponse

router = APIRouter(prefix="/reminders", tags=["Reminders"])

@router.post("/create", response_model=ReminderResponse)
def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = Reminder(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder

@router.get("/user/{user_id}/reminders", response_model=list[ReminderResponse])
def get_user_reminders(user_id: int, db: Session = Depends(get_db)):
    return db.query(Reminder).filter(Reminder.user_id == user_id)\
        .order_by(Reminder.sent_at.desc()).all()

@router.get("/admin/reminders", response_model=list[ReminderResponse])
def get_all_reminders(db: Session = Depends(get_db)):
    return db.query(Reminder).order_by(Reminder.sent_at.desc()).all()
