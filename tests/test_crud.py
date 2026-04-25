import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from restaurant_reviews.config import TEST_DATABASE_URL
from restaurant_reviews.db.models import User
from datetime import datetime, timezone
import bcrypt
from sqlalchemy.exc import IntegrityError
from restaurant_reviews.db import crud


engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def session():
    session = TestSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture(autouse=True)
def clean_db():
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE reviews, users, restaurants RESTART IDENTITY CASCADE"))
        conn.commit()
    yield
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE reviews, users, restaurants RESTART IDENTITY CASCADE"))
        conn.commit()
        
# USER Endpoints

def test_create_user():
    # arrange
    username = "testuser"
    email = "test@example.com"
    password = "password123"

    # act
    user = crud.create_user(username, email, password)

    # assert
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert bcrypt.checkpw(password.encode('utf-8'), user.password)

def test_create_user_duplicate():
    crud.create_user("testuser", "test@example.com", "password123")
    
    with pytest.raises(ValueError):
        crud.create_user("testuser", "test@example.com", "password123")

def test_get_user_by_username():
    # arrange
    username = "testuser"
    email = "test@example.com"
    password = "password123"
    crud.create_user(username, email, password)
    # act
    retrieved_user = crud.get_user_by_username(username)
    
    # assert
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "test@example.com"
    assert bcrypt.checkpw(password.encode('utf-8'), bytes.fromhex(retrieved_user.password[2:]))

def test_get_user_by_username_not_found():
    with pytest.raises(ValueError):
        crud.get_user_by_username("nonexistentuser")

def test_list_users():
    crud.create_user("user1", "user1@example.com", "password123")
    crud.create_user("user2", "user2@example.com", "password123")
    users = crud.list_users()
    assert len(users) >= 2
    assert any(u.username == "user1" for u in users)
    assert any(u.username == "user2" for u in users)
    assert all(isinstance(u, User) for u in users)

# RESTAURANT Endpoints

def test_create_restaurant():
    # arrange
    restaurant_name = "Test Restaurant"
    address = "123 Test St"
    city = "Testville"
    state = "TS"

    # act
    restaurant = crud.create_restaurant(restaurant_name, address, city, state)

    # assert
    assert restaurant.restaurant_name == restaurant_name
    assert restaurant.address == address
    assert restaurant.city == city
    assert restaurant.state == state

def test_create_restaurant_duplicate():
    restaurant_name = "Test Restaurant"
    address = "123 Test St"
    city = "Testville"
    state = "TS"
    crud.create_restaurant(restaurant_name, address, city, state)

    with pytest.raises(ValueError):
        crud.create_restaurant(restaurant_name, address, city, state)

def test_get_restaurant():
    restaurant_name = "Test Restaurant"
    address = "123 Test St"
    city = "Testville"
    state = "TS"
    restaurant = crud.create_restaurant(restaurant_name, address, city, state)

    retrieved_restaurant = crud.get_restaurant(restaurant.restaurant_id)

    assert retrieved_restaurant.restaurant_name == restaurant_name
    assert retrieved_restaurant.address == address
    assert retrieved_restaurant.city == city
    assert retrieved_restaurant.state == state

def test_get_restaurant_not_found():
    with pytest.raises(ValueError):
        crud.get_restaurant(9999)

def test_list_restaurants():
    crud.create_restaurant("Restaurant A", "123 A St", "CityA", "MD")
    crud.create_restaurant("Restaurant B", "456 B St", "CityB", "CA")
    restaurants = crud.list_restaurants()
    assert len(restaurants) >= 2
    assert any(r.restaurant_name == "Restaurant A" for r in restaurants)
    assert any(r.restaurant_name == "Restaurant B" for r in restaurants)

def test_list_restaurants_with_filters():
    crud.create_restaurant("Filtered Restaurant", "789 Filter St", "Filterville", "FV")
    restaurants = crud.list_restaurants(city="Filterville")
    assert len(restaurants) >= 1
    assert any(r.restaurant_name == "Filtered Restaurant" for r in restaurants)
    restaurants = crud.list_restaurants(state="FV")
    assert len(restaurants) >= 1
    assert any(r.restaurant_name == "Filtered Restaurant" for r in restaurants)

def test_list_restaurants_with_filters_no_match():
    crud.create_restaurant("Another Restaurant", "101 Another St", "Anotherville", "AV")
    restaurants = crud.list_restaurants(city="Nonexistent City")
    assert len(restaurants) == 0
    restaurants = crud.list_restaurants(state="Nonexistent State")
    assert len(restaurants) == 0

def test_get_reviews_by_restaurant():
    restaurant = crud.create_restaurant("Review Test Restaurant", "123 Review St", "Reviewville", "RV")
    user = crud.create_user("reviewtestuser", "reviewtestuser@example.com", "password123")
    crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    reviews = crud.get_reviews_by_restaurant(restaurant.restaurant_id)  
    assert len(reviews) == 1
    assert reviews[0].rating == 4.0
    assert reviews[0].review_text == "Good food!"

def test_get_restaurant_by_name():
    restaurant_name = "Unique Restaurant Name"
    address = "123 Unique St"
    city = "Uniqueville"
    state = "UV"
    crud.create_restaurant(restaurant_name, address, city, state)

    restaurant = crud.get_restaurant_by_name(restaurant_name)
    assert restaurant.restaurant_name == restaurant_name
    assert restaurant.address == address
    assert restaurant.city == city
    assert restaurant.state == state

def test_get_restaurant_by_name_not_found():
    with pytest.raises(ValueError):
        crud.get_restaurant_by_name("Nonexistent Restaurant Name")

# REVIEW Endpoints

def test_create_review():
    user = crud.create_user("reviewuser", "reviewuser@example.com", "password123")
    restaurant = crud.create_restaurant("Review Restaurant", "123 Review St", "Reviewville", "RV")
    review = crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    assert review.user_id == user.user_id           
    assert review.restaurant_id == restaurant.restaurant_id
    assert review.rating == 4.0
    assert review.review_text == "Good food!"

def test_create_review_duplicate():
    user = crud.create_user("reviewuser2", "reviewuser2@example.com", "password123")
    restaurant = crud.create_restaurant("Review Restaurant", "123 Review St", "Reviewville", "RV")
    crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    with pytest.raises(ValueError):
        crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")

def test_create_review_invalid_rating():
    user = crud.create_user("reviewuser2", "reviewuser2@example.com", "password123")
    restaurant = crud.create_restaurant("Review Restaurant", "123 Review St", "Reviewville", "RV")
    with pytest.raises(ValueError):
        crud.create_review(user.user_id, restaurant.restaurant_id, 6.0, "Good food!")
        
def test_create_review_invalid_user():
    restaurant = crud.create_restaurant("Review Restaurant", "123 Review St", "Reviewville", "RV")
    with pytest.raises(ValueError):
        crud.create_review(9999, restaurant.restaurant_id, 4.0, "Good food!")

def test_create_review_invalid_restaurant():
    user = crud.create_user("reviewuser2", "reviewuser2@example.com", "password123")
    with pytest.raises(ValueError):
        crud.create_review(user.user_id, 9999, 4.0, "Good food!")
    
def test_get_review_history():
    user = crud.create_user("historyuser2", "historyuser2@example.com", "password123")
    restaurant = crud.create_restaurant("History Restaurant", "123 History St", "Historyville", "HS")
    crud.create_review(user.user_id, restaurant.restaurant_id, 4.5, "Great food!")
    history = crud.get_review_history(user.user_id)
    assert len(history) == 1
    assert history[0][2] == "History Restaurant"  # restaurant_name is 3rd column
    assert history[0][0] == 4.5                   # rating is 1st column
    assert history[0][1] == "Great food!"         # review_text is 2nd column

def test_get_review_history_no_reviews():
    user = crud.create_user("noreviewsuser2", "noreviewsuser2@example.com", "password123")
    history = crud.get_review_history(user.user_id)
    assert history == []

def test_get_average_rating():
    restaurant = crud.create_restaurant("Rating Restaurant", "123 Rating St", "Ratingville", "RV")
    user1 = crud.create_user("ratinguser1", "ratinguser1@example.com", "password123")
    user2 = crud.create_user("ratinguser2", "ratinguser2@example.com", "password123")
    crud.create_review(user1.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    crud.create_review(user2.user_id, restaurant.restaurant_id, 5.0, "Excellent food!")
    average_rating = crud.get_average_rating(restaurant.restaurant_id)
    assert average_rating == 4.5    

def test_get_average_rating_no_reviews():
    restaurant = crud.create_restaurant("No Rating Restaurant", "123 No Rating St", "No Ratingville", "NR")
    average_rating = crud.get_average_rating(restaurant.restaurant_id)
    assert average_rating == 0.0

def test_list_average_ratings():
    restaurant1 = crud.create_restaurant("Average Rating Restaurant 1", "123 AR St", "ARville", "AR")
    restaurant2 = crud.create_restaurant("Average Rating Restaurant 2", "456 AR St", "ARville", "AR")
    user1 = crud.create_user("avgratinguser1", "avgratinguser1@example.com", "password123")
    user2 = crud.create_user("avgratinguser2", "avgratinguser2@example.com", "password123")
    crud.create_review(user1.user_id, restaurant1.restaurant_id, 4.0, "Good food!")
    crud.create_review(user2.user_id, restaurant2.restaurant_id, 5.0, "Excellent food!")
    average_ratings = crud.list_average_ratings()
    names = [r[0] for r in average_ratings]
    assert "Average Rating Restaurant 1" in names
    assert "Average Rating Restaurant 2" in names

def test_update_review():
    user = crud.create_user("updatereviewuser", "updatereviewuser@example.com", "password123")
    restaurant = crud.create_restaurant("Update Review Restaurant", "123 Update St", "Updateville", "UV")
    review = crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    crud.update_review(user.user_id, restaurant.restaurant_id, 5.0, "Excellent food!")
    updated = crud.get_review(user.user_id, restaurant.restaurant_id)
    assert updated.rating == 5.0
    assert updated.review_text == "Excellent food!"

def test_update_review_not_found():
    with pytest.raises(ValueError):
        crud.update_review(9999, 9999, 5.0, "Excellent food!")

def test_delete_review():
    user = crud.create_user("deletereviewuser", "deletereviewuser@example.com", "password123")
    restaurant = crud.create_restaurant("Delete Review Restaurant", "123 Delete St", "Deleteville", "DV")
    review = crud.create_review(user.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    crud.delete_review(user.user_id, restaurant.restaurant_id)
    with pytest.raises(ValueError):
        crud.get_review(user.user_id, restaurant.restaurant_id)

def test_delete_review_not_found():
    with pytest.raises(ValueError):
        crud.delete_review(9999, 9999)
        
def test_list_reviews():
    restaurant = crud.create_restaurant("List Reviews Restaurant", "123 List St", "Listville", "LV")
    user1 = crud.create_user("listreviewsuser1", "listreviewsuser1@example.com", "password123")
    user2 = crud.create_user("listreviewsuser2", "listreviewsuser2@example.com", "password123")
    crud.create_review(user1.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    crud.create_review(user2.user_id, restaurant.restaurant_id, 5.0, "Excellent food!")
    reviews = crud.list_reviews(10, 0)
    assert len(reviews) == 2
    ratings = [r.rating for r in reviews]
    assert 4.0 in ratings
    assert 5.0 in ratings

def test_list_reviews_pagination():
    restaurant = crud.create_restaurant("Paginated Reviews Restaurant", "123 Paginate St", "Paginateville", "PV")
    user1 = crud.create_user("paginatedreviewsuser1", "paginatedreviewsuser1@example.com", "password123")
    user2 = crud.create_user("paginatedreviewsuser2", "paginatedreviewsuser2@example.com", "password123")
    crud.create_review(user1.user_id, restaurant.restaurant_id, 4.0, "Good food!")
    crud.create_review(user2.user_id, restaurant.restaurant_id, 5.0, "Excellent food!")
    reviews = crud.list_reviews(1, 0)
    assert len(reviews) == 1
    reviews = crud.list_reviews(1, 1)
    assert len(reviews) == 1

def test_list_reviews_no_reviews():
    reviews = crud.list_reviews(10, 0)
    assert reviews == []

