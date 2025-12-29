from decimal import Decimal
from app.models import Cart, Cart_Items, Orders, OrderItem, Products
from app.models import Cart, Products, Cart_Items
from sqlalchemy.orm import Session
from app import models, schemas
from app.utils import hash_password
from app.models import Products

# -------------------- USERS --------------------


def get_user_by_email(db: Session, email: str):
    return db.query(models.Users).filter(models.Users.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(
        models.Users).filter(
        models.Users.user_id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.Users(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Users).offset(skip).limit(limit).all()


def update_user_role(db: Session, user_id: int, new_role: str):
    user = get_user_by_id(db, user_id)
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
    return None


def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

# -------------------- CATEGORIES --------------------


def create_category(db: Session, category: schemas.CategoryCreate):
    new_category = models.Categories(
        category_name=category.category_name,
        description=category.description
    )
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def get_category_by_id(db: Session, category_id: int):
    return db.query(models.Categories).filter(
        models.Categories.category_id == category_id).first()


def get_all_categories(db: Session):
    return db.query(models.Categories).all()


def update_category(
        db: Session,
        category_id: int,
        updated: schemas.CategoryCreate):
    category = get_category_by_id(db, category_id)
    if not category:
        return None
    category.category_name = updated.category_name
    category.description = updated.description
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: int):
    category = get_category_by_id(db, category_id)
    if not category:
        return None
    db.delete(category)
    db.commit()
    return True

# -------------------- PRODUCTS --------------------


def create_product(db: Session, payload: schemas.ProductCreate):
    db_product = models.Products(
        name=payload.name,  # payload.name maps to JSON 'product_name'
        description=payload.description,
        price=payload.price,
        discount_price=payload.discount_price or 0,
        stock_qty=payload.stock_qty or 0,
        brand=payload.brand,
        category_id=payload.category_id,
        is_active=payload.is_active
    )

    product_data = payload.model_dump()
    product = models.Products(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product(db: Session, product_id: int):
    return db.query(models.Products).filter(
        models.Products.id == product_id).first()


def list_products(db: Session):
    return db.query(models.Products).all()


def update_product(
        db: Session,
        product_id: int,
        payload: schemas.ProductUpdate):
    product = get_product(db, product_id)
    if not product:
        return None
    if payload.product_name is not None:
        product.name = payload.product_name
    if payload.description is not None:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price
    if payload.discount_price is not None:
        product.discount_price = payload.discount_price
    if payload.stock is not None:
        product.stock_qty = payload.stock
    if payload.brand is not None:
        product.brand = payload.brand
    if payload.category_id is not None:
        product.category_id = payload.category_id
    if payload.is_active is not None:
        product.is_active = payload.is_active

    data = payload.model_dump(exclude_unset=True)  # only fields that were sent
    for key, value in data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    if not product:
        return None
    db.delete(product)
    db.commit()
    return True



def get_product_by_name(db: Session, name: str):
    return (
        db.query(Products)
        .filter(Products.name.ilike(f"%{name}%"))
        .first()
    )



# -------------------- CARTS --------------------

def add_item_to_cart(db: Session, user, product_id: int, quantity: int):
    # Get or create the user's cart
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    # Check if the product is already in cart
    cart_item = db.query(Cart_Items).filter(
        Cart_Items.cart_id == cart.cart_id,
        Cart_Items.product_id == product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
        db.commit()
        db.refresh(cart_item)
    else:
        cart_item = Cart_Items(
            cart_id=cart.cart_id,
            product_id=product_id,
            quantity=quantity)
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)

    return cart_item


def list_cart_items(db: Session, user):
    # Get the user's cart
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        return []  # Empty list if no cart exists

    # Get all items in the cart
    items = db.query(Cart_Items).filter(
        Cart_Items.cart_id == cart.cart_id).all()

    # Optionally, include product details
    cart_list = []
    for item in items:
        product = db.query(Products).filter(
            Products.id == item.product_id).first()
        cart_list.append({
            "cart_item_id": item.cart_item_id,
            "product_id": item.product_id,
            "product_name": product.name if product else "Unknown",
            "quantity": item.quantity,
            "price": product.price if product else 0,
            "discount_price": product.discount_price if product else 0
        })

    return cart_list


def get_or_create_cart_for_user(db: Session, user):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def remove_item_from_cart(db: Session, user, cart_item_id: int):
    cart = get_or_create_cart_for_user(db, user)

    cart_item = db.query(Cart_Items).filter(
        Cart_Items.cart_id == cart.cart_id,
        Cart_Items.cart_item_id == cart_item_id
    ).first()

    if cart_item:
        db.delete(cart_item)
        db.commit()
        return True
    return False



def list_cart_items(db: Session, user):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        return []
    items = db.query(Cart_Items).filter(
        Cart_Items.cart_id == cart.cart_id).all()
    return items

# -------------------- ORDERS --------------------

def create_order_from_cart(
        db: Session,
        user,
        shipping_address_id: int = None,
        billing_address_id: int = None):
    """
    Create an order from everything in user's cart.
    Policy: If any cart item quantity > product.stock_qty => raise ValueError (reject full order).
    """
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.cart_items:
        raise ValueError("Cart is empty")

    # Validate stock for all items first
    for cart_item in cart.cart_items:
        product = db.query(Products).filter(
            Products.id == cart_item.product_id).first()
        if not product:
            raise ValueError(f"Product id {cart_item.product_id} not found")
        if product.stock_qty is None:
            raise ValueError(
                f"Product id {product.id} has no stock information")
        if cart_item.quantity > product.stock_qty:
            raise ValueError(
                f"Not enough stock for product id {product.id}. Requested {cart_item.quantity}, available {product.stock_qty}")

    order = Orders(user_id=user.id, total_amount=0, status="pending")   
    
    order = Orders(user_id=user.id, total_amount=0, status="pending")
    
    db.add(order)
    db.commit()
    db.refresh(order)

    total_amount = Decimal(0)

    # Move each cart item to order_items and reduce stock
    for cart_item in cart.cart_items:
        product = db.query(Products).filter(
            Products.id == cart_item.product_id).first()
        price = product.price - product.discount_price if product.discount_price is not None and product.discount_price > 0 else product.price
        # ensure Decimal math if using Numeric
        price_val = Decimal(str(price)) if price is not None else Decimal(0)
        total_amount += price_val * Decimal(cart_item.quantity)

        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=float(price_val)
        )
        db.add(order_item)

        # reduce stock
        product.stock_qty = product.stock_qty - cart_item.quantity
        db.add(product)

    # finalize order
    order.total_amount = total_amount
    db.commit()
    db.refresh(order)

    # clear cart items
    db.query(Cart_Items).filter(Cart_Items.cart_id == cart.cart_id).delete()
    db.commit()

    return order


def create_order_buy_now(
        db: Session,
        user,
        product_id: int,
        quantity: int,
        shipping_address_id: int = None,
        billing_address_id: int = None):
    """
    Create an order directly for a single product (Buy Now).
    Same stock policy: fail if insufficient stock.
    """
    product = db.query(Products).filter(Products.id == product_id).first()
    if not product:
        raise ValueError("Product not found")
    if quantity > product.stock_qty:
        raise ValueError(
            f"Not enough stock for product id {product.id}." 
            f"Requested {quantity}, available {product.stock_qty}")

    order = Orders(user_id=user.id, total_amount=0, status="pending")
    db.add(order)
    db.commit()
    db.refresh(order)

    price = product.price - product.discount_price if product.discount_price is not None and product.discount_price > 0 else product.price
    price_val = Decimal(str(price)) if price is not None else Decimal(0)
    total_amount = price_val * Decimal(quantity)

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=quantity,
        price=float(price_val)
    )
    db.add(order_item)

    product.stock_qty = product.stock_qty - quantity
    db.add(product)

    order.total_amount = total_amount
    db.commit()
    db.refresh(order)

    return order


def get_orders_for_user(db: Session, user: models.Users):
    return db.query(
        models.Orders).filter(
        models.Orders.user_id == user.id).all()


def create_review(db, user, payload: schemas.ReviewCreate):
    review = models.Reviews(
        user_id=user.id,
        product_id=payload.product_id,
        rating=payload.rating,
        comment=payload.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review