from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import status
from .database import engine, Base
from . import models
from app.agent.graph import build_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# create tables if not using alembic
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=GROQ_API_KEY
)


agent = build_agent(llm)

from typing import Optional
from . import utils

@app.post("/agent/order")
def agent_order(
    query: str,
    user: Optional[models.Users] = Depends(utils.get_current_user_optional)
):
    result = agent.invoke({"user_query": query, "user": user})
    return {"message": result["response"]}


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