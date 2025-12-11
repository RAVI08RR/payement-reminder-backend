from pydantic import BaseModel
from datetime import date


class UserCreate(BaseModel):
    name: str
    email: str


class InvoiceCreate(BaseModel):
    invoice_number: str
    customer_name: str
    amount: float
    issue_date: date
    due_date: date
    status: str = "Pending"
    user_id: int


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_name: str
    amount: float
    issue_date: date
    due_date: date
    status: str
    user_id: int

    class Config:
        orm_mode = True