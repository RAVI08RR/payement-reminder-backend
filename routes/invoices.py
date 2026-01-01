from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Invoice, User
from schemas import InvoiceCreate, InvoiceResponse

router = APIRouter(prefix="/users/{user_id}/invoices", tags=["Invoices"])

@router.post("/create", response_model=InvoiceResponse)
def create_invoice(
    user_id: int,
    invoice: InvoiceCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_invoice = Invoice(
        **invoice.dict(),
        user_id=user_id,
        user_email=user.email
    )

    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


@router.get("/", response_model=list[InvoiceResponse])
def get_user_invoices(
    user_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Invoice).filter(Invoice.user_id == user_id).all()


@router.get("/all", response_model=list[InvoiceResponse])
def get_all_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()
