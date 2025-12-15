from fastapi import FastAPI
from database import engine
from models import Base
from routes import users, invoices

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Reminder Backend")

app.include_router(users.router)
app.include_router(invoices.router)

@app.get("/")
def health():
    return {"status": "Backend running 🚀"}
