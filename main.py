from fastapi import FastAPI
from database import engine
from models import Base
from routes import users, invoices
from fastapi.middleware.cors import CORSMiddleware
from routes import admin, reminders


try:
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to initialize database: {e}")
    # We continue so the health check endpoint can still run and we see logs

app = FastAPI(title="Payment Reminder Backend")
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # credentials=True is incompatible with allow_origins=["*"]
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
