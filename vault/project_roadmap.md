# Project Roadmap
## Restaurant Review System

Use this file to track your progress through the project. Check off each task as you complete it. Each phase ends with a milestone — a concrete deliverable that confirms the phase is done before moving on.

> **Reference:** See `vault/engineering_best_practices.md` for deeper guidance on any topic.

---

## Phase 1 — Environment Setup

*Goal: A clean, reproducible local environment with the project scaffolded and version-controlled.*

### 1.1 Python Environment
- [ ] Install Python 3.11+ if not already installed
- [ ] Create a virtual environment inside the project root (`python -m venv .venv`) — keeps dependencies isolated from your global Python
- [ ] Activate the virtual environment and confirm you're using the project-local Python

### 1.2 Dependencies
- [ ] Create a `requirements.txt` listing your core dependencies: `psycopg2-binary`, `sqlalchemy`, `python-dotenv` — pin exact versions
- [ ] Install dependencies with `pip install -r requirements.txt` and verify no errors

### 1.3 PostgreSQL
- [ ] Install PostgreSQL locally if not already installed
- [ ] Create a dedicated database for this project (e.g., `restaurant_reviews`) — don't use the default `postgres` database for application data
- [ ] Create a dedicated database user with limited permissions — avoid using the superuser `postgres` account in your app

### 1.4 Project Structure
- [ ] Create the recommended folder skeleton: `src/restaurant_reviews/db/`, `tests/`, `vault/` — refer to the repo structure section of the best practices doc
- [ ] Add `__init__.py` files to make Python packages importable
- [ ] Create placeholder files: `config.py`, `db/connection.py`, `db/models.py`, `db/crud.py`, `main.py`

### 1.5 Configuration & Secrets
- [ ] Create `.gitignore` — ensure `.env`, `.venv/`, and `__pycache__/` are listed *before* your first commit
- [ ] Create `.env` with your database credentials (`DATABASE_URL`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- [ ] Create `.env.example` with the same keys but dummy values — this gets committed so others know what's required
- [ ] Write `config.py` to load variables from `.env` using `python-dotenv` — use `os.environ["KEY"]` (not `.get()`) so the app fails fast on missing config

### 1.6 Version Control
- [ ] Confirm `.env` is untracked (`git status` should not show it)
- [ ] Make your initial commit with the project skeleton

---

**Phase 1 Milestone:** You can activate your virtual environment, connect to your PostgreSQL database manually via `psql`, and your `.env` is confirmed absent from git history.

---

## Phase 2 — Schema Design & DDL

*Goal: A normalized, constrained PostgreSQL schema that enforces data integrity at the database level.*

### 2.1 Design the Schema (on paper first)
- [ ] Sketch out the three tables and their columns before writing any SQL — identify what data each table owns
- [ ] Define the relationships: what is the primary key of each table? what foreign keys link them?
- [ ] Identify which columns must be `NOT NULL` — anything required to exist in every row
- [ ] Identify which combinations of columns must be unique — e.g., one review per user/restaurant pair requires a `UNIQUE(user_id, restaurant_id)` constraint on `reviews`
- [ ] Decide on `ON DELETE` behavior for each foreign key — what should happen to reviews if the referenced user or restaurant is deleted?
- [ ] Apply naming conventions throughout: plural `snake_case` table names (`users`, `restaurants`, `reviews`), singular `snake_case` columns (`user_id`, `created_at`), FK columns named `{referenced_table_singular}_id`, indexes named `idx_{table}_{column}` — see BP §1.3

### 2.2 Write the DDL
- [ ] Create a `schema.sql` file (or use SQLAlchemy models — your choice) to define all three tables
- [ ] `users` table: id, username, email, password_hash, created_at — use `SERIAL` for id, `VARCHAR(254)` for email, `TIMESTAMPTZ` for created_at
- [ ] `restaurants` table: id, name, address, city, cuisine_type, created_at — use `SERIAL` for id, `TEXT` for free-text fields, `TIMESTAMPTZ` for created_at
- [ ] `reviews` table: id, user_id (FK), restaurant_id (FK), rating, body, created_at, updated_at — use `SMALLINT` for rating, `TIMESTAMPTZ` for both timestamp columns; never use `TIMESTAMP` without timezone or `CHAR(n)` — see BP §1.5
- [ ] Add a `CHECK` constraint on `rating` to enforce valid values (e.g., 1–5)

### 2.3 Indexes
- [ ] Add indexes on `reviews.user_id` and `reviews.restaurant_id` — FK columns on the child side are not auto-indexed by PostgreSQL
- [ ] Add an index on `users.email` — this column will be used frequently for login lookups

### 2.4 Validate the Schema
- [ ] Run the DDL against your local database and confirm all tables are created without errors
- [ ] Manually insert test rows via `psql` to verify constraints fire correctly — try inserting a duplicate review for the same user/restaurant and confirm it is rejected
- [ ] Try deleting a user that has reviews — confirm the `ON DELETE` behavior works as intended

---

**Phase 2 Milestone:** All three tables exist in your database with constraints and indexes in place. You can demonstrate that the unique review constraint and foreign key constraints reject invalid data.

---

## Phase 3 — Python / Database Connection

*Goal: A working, properly structured Python layer that connects to PostgreSQL and can execute queries reliably.*

### 3.1 Connection Module
- [ ] Write `db/connection.py` to create a SQLAlchemy `engine` using `DATABASE_URL` from `config.py` — do not hardcode the connection string here
- [ ] Configure a basic connection pool (`pool_size`, `max_overflow`) — understand what each setting controls
- [ ] Test the connection by running a simple `SELECT 1` query from Python and printing the result

### 3.2 SQLAlchemy Models (if using ORM)
- [ ] Write `db/models.py` with SQLAlchemy ORM classes mapping to `users`, `restaurants`, and `reviews`
- [ ] Declare all columns with correct types and constraints mirroring the schema — the ORM models and the actual schema should agree
- [ ] Define relationships between models (`relationship()`) so you can navigate from a review to its user and restaurant in Python

### 3.3 Session Management
- [ ] Write a session factory or context manager in `db/connection.py` that opens and closes a `Session` properly — ensure the session is always closed, even if an error occurs
- [ ] Confirm that your session pattern commits on success and rolls back on exception — test this by intentionally triggering a constraint violation

### 3.4 Error Handling
- [ ] Import and handle `sqlalchemy.exc.IntegrityError` in your connection/crud layer — this is the exception raised when a constraint is violated
- [ ] Ensure your error handling always calls `session.rollback()` before re-raising — a session left in a failed state will reject all subsequent queries

---

**Phase 3 Milestone:** A Python script (`main.py` or a test file) can open a session, execute a basic query, and close cleanly. Triggering a constraint violation raises a caught `IntegrityError` and rolls back without crashing the program.

---

## Phase 4 — CRUD Operations & Business Logic

*Goal: Working Python functions that implement every user-facing operation the system supports.*

### 4.1 User Registration
- [ ] Write `create_user(username, email, password)` in `db/crud.py` — inserts a new row into `users`
- [ ] Hash the password before storing it — never store plaintext passwords. Use `bcrypt` or `hashlib` with a salt
- [ ] Handle the `IntegrityError` that fires when a duplicate email is submitted — surface a meaningful message rather than a raw database error

### 4.2 Restaurant Management
- [ ] Write `create_restaurant(name, address, city, cuisine_type)` — inserts a new restaurant
- [ ] Write `get_restaurant(restaurant_id)` — retrieves a single restaurant by ID; select only the columns you need, never `SELECT *` — see BP §3.2
- [ ] Write `list_restaurants(city=None, cuisine=None)` — retrieves restaurants with optional filters; use parameterized query placeholders for all filter values, never f-strings or concatenation — see BP §3.1

### 4.3 Review Operations
- [ ] Write `create_review(user_id, restaurant_id, rating, body)` — inserts a review and handles the unique constraint violation when the user has already reviewed that restaurant; use parameterized values — see BP §3.1
- [ ] Write `get_reviews_for_restaurant(restaurant_id)` — retrieves all reviews for a restaurant, ordered by `created_at DESC`; name each column explicitly in the SELECT — see BP §3.2
- [ ] Write `update_review(review_id, user_id, rating, body)` — updates an existing review; include `user_id` in the `WHERE` clause to ensure a user can only edit their own reviews
- [ ] Write `delete_review(review_id, user_id)` — deletes a review with the same ownership check
- [ ] Format all raw SQL you write with uppercase keywords, one clause per line, and meaningful table aliases — see BP §3.5

### 4.4 Read Operations & Aggregates
- [ ] Write a query to calculate the average rating for a restaurant — use `COALESCE(AVG(rating), 0)` to handle restaurants with no reviews yet
- [ ] Write a query to retrieve a user's full review history — join `reviews` with `restaurants` to return restaurant names alongside ratings

### 4.5 Wire Everything Together
- [ ] Update `main.py` to demonstrate each operation end-to-end — registration, adding a restaurant, submitting a review, updating it, and reading the results back
- [ ] Test the one-review-per-user rule: attempt to submit a second review from the same user for the same restaurant and confirm it is rejected with a clear message
- [ ] Test that `update_review` with a mismatched `user_id` updates zero rows — confirm your ownership check works

---

**Phase 4 Milestone:** Every CRUD function works end-to-end. The business rule (one review per user/restaurant) is enforced at the database level and handled gracefully at the application level. Running `main.py` produces readable, correct output for all operations.

---

## Overall Progress

| Phase | Status |
|---|---|
| Phase 1 — Environment Setup | Not started |
| Phase 2 — Schema Design & DDL | Not started |
| Phase 3 — Python / DB Connection | Not started |
| Phase 4 — CRUD Operations & Business Logic | Not started |

Update the status column as you move through phases: `Not started` → `In progress` → `Complete`.
