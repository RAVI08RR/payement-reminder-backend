from fastapi import FastAPI
from database import engine
from models import Base
from routes import users, invoices
from fastapi.middleware.cors import CORSMiddleware
from routes import admin, reminders


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Reminder Backend")
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # can use ["*"] for all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(users.router)
app.include_router(invoices.router)
app.include_router(reminders.router)

@app.get("/")
def health():
    return {"status": "Backend running 🚀"}
