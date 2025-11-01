from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
from .database import engine, Base
from . import models

# create tables if not using alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": "Oops! error"},
    )

# include routers
from .routers import auth, users, addresses, categories, products, cart, orders, payments, reviews, shipping

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(addresses.router)
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(reviews.router)
app.include_router(shipping.router)
