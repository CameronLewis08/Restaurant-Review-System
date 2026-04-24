from pydantic import BaseModel
from datetime import datetime 

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    user_id: int
    username: str
    email: str
    created_at: datetime


class RestaurantCreate(BaseModel):
    restaurant_name: str
    address: str
    city: str
    state: str

class RestaurantResponse(BaseModel):
    model_config = {"from_attributes": True}
    restaurant_id: int
    restaurant_name: str
    address: str
    city: str
    state: str
    created_at: datetime

class ReviewCreate(BaseModel):
    user_id: int
    restaurant_id: int
    rating: float
    review_text: str | None = None

class ReviewUpdate(BaseModel):
    rating: float | None = None
    review_text: str | None = None

class ReviewResponse(BaseModel):
    model_config = {"from_attributes": True}
    user_id: int
    restaurant_id: int
    rating: float
    review_text: str | None = None
    created_at: datetime
    updated_at: datetime


