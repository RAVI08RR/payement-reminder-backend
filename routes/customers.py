from fastapi import APIRouter
from database import db
from models import Customer
from bson import ObjectId

router = APIRouter()

@router.get("/")
async def get_customers():
    customers = await db.customers.find().to_list(100)
    for c in customers:
        c["_id"] = str(c["_id"])
    return customers

@router.post("/")
async def create_customer(customer: Customer):
    result = await db.customers.insert_one(customer.dict())
    return {"id": str(result.inserted_id)}
