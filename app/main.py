from fastapi import FastAPI

from app.routers.orders import router as orders_router

app = FastAPI(title="Order Management System")

app.include_router(orders_router, prefix="/api")
