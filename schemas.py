from pydantic import BaseModel,EmailStr,Field
from datetime import date, datetime
from typing import Optional

# ---------- USER ----------

# ---------- REGISTER ----------
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    role: str = "user"


# ---------- LOGIN ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- RESPONSE ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str 

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class TokenValidationRequest(BaseModel):
    token: str

class ResetPasswordFlowRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=64)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=64)

# ---------- INVOICE ----------

class InvoiceUser(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    invoice_number: str
    customer_name: str
    amount: float
    issue_date: date
    due_date: date

class InvoiceResponse(InvoiceCreate):
    id: int
    status: str
    user_id: int
    invoice_number: str
    customer_name: str
    issue_date: date
    due_date: date
    user: InvoiceUser

    class Config:
        from_attributes = True


# ---------- REMINDER ----------
class ReminderCreate(BaseModel):
    user_id: int
    invoice_id: int
    reminder_type: str = "email"
    status: str = "sent"

class ReminderResponse(BaseModel):
    id: int
    user_id: int
    invoice_id: int
    reminder_type: str
    status: str
    sent_at: datetime

    class Config:
        from_attributes = True

class ReminderCreateResponse(BaseModel):
    id: int
    reminder_type: str
    status: str
    sent_at: datetime

    user_id: int
    user_email: str

    invoice_id: int
    invoice_number: str

    class Config:
        from_attributes = True
