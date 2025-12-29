from app.database import SessionLocal
from app import crud
import requests

ORDER_API = "http://localhost:8000/orders/order-product"

def get_product_by_name(name: str):
    db = SessionLocal()
    try:
        return crud.get_product_by_name(db, name)
    finally:
        db.close()


def place_order(user, product_id: int, quantity: int):
    db = SessionLocal()
    try:
        # Resolve shipping address (simplistic logic: use default or first available)
        shipping_id = None
        # Accessing user.addresses might require the user object to be bound to a session 
        # or have eager loaded addresses. If user session is closed, this might fail.
        # But commonly in FastAPI with Depends, the session is open during request processing.
        if user.addresses:
            for addr in user.addresses:
                if addr.is_default_shipping:
                    shipping_id = addr.address_id
                    break
            if not shipping_id:
                shipping_id = user.addresses[0].address_id
        
        if not shipping_id:
            return {"error": "No shipping address found. Please add an address to your profile."}

        order = crud.create_order_buy_now(
            db,
            user=user,
            product_id=product_id,
            quantity=quantity,
            shipping_address_id=shipping_id
        )
        return {"order_id": order.id, "message": "Order placed successfully!"}
    except Exception as e:
        return {"error": f"Failed to place order: {str(e)}"}
    finally:
        db.close()
