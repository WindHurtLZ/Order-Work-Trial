import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
from starlette.background import BackgroundTask

from app.database.database import get_db, SessionLocal
from app.models.models import Order
from app.enums import OrderStatus
from app.api.websockets import manager, get_orders_json

router = APIRouter()


class OrderCreate(BaseModel):
    symbol: str
    price: float
    quantity: int
    order_type: str

    @field_validator('symbol')
    def symbol_uppercase(cls, v):
        if not v.isupper():
            raise ValueError('Symbol must be uppercase')
        return v

    @field_validator('order_type')
    def validate_order_type(cls, v):
        if v not in ('limit', 'market'):
            raise ValueError('Invalid order type')
        return v


@router.post("/orders", status_code=201)
async def create_order(order: OrderCreate, db: Session = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    if order.price <= 0 or order.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price and quantity must be positive values"
        )

    db_order = Order(
        symbol=order.symbol,
        price=order.price,
        quantity=order.quantity,
        order_type=order.order_type,
        status=OrderStatus.PENDING
    )

    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)

        # broadcast when update
        updated_orders = await get_orders_json(db)
        await manager.broadcast(json.dumps(updated_orders))

        background_tasks.add_task(simulate_execution, db_order.id)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "id": db_order.id,
        "symbol": db_order.symbol,
        "price": db_order.price,
        "quantity": db_order.quantity,
        "status": db_order.status.value,
        "created_at": db_order.created_at.isoformat()
    }

@router.get("/orders")
async def get_orders(
        symbol: str = None,
        status: OrderStatus = None,
        db: Session = Depends(get_db)
):
    query = db.query(Order)

    if symbol:
        query = query.filter(Order.symbol == symbol.upper())
    if status:
        query = query.filter(Order.status == status)

    return query.order_by(Order.created_at.desc()).all()


# update to executed 3s after placed order
async def simulate_execution(order_id: int):
    await asyncio.sleep(3)
    db = SessionLocal()

    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return

        order.status = OrderStatus.EXECUTED
        db.commit()
        db.refresh(order)

        # broadcast
        updated_orders = await get_orders_json(db)
        await manager.broadcast(json.dumps(updated_orders))
    finally:
        db.close()