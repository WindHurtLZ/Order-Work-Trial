import json
import asyncio
from fastapi import APIRouter, WebSocket
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import Order

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.active_connections.append(websocket)

    async def broadcast(self, message: str):
        async with self.lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    self.active_connections.remove(connection)

    async def disconnect(self, websocket: WebSocket):
        async with self.lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)


manager = ConnectionManager()


async def get_orders_json(db: Session):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [
        {
            "id": order.id,
            "symbol": order.symbol,
            "price": float(order.price),
            "quantity": order.quantity,
            "status": order.status.value,
            "created_at": order.created_at.isoformat()
        }
        for order in orders
    ]


@router.websocket("/orders")
async def websocket_endpoint(websocket: WebSocket):
    db = next(get_db())
    await manager.connect(websocket)

    try:
        # Send initial orders
        orders = await get_orders_json(db)
        await websocket.send_json(orders)

        # Keep connection alive
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)
        db.close()