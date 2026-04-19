from typing import Optional

from sqlalchemy import String, Text, Numeric, DateTime, ForeignKey, PrimaryKeyConstraint, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")

    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username='{self.username}', email='{self.email}')"
    
class Restaurant(Base):
    __tablename__ = "restaurants"
    __table_args__ = (UniqueConstraint('restaurant_name', 'city', 'state','address', name='uix_restaurant_location'),)

    restaurant_id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_name: Mapped[str] = mapped_column(String(64), nullable=False)
    address: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="restaurant")

    def __repr__(self) -> str:
        return f"Restaurant(restaurant_id={self.restaurant_id}, restaurant_name='{self.restaurant_name}', address='{self.address}', city='{self.city}', state='{self.state}')"

class Review(Base):
    __tablename__ = "reviews"
    
    __table_args__ = (PrimaryKeyConstraint('user_id', 'restaurant_id'),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"), nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(2,1), CheckConstraint("rating >= 1 AND rating <= 5"), nullable=False)
    review_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    restaurant: Mapped["Restaurant"] = relationship("Restaurant", back_populates="reviews")

    def __repr__(self) -> str:
        return f"Review(user_id={self.user_id}, restaurant_id={self.restaurant_id}, rating={self.rating}, review_text='{self.review_text}')"

