from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey,DateTime, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    # hashed_password = Column(String, nullable=False)
    password = Column(String(150), nullable=False)
    invoices = relationship("Invoice", back_populates="user")
    role = Column(String(20), nullable=False, default="user")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String, default="Pending")

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="invoices")
    user_email = Column(String, nullable=False)



class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)

    reminder_type = Column(String, default="email")
    status = Column(String, default="sent")

    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    invoice = relationship("Invoice")

class PasswordResetToken(Base) :
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String, nullable=False)
    token = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False) # 'user' or 'admin'
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
