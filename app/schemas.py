# app/schemas.py
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Auth / User ---


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = None


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: str
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

# --- Token ---


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    user_id: Optional[int] = None
    exp: Optional[int] = None

# --- Category & Product ---


class CategoryCreate(BaseModel):
    category_name: str
    description: Optional[str] = None


class CategoryOut(BaseModel):
    category_id: int
    category_name: str
    description: Optional[str]

    model_config = {
        "from_attributes": True
    }


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    stock_qty: Optional[int] = 0
    brand: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = True


class ProductOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    discount_price: Optional[float]
    stock_qty: int
    brand: Optional[str]
    category: Optional[CategoryOut]
    is_active: bool
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }

# --- Address ---


class AddressCreate(BaseModel):
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    is_default_shipping: Optional[bool] = False
    is_default_billing: Optional[bool] = False


class AddressOut(AddressCreate):
    address_id: int
    model_config = {
        "from_attributes": True
    }

# --- Cart ---


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartItemOut(BaseModel):
    cart_item_id: int
    product: ProductOut
    quantity: int
    model_config = {
        "from_attributes": True
    }


class CartOut(BaseModel):
    cart_id: int
    cart_items: List[CartItemOut] = []
    model_config = {
        "from_attributes": True
    }

# --- Order ---


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    shipping_address_id: int
    billing_address_id: Optional[int] = None
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    id: int
    user_id: int
    total_amount: Optional[float]
    status: str
    created_at: Optional[datetime]
    model_config = {
        "from_attributes": True
    }


class CartCheckout(BaseModel):
    shipping_address_id: int
    billing_address_id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }


class BuyNowPayload(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    shipping_address_id: int
    billing_address_id: Optional[int] = None


# --- Payment & Review & Shipping ---
class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float


class ReviewCreate(BaseModel):
    product_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewOut(ReviewCreate):
    review_id: int
    name: str
    model_config = {
        "from_attributes": True
    }


class CategoryBase(BaseModel):
    category_name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    category_id: int

    model_config = {
        "from_attributes": True
    }


class ProductBase(BaseModel):
    description: str
    price: float
    stock: Optional[int] = 0
    category_id: int


class ProductUpdate(ProductBase):
    product_name: Optional[str] = None
    discount_price: Optional[float] = None
    brand: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    name: str
    discount_price: float

    model_config = {
        "from_attributes": True
    }
