# app/models.py
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    role = Column(String, default="user", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(
            timezone=True),
        server_default=func.now(),
        onupdate=func.now())

    addresses = relationship(
        "Addresses",
        back_populates="user",
        cascade="all, delete-orphan")
    orders = relationship(
        "Orders",
        back_populates="user",
        cascade="all, delete-orphan")
    reviews = relationship(
        "Reviews",
        back_populates="user",
        cascade="all, delete-orphan")
    cart = relationship(
        "Cart",
        uselist=False,
        back_populates="user",
        cascade="all, delete-orphan")

    model_config = {
        "from_attributes": True
    }


class Categories(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    products = relationship(
        "Products",
        back_populates="category",
        cascade="all, delete-orphan")

    model_config = {
        "from_attributes": True
    }


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric, nullable=False)
    discount_price = Column(Numeric, nullable=True)
    stock_qty = Column(Integer, default=0)
    brand = Column(String, nullable=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.category_id"),
        nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(
            timezone=True),
        server_default=func.now(),
        onupdate=func.now())
    is_active = Column(Boolean, default=True)

    category = relationship("Categories", back_populates="products")
    reviews = relationship(
        "Reviews",
        back_populates="product",
        cascade="all, delete-orphan")
    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan")
    cart_items = relationship(
        "Cart_Items",
        back_populates="product",
        cascade="all, delete-orphan")


class Addresses(Base):
    __tablename__ = "addresses"
    address_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    street = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)

    user = relationship("Users", back_populates="addresses")


class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Added columns so order metadata persists
    total_amount = Column(Numeric, default=0)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="orders")
    order_items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan")
    payment = relationship("Payments", back_populates="order", uselist=False)
    shipping = relationship("Shipping", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Orders", back_populates="order_items")
    product = relationship("Products", back_populates="order_items")


class Cart(Base):
    __tablename__ = "cart"
    cart_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="cart")
    cart_items = relationship(
        "Cart_Items",
        back_populates="cart",
        cascade="all, delete-orphan")


class Cart_Items(Base):
    __tablename__ = "cart_items"
    cart_item_id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("cart.cart_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Products", back_populates="cart_items")


class Payments(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_method = Column(String, nullable=True)
    amount = Column(Numeric, nullable=True)
    status = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Orders", back_populates="payment")


class Reviews(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("Users", back_populates="reviews")
    product = relationship("Products", back_populates="reviews")


class Shipping(Base):
    __tablename__ = "shipping"
    shipment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    courier_name = Column(String, nullable=True)
    tracking_number = Column(String, nullable=True)
    status = Column(String, nullable=True)
    estimated_delivery = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    order = relationship("Orders", back_populates="shipping")
