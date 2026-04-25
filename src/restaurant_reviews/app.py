from fastapi import FastAPI, HTTPException
from restaurant_reviews.db import crud
from restaurant_reviews.db.models import Review
from restaurant_reviews.schemas import RestaurantResponse, ReviewResponse, ReviewUpdate, UserCreate, RestaurantCreate, ReviewCreate, UserResponse

app = FastAPI(
    title="Restaurant Review System",
    description="A REST API for managing restaurant reviews",
    version="1.0.0",
    servers=[{"url": "http://127.0.0.1:8000"}]
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Restaurant Review System API!"}

# User Endpoints

@app.post("/users")
def create_user(user: UserCreate):
    try:
        crud.create_user(user.username, user.email, user.password)
        return {"message": "User created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str):
    try:
        user = crud.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.get("/users/history/{user_id}")
def get_user_history(user_id: int, limit: int = 10, offset: int = 0):
    try:
        reviews = crud.get_review_history(user_id, limit, offset)
        return [
            {
                "restaurant_name": r.restaurant_name,
                "rating": float(r.rating),
                "review_text": r.review_text,
                "created_at": str(r.created_at)
            }
            for r in reviews
        ]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Restaurant Endpoints

@app.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate):
    try:
        crud.create_restaurant(
            restaurant.restaurant_name,
            restaurant.address,
            restaurant.city,
            restaurant.state
        )
        return {"message": "Restaurant created successfully"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/restaurants/search")
def search_restaurants(name: str):
    try:
        restaurant = crud.get_restaurant_by_name(name)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int):
    try:
        restaurant = crud.get_restaurant(restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/restaurants")
def list_restaurants(city: str | None = None, state: str | None = None, limit: int = 10, offset: int = 0):
    return crud.list_restaurants(city, state, limit, offset)
    

# Review Endpoint

@app.post("/reviews")
def create_review(review: ReviewCreate):   
    try:
        crud.create_review(
            user_id =review.user_id,
            restaurant_id=review.restaurant_id,
            rating=review.rating,
            review_text=review.review_text
        )
        return {"message": "Review created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/reviews/list", response_model=list[ReviewResponse])
def list_reviews(limit: int = 10, offset: int = 0):
    try:
        reviews = crud.list_reviews(limit, offset)
        return reviews
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/reviews/{restaurant_id}", response_model=list[ReviewResponse])
def get_reviews(restaurant_id: int, limit: int = 10, offset: int = 0):
    try:
        restaurant = crud.get_restaurant(restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        reviews = crud.get_reviews_by_restaurant(restaurant_id, limit, offset)
        return reviews
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/reviews/{restaurant_id}/average")
def get_average_rating(restaurant_id: int):
    try:
        restaurant = crud.get_restaurant(restaurant_id)
        if restaurant is None:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        average_rating = crud.get_average_rating(restaurant_id)
        return {"average_rating": float(average_rating)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@app.patch("/reviews/{user_id}/{restaurant_id}")
def update_review(user_id: int, restaurant_id: int, review: ReviewUpdate):
    try:
        crud.update_review(user_id, restaurant_id, review.rating, review.review_text)
        return {"message": "Review updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/reviews/{user_id}/{restaurant_id}")
def delete_review(user_id: int, restaurant_id: int):
    try:
        crud.delete_review(user_id, restaurant_id)
        return {"message": "Review deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
