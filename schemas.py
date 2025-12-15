from pydantic import BaseModel,EmailStr
from datetime import date

# ---------- USER ----------

# ---------- REGISTER ----------
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


# ---------- LOGIN ----------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ---------- RESPONSE ----------
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


# ---------- INVOICE ----------

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

    class Config:
        from_attributes = True
