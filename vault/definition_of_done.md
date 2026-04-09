# Definition of Done
## Restaurant Review System

A roadmap task is not complete when the code runs — it is complete when it meets every criterion in this file. Before checking off any task in `project_roadmap.md`, work through the relevant section here and confirm every box applies.

> **References:** `vault/engineering_best_practices.md` · `vault/project_roadmap.md`

---

## How to Use This File

1. Complete a roadmap task
2. Open the matching section below
3. Work through each criterion — correctness, best practice compliance, common mistake checks, and the self-review question
4. Only check off the roadmap task when every criterion is met

If any criterion exposes a problem, fix it before marking the task done.

---

## Phase 1 — Environment Setup

### 1.1 Python Environment
- [ ] Running `python --version` inside the activated virtual environment shows the project-local Python, not the system Python
- [ ] The `.venv/` directory exists inside the project root and is not committed to git
- [ ] No packages are installed globally for this project — all dependencies live inside `.venv/`

**Common mistake check:** Skipping virtual environment creation and installing packages globally. If `which python` (or `where python` on Windows) points outside the project directory, the environment is not activated.

**Self-review:** Could you explain to someone why virtual environments exist and what problem they solve?

---

### 1.2 Dependencies
- [ ] `requirements.txt` exists and lists exact pinned versions for all three core packages (`psycopg2-binary`, `sqlalchemy`, `python-dotenv`)
- [ ] Running `pip install -r requirements.txt` from a fresh virtual environment completes without errors
- [ ] No unnecessary packages are listed — only what the project actually needs

**Common mistake check:** Using unpinned versions (e.g., `sqlalchemy` with no version number). This makes the environment non-reproducible — a future install could pull a breaking version.

**Self-review:** If someone cloned your repo tomorrow and ran `pip install -r requirements.txt`, would they get an identical environment to yours?

---

### 1.3 PostgreSQL
- [ ] A dedicated database exists for this project (not the default `postgres` database)
- [ ] A dedicated database user exists with limited permissions — not the superuser `postgres` account
- [ ] You can connect to the database manually via `psql` using that user's credentials

**Common mistake check:** Using the `postgres` superuser in the application. Application users should only have the permissions they need (`CONNECT`, `SELECT`, `INSERT`, `UPDATE`, `DELETE` on the relevant tables).

**Self-review:** Why is it a problem to use the superuser account for application connections?

---

### 1.4 Project Structure
- [ ] The folder structure matches the layout defined in BP §4.1: `src/restaurant_reviews/db/`, `tests/`, `vault/`
- [ ] All Python package directories contain an `__init__.py` file
- [ ] Placeholder files exist for `config.py`, `db/connection.py`, `db/models.py`, `db/crud.py`, `main.py`
- [ ] No application logic is written directly in `main.py` yet — it is a placeholder only at this stage

**Common mistake check:** Placing all `.py` files in the root directory. This conflates package code with configuration files, makes imports fragile, and does not match the `src` layout recommended in BP §4.1.

**Self-review:** What is the purpose of separating `connection.py`, `models.py`, and `crud.py` into distinct files rather than putting everything in one file?

---

### 1.5 Configuration & Secrets
- [ ] `.env` exists locally and contains all required keys (`DATABASE_URL`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`)
- [ ] `.env` does **not** appear in `git status` — it is tracked by `.gitignore`
- [ ] `.env.example` exists with the same keys and dummy values — it **is** committed
- [ ] `config.py` loads variables using `os.environ["KEY"]` (bracket syntax), not `os.environ.get("KEY")` — so a missing variable raises a `KeyError` immediately on startup rather than silently returning `None`
- [ ] No other file in the project calls `os.environ` directly — all config is imported from `config.py`

**Common mistake check:** Using `.get()` for required variables. `os.environ.get("DATABASE_URL")` returns `None` silently if the variable is missing, which produces a confusing error later (e.g., when trying to use `None` as a connection string) rather than a clear failure at startup.

**Self-review:** What would happen if you hard-coded the database password in `config.py` and accidentally pushed to a public GitHub repo? What would you need to do to recover?

---

### 1.6 Version Control
- [ ] `git status` shows `.env` as untracked or ignored — never staged or committed
- [ ] The initial commit contains only the project skeleton: folder structure, placeholder files, `.gitignore`, `.env.example`, `requirements.txt`, `README.md`
- [ ] No credentials, no `.venv/`, and no `__pycache__/` appear in the commit

**Common mistake check:** Adding `.gitignore` after the first commit. If `.env` was committed even once, it exists in git history and must be treated as compromised regardless of whether it was later deleted.

**Self-review:** How would you verify that `.env` has never appeared in your git history, not just in the current working tree?

---

**Phase 1 Complete When:** You can run `git log`, see the initial skeleton commit, activate your virtual environment, and connect to your PostgreSQL database with your dedicated user — with zero credentials visible in the git history.

---

## Phase 2 — Schema Design & DDL

### 2.1 Schema Design
- [ ] Each table owns only the data that belongs to it — no column in `reviews` stores data that already lives in `users` or `restaurants` (e.g., no `restaurant_name` column in `reviews`)
- [ ] Every table has a primary key using `SERIAL` or `BIGSERIAL` — not a manually managed integer
- [ ] Every foreign key column is named `{referenced_table_singular}_id` (e.g., `user_id`, `restaurant_id`)
- [ ] All table names are plural and `snake_case`; all column names are singular and `snake_case`
- [ ] `ON DELETE` behavior is explicitly declared on every foreign key — not left as the implicit default
- [ ] You have written down (on paper or in a comment) the reason for your `ON DELETE` choice on each FK

**Common mistake check:** Leaving `ON DELETE` behavior undeclared. PostgreSQL defaults to `RESTRICT`, which is safe, but not declaring it means your intent is undocumented. A future change to the schema could alter behavior unexpectedly.

**Self-review:** Could you explain the three `ON DELETE` options (`RESTRICT`, `CASCADE`, `SET NULL`) and justify which you chose for each foreign key in this schema?

---

### 2.2 DDL — Tables and Constraints
- [ ] Primary key columns use `SERIAL` (not bare `INT`)
- [ ] Email column uses `VARCHAR(254)` — not unconstrained `TEXT`
- [ ] Rating column uses `SMALLINT` — not `FLOAT` or `INT`
- [ ] All timestamp columns use `TIMESTAMPTZ` — never `TIMESTAMP` without timezone
- [ ] No column uses `CHAR(n)` — use `TEXT` or `VARCHAR(n)` instead
- [ ] A `CHECK` constraint enforces the valid rating range (e.g., `CHECK (rating BETWEEN 1 AND 5)`)
- [ ] A composite `UNIQUE(user_id, restaurant_id)` constraint exists on `reviews` — the one-review-per-user rule is enforced at the database level, not just in Python
- [ ] All required columns have `NOT NULL` — no column that must always have a value is left nullable

**Common mistake check:** Using `TIMESTAMP` instead of `TIMESTAMPTZ`. A `TIMESTAMP` column stores no timezone information — if your application ever runs in a different timezone or processes data from users in multiple timezones, the stored values become ambiguous. This is listed explicitly in the PostgreSQL "Don't Do This" wiki (BP §1.5).

**Self-review:** Why does storing ratings as `SMALLINT` instead of `FLOAT` matter, even if the values are always whole numbers?

---

### 2.3 Indexes
- [ ] Indexes exist on `reviews.user_id` and `reviews.restaurant_id` — these FK columns are not auto-indexed by PostgreSQL
- [ ] An index exists on `users.email` — this column will be used in login lookups
- [ ] Index names follow the `idx_{table}_{column}` convention
- [ ] You have not added indexes speculatively on columns that have no query patterns yet

**Common mistake check:** Assuming PostgreSQL indexes foreign key columns automatically. It does not. Without indexes on `reviews.user_id` and `reviews.restaurant_id`, every join between these tables requires a full sequential scan of `reviews`.

**Self-review:** What is the trade-off of adding an index? Why not just index every column?

---

### 2.4 Schema Validation
- [ ] The DDL runs against your local database without errors
- [ ] You have confirmed the unique constraint rejects a duplicate `(user_id, restaurant_id)` pair by testing it manually in `psql`
- [ ] You have confirmed the `CHECK` constraint on `rating` rejects a value outside the valid range
- [ ] You have confirmed the `ON DELETE` behavior works as intended by manually testing a delete in `psql`
- [ ] All three tables appear in `\dt` output with the correct column structure (`\d users`, `\d restaurants`, `\d reviews`)

**Common mistake check:** Skipping manual validation and trusting the DDL is correct because it ran without errors. A schema can be syntactically valid but logically wrong — constraints can be declared but not actually fire in edge cases you haven't tested.

**Self-review:** Why is it important to validate constraints by testing violation cases, not just the happy path?

---

**Phase 2 Complete When:** All three tables exist with correct types, constraints, and indexes. You can demonstrate — not just assert — that the unique review constraint, CHECK constraint, and FK behavior all reject invalid data in `psql`.

---

## Phase 3 — Python / Database Connection

### 3.1 Connection Module
- [ ] `db/connection.py` reads `DATABASE_URL` from `config.py` — the connection string is not hardcoded anywhere
- [ ] The SQLAlchemy engine is created with explicit `pool_size` and `max_overflow` values — not left as defaults you haven't thought about
- [ ] A `SELECT 1` test query runs successfully from Python and prints a result
- [ ] The engine is created once at module level and reused — not re-created on every function call

**Common mistake check:** Calling `create_engine()` inside a function that runs per-request. This creates a new connection pool on every call, defeating the purpose of pooling and leaking resources.

**Self-review:** What is a connection pool and why does it matter even in a local development project?

---

### 3.2 SQLAlchemy Models
- [ ] ORM model classes exist for `User`, `Restaurant`, and `Review` in `db/models.py`
- [ ] Every column in the ORM models matches the corresponding column in the actual database schema — type, nullability, and constraints agree
- [ ] `relationship()` definitions allow navigating from a `Review` to its `User` and `Restaurant` in Python without writing a manual join
- [ ] Model class names are singular `PascalCase` (`User`, not `Users`) — this is the Python ORM convention, distinct from the plural `snake_case` table names

**Common mistake check:** Declaring a column as `nullable=True` in the ORM model while the database column has `NOT NULL`. The ORM and the schema can drift apart silently — the database constraint still protects you, but the ORM gives misleading signals about what values are valid.

**Self-review:** If you change a column name in the database schema, what else needs to change to keep the ORM models consistent?

---

### 3.3 Session Management
- [ ] Sessions are opened and closed using a context manager (`with Session(engine) as session:`) — never left open manually
- [ ] A failed operation triggers a rollback — the session is never left in a failed transaction state
- [ ] You have verified rollback behavior by intentionally triggering a constraint violation and confirming the session recovers cleanly

**Common mistake check:** Calling `session.commit()` and then continuing to use the session without checking for errors. If the commit raises an exception (e.g., a constraint violation), the session is in a failed state and every subsequent operation on it will fail with `InFailedSqlTransaction` until you call `rollback()`.

**Self-review:** What is the difference between a connection and a session in SQLAlchemy? Why does this distinction matter?

---

### 3.4 Error Handling
- [ ] `sqlalchemy.exc.IntegrityError` is caught specifically — not bare `Exception`
- [ ] Every `except` block calls `session.rollback()` before re-raising or converting the error
- [ ] Errors are re-raised as meaningful domain exceptions (e.g., `ValueError("A review already exists for this restaurant")`) — not raw SQLAlchemy error messages
- [ ] No `except` block silently swallows an exception without at minimum logging it

**Common mistake check:** Catching `Exception` broadly and printing the error. This masks the exception type (making debugging harder), leaves the session in a broken state, and presents raw database internals to the caller rather than a meaningful message.

**Self-review:** What is the difference between catching `IntegrityError` and catching `Exception`? What do you lose by catching too broadly?

---

**Phase 3 Complete When:** A Python script can open a session, execute a read query, commit a write, and recover cleanly from a deliberately triggered constraint violation — all without crashing or leaking connections.

---

## Phase 4 — CRUD Operations & Business Logic

### 4.1 User Registration
- [ ] `create_user()` inserts a row into `users` and returns the created user
- [ ] The password is hashed before insertion — plaintext is never written to the database
- [ ] A duplicate email submission raises a caught `IntegrityError` that is converted to a clear, user-facing message — not a raw database error
- [ ] The INSERT uses parameterized values — no f-strings or string concatenation in the query

**Common mistake check:** Storing plaintext passwords. Even in a learning project, this is the habit that causes real-world breaches. Use `bcrypt` or `hashlib` with a salt — the mechanics matter less than the principle that passwords are never stored as-is.

**Self-review:** If your `users` table were leaked tomorrow, what would an attacker be able to do with hashed passwords vs. plaintext passwords?

---

### 4.2 Restaurant Management
- [ ] All three functions (`create_restaurant`, `get_restaurant`, `list_restaurants`) use parameterized query values — no user-supplied input is concatenated into a SQL string
- [ ] `get_restaurant` and `list_restaurants` name specific columns in the SELECT — no `SELECT *` appears in application code
- [ ] `list_restaurants` with `city=None` and `cuisine=None` returns all restaurants without error — the optional filter logic handles `None` correctly and does not produce malformed SQL
- [ ] `get_restaurant` returns `None` (or raises a clear exception) when the ID does not exist — it does not crash with an unhandled `NoneType` error

**Common mistake check:** Using f-strings to build filter conditions (e.g., `f"WHERE city = '{city}'"`) when optional filters are applied. This is the most common place SQL injection is introduced — always use parameterized placeholders even for optional values.

**Self-review:** How would you test that `list_restaurants` is safe against SQL injection? What input would you try?

---

### 4.3 Review Operations
- [ ] `create_review()` handles the `IntegrityError` from the unique constraint and raises a clear message — not a raw database error
- [ ] `get_reviews_for_restaurant()` names specific columns in the SELECT and returns results ordered by `created_at DESC`
- [ ] `update_review()` includes `user_id` in the `WHERE` clause — a user cannot update another user's review
- [ ] `delete_review()` includes `user_id` in the `WHERE` clause — a user cannot delete another user's review
- [ ] All raw SQL in these functions uses uppercase keywords, one clause per line, and table aliases for multi-table queries — see BP §3.5
- [ ] All values passed into queries use parameterized placeholders — no concatenation anywhere

**Common mistake check:** Writing `UPDATE reviews SET ... WHERE id = {review_id}` without also checking `user_id`. This passes all functional tests but allows any authenticated user to modify any review. The ownership check must be in the SQL `WHERE` clause — not just a Python `if` statement before the query.

**Self-review:** Why is the ownership check safer in the SQL `WHERE` clause than in a Python `if` statement before the query? What scenario does the SQL approach protect against that the Python approach does not?

---

### 4.4 Read Operations & Aggregates
- [ ] The average rating query uses `COALESCE(AVG(rating), 0)` — it returns `0` for a restaurant with no reviews rather than `None`
- [ ] The user review history query joins `reviews` with `restaurants` and returns restaurant names — not just IDs
- [ ] Both queries name specific columns in SELECT — no `SELECT *`
- [ ] Both queries use table aliases and follow the SQL formatting style from BP §3.5

**Common mistake check:** Returning `None` from the average rating query when a restaurant has no reviews, then trying to format or compare that `None` in Python without a null check. `COALESCE` handles this at the SQL level and is cleaner than a Python `if result is None` workaround.

**Self-review:** What is the difference between `AVG()` returning `NULL` and `COALESCE(AVG(), 0)` returning `0`? Are there cases where returning `NULL` instead of `0` is actually the more correct choice?

---

### 4.5 End-to-End Verification
- [ ] Running `main.py` executes all operations in sequence without errors: register a user, add a restaurant, submit a review, update it, read it back, and delete it
- [ ] Attempting to submit a second review from the same user for the same restaurant produces a clear error message — not a crash
- [ ] Calling `update_review` with a mismatched `user_id` updates zero rows and does not raise an unhandled exception
- [ ] The output of `main.py` is readable — column values are labeled, not printed as raw tuples

**Common mistake check:** Testing only the happy path. The definition of done requires explicitly testing failure cases: duplicate review, mismatched ownership, missing records. A function that only works when given valid input is not finished.

**Self-review:** If you were asked to demo this project in a technical interview, what would you run to show it working? What failure cases would you demonstrate to show you understand the constraints?

---

**Phase 4 Complete When:** Every CRUD function handles both the success path and the relevant failure paths. Business rules are enforced at the database level and handled gracefully at the application level. `main.py` produces clean, labeled output end-to-end.

---

## Project-Wide Standards

These criteria apply to every task in every phase. If any of these are violated, the task is not done regardless of whether the phase-specific criteria are met.

| Standard | Check |
|---|---|
| No credentials in source code | `git grep -i "password"` returns no hits in `.py` files |
| No `SELECT *` in application code | All SELECT statements in `crud.py` name columns explicitly |
| All queries parameterized | No f-strings or `%` string formatting used to build SQL |
| `snake_case` throughout | All table names, column names, and index names use `snake_case` |
| `TIMESTAMPTZ` on all timestamps | No bare `TIMESTAMP` columns in the schema |
| Sessions always closed | No `Session()` call exists outside of a `with` block |
| Errors never swallowed | No `except` block exists without a `rollback()` and a re-raise or log |
| `.env` never committed | `git log --all --full-history -- .env` returns no commits |
