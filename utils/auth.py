from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User

def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).first()  # TEMP: first user
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
