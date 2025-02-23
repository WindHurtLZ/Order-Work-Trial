import datetime
from fastapi import Request
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import orders, websockets
from app.database.database import engine
from app.database.models import Base
from fastapi.templating import Jinja2Templates

app = FastAPI(
    title="Trading Platform API",
    description="Real-time Trading System with WebSocket Support",
    version="0.1.0",
    openapi_url="/api/openapi.json"
)

# Create table migration
@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

# CORS Config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/api")
app.include_router(websockets.router, prefix="/ws")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.utcnow()}