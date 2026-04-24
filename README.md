# Restaurant Review System

## Project Description

A fully functional backend REST API for a restaurant review platform. Users can register accounts, browse restaurants, and submit one review per restaurant. The system enforces data integrity through database-level constraints and exposes a documented REST API built with FastAPI.

Built as a portfolio project to demonstrate real-world backend and database engineering skills including schema design, ORM usage, REST API design, and test-driven development.

## Tech Stack

| Layer | Technology |
|---|---|
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| API Framework | FastAPI |
| Server | Uvicorn |
| Password Hashing | bcrypt |
| Testing | pytest |
| Config Management | python-dotenv |

## Project Structure

```
src/restaurant_reviews/
├── db/
│   ├── connection.py     # SQLAlchemy engine and session context manager
│   ├── models.py         # ORM models for User, Restaurant, Review
│   ├── crud.py           # All database operations
│   ├── schema.sql        # PostgreSQL DDL (tables, indexes, trigger)
│   ├── setup.sql         # Grant statements for the main database user
│   └── setup_test.sql    # Grant statements for the test database user (includes table ownership for TRUNCATE)
├── schemas.py            # Pydantic request/response models
├── app.py                # FastAPI routes and endpoints
├── config.py             # Environment variable management
├── main.py               # Seed data runner
└── seed_data.json        # Sample data for local development
tests/
└── test_crud.py          # pytest test suite
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL

### Installation

1. Clone the repository
2. Create and activate a virtual environment:
```
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Copy `.env.example` to `.env` and fill in your database credentials:
```
cp .env.example .env
```
5. Create the database, run the schema, and grant permissions:
```sql
CREATE DATABASE restaurant_reviews;
```
Then run `schema.sql` against the database, followed by `user_setup.sql` to grant the required permissions to your database user.

6. (Optional) For running tests, create a test database:
```sql
CREATE DATABASE restaurant_reviews_test_db;
```
Then run `schema.sql` against the test database, followed by `testuser_setup.sql` to grant the additional permissions required for test cleanup.

7. Start the API server:
```
uvicorn restaurant_reviews.app:app --reload
```

## API Documentation

Interactive API docs are available at `http://127.0.0.1:8000/docs` when the server is running.

Full OpenAPI specification is available in `openapi.json` and published on SwaggerHub.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/users` | Register a new user |
| GET | `/users/{username}` | Get a user by username |
| GET | `/users/history/{user_id}` | Get a user's review history |
| POST | `/restaurants` | Add a new restaurant |
| GET | `/restaurants` | List restaurants (supports city/state filters + pagination) |
| GET | `/restaurants/{id}` | Get a restaurant by ID |
| POST | `/reviews` | Submit a review |
| GET | `/reviews/{restaurant_id}` | Get reviews for a restaurant (paginated) |
| GET | `/reviews/{restaurant_id}/average` | Get average rating for a restaurant |
| PATCH | `/reviews/{user_id}/{restaurant_id}` | Update a review |
| DELETE | `/reviews/{user_id}/{restaurant_id}` | Delete a review |

## Running Tests

Create a test database and add `TEST_DATABASE_URL` to your `.env`, then:

```
$env:TESTING="true"; pytest  # Windows
TESTING=true pytest          # Mac/Linux
```

## Key Design Decisions

- **Composite primary key on reviews** — `(user_id, restaurant_id)` enforces one review per user per restaurant at the database level
- **Constraints at the database level** — foreign keys, CHECK constraints, and unique constraints prevent invalid data regardless of how the database is accessed
- **bcrypt password hashing** — passwords are never stored in plaintext
- **Session context manager** — all database sessions commit on success and rollback on failure automatically
- **Pagination** — list endpoints support `limit` and `offset` query parameters
