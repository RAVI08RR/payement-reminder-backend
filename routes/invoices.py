from fastapi import APIRouter
from database import db
from models import Invoice
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def list_invoices():
    invoices = await db.invoices.find().to_list(100)
    for i in invoices:
        i["_id"] = str(i["_id"])
    return invoices

@router.post("/")
async def create_invoice(invoice: Invoice):
    result = await db.invoices.insert_one(invoice.dict())
    return {"id": str(result.inserted_id)}
