from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, engine
from models import User,Invoice
from models import Base, User
from schemas import UserCreate, InvoiceCreate, InvoiceResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend Working 👍"}

@app.post("/addUsers")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()


# invoices

@app.post("/ceateInvoice", response_model=InvoiceResponse)
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    db_invoice = Invoice(**invoice.dict())
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@app.get("/getInvoices", response_model=list[InvoiceResponse])
def get_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()


