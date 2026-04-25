from typing import Optional

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone


from restaurant_reviews.db.connection import get_session
from restaurant_reviews.db.models import User, Review, Restaurant

# User CRUD Operations

def create_user(username: str, email: str, password: str) -> User:
    try:
        with get_session() as session:
            user = User(
                username=username,
                email=email,
                password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()),
                created_at=datetime.now(timezone.utc)
            )
            session.add(user)
            session.flush()  # Ensure the user is assigned an ID before returning
            return user

    except IntegrityError:
        raise ValueError("User with that username or email address already exists")

def get_user_by_username(username: str) -> User:
    with get_session() as session:
        user = session.execute(select(User).where(User.username == username)).scalars().first()
        if user is None:
            raise ValueError("User not found")
        return user
    
def list_users(limit: int = 10, offset: int = 0) -> list[User]:
    with get_session() as session:
        return session.execute(select(User).limit(limit).offset(offset)).scalars().all()

# Restaurant CRUD Operation

def create_restaurant(restaurant_name: str, address: str, city: str, state: str) -> Restaurant:
    try:
        with get_session() as session:
            restaurant = Restaurant(
                restaurant_name=restaurant_name,
                address=address,
                city=city,
                state=state,
                created_at=datetime.now(timezone.utc)
            )
            session.add(restaurant)
            session.flush()  # Ensure the restaurant is assigned an ID before returning
            return restaurant
    except IntegrityError:
        raise ValueError("Restaurant with that name, location, and address already exists")

def get_restaurant(restaurant_id: int) -> Restaurant:
    with get_session() as session:
        restaurant = session.execute(select(Restaurant).where(Restaurant.restaurant_id == restaurant_id)).scalars().first()
        if restaurant is None:
            raise ValueError("Restaurant not found")
        else:
            return restaurant
        
def list_restaurants(city: Optional[str] = None, state: Optional[str] = None, limit: int = 10, offset: int = 0) -> list[Restaurant]:
    with get_session() as session:
        query = select(Restaurant)
        if city is not None:
            query = query.where(Restaurant.city == city)
        if state is not None:
            query = query.where(Restaurant.state == state)
        query = query.limit(limit).offset(offset)
        return session.execute(query).scalars().all()

def get_average_rating(restaurant_id: int) -> float:
    with get_session() as session:
        avg_rating = session.execute(select(func.round(func.coalesce(func.avg(Review.rating), 0), 1)).where(Review.restaurant_id == restaurant_id)).scalar()
        return avg_rating 
    
def get_restaurant_by_name(restaurant_name: str) -> Restaurant:
    with get_session() as session:
        restaurant = session.execute(select(Restaurant).where(Restaurant.restaurant_name == restaurant_name)).scalars().first()
        if restaurant is None:
            raise ValueError("Restaurant not found")
        return restaurant
    
def list_average_ratings() -> list[tuple]:
    with get_session() as session:
        results = session.execute(
            select(
                Restaurant.restaurant_name,
                func.round(func.coalesce(func.avg(Review.rating), 0), 1)
            )
            .join(Review, Restaurant.restaurant_id == Review.restaurant_id, isouter=True)
            .group_by(Restaurant.restaurant_id)
        ).all()
        return results

# Review CRUD Operations

def create_review(user_id: int, restaurant_id: int, rating: float, review_text: Optional[str] = None) -> Review:
    try:
        with get_session() as session:
            # insert review
            review = Review(
                user_id=user_id,
                restaurant_id=restaurant_id,
                rating=round(rating, 1),
                review_text=review_text,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            session.add(review)
            session.flush()
            return review
    except IntegrityError:
        raise ValueError("You have already reviewed this restaurant")
    
def get_reviews_by_restaurant(restaurant_id: int, limit: int = 10, offset: int = 0) -> list[Review]:
    with get_session() as session:
        review_list = session.execute(select(Review).where(Review.restaurant_id == restaurant_id).order_by(Review.created_at.desc()).limit(limit).offset(offset)).scalars().all()
        return review_list
    
def get_review(user_id: int, restaurant_id: int) -> Review:
    with get_session() as session:
        review = session.execute(select(Review).where(Review.user_id == user_id, Review.restaurant_id == restaurant_id)).scalars().first()
        if review is None:
            raise ValueError("Review not found")
        return review
    
def update_review(user_id: int, restaurant_id: int, rating: Optional[float] = None, review_text: Optional[str] = None) -> None:
    with get_session() as session:
        review = session.execute(select(Review).where(Review.user_id == user_id, Review.restaurant_id == restaurant_id)).scalars().first()
        if review is None:
            raise ValueError("Review not found")
        if rating is not None:
            review.rating = rating
        if review_text is not None:
            review.review_text = review_text
        review.updated_at = datetime.now(timezone.utc)

def delete_review(user_id: int, restaurant_id: int) -> None:
    with get_session() as session:
        review = session.execute(select(Review).where(Review.user_id == user_id, Review.restaurant_id == restaurant_id)).scalars().first()
        if review is None:
            raise ValueError("Review not found")
        session.delete(review)

def get_review_history(user_id: int, limit: int = 10, offset: int = 0) -> list[tuple]:
    with get_session() as session:
        review_history = session.execute(select(Review.rating, Review.review_text, Restaurant.restaurant_name, Review.created_at).join(Restaurant).where(Review.user_id == user_id).order_by(Review.created_at.desc()).limit(limit).offset(offset)).all()
        return review_history
    
def list_reviews(limit: int = 10, offset: int = 0) -> list[Review]:
    with get_session() as session:
        return session.execute(select(Review).limit(limit).offset(offset)).scalars().all()
