from sqlalchemy import Integer, String, Text, Numeric, DateTime, ForeignKey, PrimaryKeyConstraint, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class Restaurant(Base):
    __tablename__ = "restaurants"
    
    restaurant_id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_name: Mapped[str] = mapped_column(String(64), nullable=False)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
class Review(Base):
    __tablename__ = "reviews"
    
    __table_args__ = (PrimaryKeyConstraint('user_id', 'restaurant_id'),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"), nullable=False)
    rating: Mapped[float] = mapped_column(Numeric(2,1), CheckConstraint("rating >= 1 AND rating <= 5"), nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
