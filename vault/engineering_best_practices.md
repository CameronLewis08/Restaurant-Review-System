# Engineering Best Practices
## Restaurant Review System — PostgreSQL + Python Reference

This file is a reference guide covering best practices across four areas relevant to this project. Each practice includes what it is, why it matters, and where beginner and production-standard approaches diverge.

---

## Table of Contents

1. [Database / Schema Design](#1-database--schema-design)
2. [Python Code Quality](#2-python-code-quality)
3. [SQL Best Practices](#3-sql-best-practices)
4. [Project / Repo Structure](#4-project--repo-structure)
5. [Beginner-to-Production Summary](#5-beginner-to-production-summary)
6. [Sources](#6-sources)

---

## 1. Database / Schema Design

### 1.1 Normalization to Third Normal Form (3NF)

**What it is:** 3NF requires that every non-key column depends on the primary key, the whole primary key, and nothing but the primary key. For this project:
- `users` holds only user-specific data — no denormalized restaurant info
- `restaurants` holds only restaurant-specific data — no embedded review aggregates
- `reviews` holds only review data, referencing `users` and `restaurants` by foreign key — it does not repeat the restaurant name or user email

**Why it matters:** Violations of 3NF create update anomalies. If a restaurant's name is stored inside `reviews`, updating that name requires touching every row in the reviews table rather than one row in `restaurants`. Over time, denormalized data drifts out of sync and becomes unreliable.

**Beginner vs. production:**
- Beginners often store redundant data (e.g., `restaurant_name` in reviews) to avoid joins. This is a short-term convenience that creates long-term consistency problems.
- Production systems normalize by default and only denormalize intentionally — for example in reporting tables or materialized views — never by accident.

---

### 1.2 Constraint Design

**What it is:** Rules enforced by the database engine itself, independently of application code. Even if your Python code is bypassed, the database still enforces its own rules.

**Core constraint types for this project:**

| Constraint | Example | Purpose |
|---|---|---|
| `PRIMARY KEY` | `id SERIAL PRIMARY KEY` | Unique row identity, auto-indexed |
| `FOREIGN KEY` | `user_id INT REFERENCES users(id)` | Referential integrity between tables |
| `NOT NULL` | `email TEXT NOT NULL` | Prevents missing required data |
| `UNIQUE` | `UNIQUE(email)` on users | Prevents duplicate accounts |
| `CHECK` | `CHECK (rating BETWEEN 1 AND 5)` | Domain validation on review ratings |

**`ON DELETE` behavior — always declare it explicitly:**

| Behavior | Meaning | Use When |
|---|---|---|
| `RESTRICT` | Prevents deleting a parent row if children exist | Safe default — forces deliberate cleanup |
| `CASCADE` | Automatically deletes child rows | Child rows are truly disposable (e.g., session tokens) |
| `SET NULL` | Sets the FK column to NULL | Child rows should survive orphaned (e.g., a review outliving a deleted user) |

**Why it matters:** Application-level validation alone is insufficient — other scripts, admin tools, or future developers can write directly to the database and bypass your Python code. Constraints are the last line of defense.

**Beginner vs. production:**
- Beginners often skip `CHECK` constraints and rely entirely on Python validation.
- Beginners often omit explicit `ON DELETE` behavior. Production designs declare it explicitly so the intent is documented in the schema itself.

---

### 1.3 Naming Conventions

**What it is:** A consistent, lowercase `snake_case` naming scheme for all database objects.

**Rules:**
- **Tables:** plural, snake_case — `users`, `restaurants`, `reviews`
- **Columns:** singular, snake_case — `user_id`, `created_at`, `restaurant_name`
- **Primary keys:** `id` (preferred) or `{table}_id`
- **Foreign keys:** `{referenced_table_singular}_id` — `user_id`, `restaurant_id`
- **Booleans:** prefix with `is_` or `has_` — `is_verified`, `has_responded`
- **Timestamps:** `created_at`, `updated_at` (standard across ORMs and tooling)
- **Indexes:** `idx_{table}_{column}` — `idx_reviews_user_id`

**Why it matters:** PostgreSQL folds unquoted identifiers to lowercase. If you use `camelCase` or `PascalCase` without double-quoting everywhere, you will encounter case mismatch errors. `snake_case` avoids the quoting requirement entirely and works cleanly with SQLAlchemy, psycopg2, and migration tools.

**Beginner vs. production:**
- Beginners sometimes use PascalCase (mirroring Python class naming) or inconsistent abbreviations (`usr`, `rst`). This creates quoting requirements and confusion.
- Production teams document and enforce a naming convention in a schema style guide or linter such as `squawk` for PostgreSQL.

---

### 1.4 Indexing Basics

**What it is:** An index is a separate data structure that speeds up lookups at the cost of additional write overhead and storage. The default index type in PostgreSQL is a B-tree, which handles `=`, `<`, `>`, `BETWEEN`, `ORDER BY`, and `IS NULL` efficiently.

**When to create an index:**

1. **Primary keys** — PostgreSQL creates these automatically.
2. **Unique constraints** — PostgreSQL creates these automatically.
3. **Foreign key columns on the child (referencing) side** — PostgreSQL does NOT create these automatically. Without them, every `JOIN` and every `ON DELETE CASCADE` check requires a full sequential scan of the child table. For this project, index `reviews.user_id` and `reviews.restaurant_id`.
4. **Columns appearing in frequent `WHERE` clauses** — e.g., `restaurants.city`, `reviews.rating`.

```sql
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_restaurant_id ON reviews(restaurant_id);
CREATE INDEX idx_users_email ON users(email);
```

**Why it matters:** Unindexed FK columns are one of the most common beginner performance pitfalls. A table with 10 rows never shows the problem — a table with 100,000 rows grinds to a halt without them.

**Beginner vs. production:**
- Beginners either index everything preemptively (wasting write performance and disk) or nothing at all.
- Production systems add FK indexes as a baseline, then add others only after observing real query patterns using `EXPLAIN ANALYZE` and `pg_stat_user_indexes`. Unused indexes waste space and slow writes.

---

### 1.5 Data Types

**What it is:** Choosing the most appropriate PostgreSQL column type for each piece of data.

| Column | Recommended Type | Avoid | Reason |
|---|---|---|---|
| Primary keys | `SERIAL` or `BIGSERIAL` | Manually managed `INT` | Auto-increment, no nullability risk |
| Names, free text | `TEXT` | `CHAR(n)` | `CHAR(n)` pads with spaces; `TEXT` is equally performant |
| Email, constrained strings | `VARCHAR(254)` | Unconstrained `TEXT` | Adds a length validation layer at the DB level |
| Ratings (1–5) | `SMALLINT` + `CHECK` | `FLOAT` | No floating-point imprecision for whole-number values |
| Money / prices | `NUMERIC(10,2)` | `FLOAT`, `REAL`, `MONEY` | Floating-point arithmetic is imprecise; `MONEY` is locale-dependent |
| Timestamps | `TIMESTAMPTZ` | `TIMESTAMP` (no tz) | `TIMESTAMPTZ` stores UTC and converts per session timezone; `TIMESTAMP` loses timezone context silently |
| Boolean flags | `BOOLEAN` | `SMALLINT` 0/1 | Semantic clarity; reads as `TRUE`/`FALSE` not `1`/`0` |

**Key rule from the PostgreSQL wiki (Don't Do This):** Never use `CHAR(n)` (blank-padding waste), never use `TIMESTAMP` without timezone, never use `MONEY`.

---

## 2. Python Code Quality

### 2.1 Code Structure — Separation of Concerns

**What it is:** Splitting database logic into distinct modules rather than writing all logic in a single file.

**Recommended module layout:**
```
db/
├── connection.py    # engine/session factory, pool configuration
├── models.py        # SQLAlchemy ORM model definitions
└── crud.py          # one function per logical DB operation
config.py            # loads and validates environment variables
main.py              # entry point and orchestration only
```

**Why it matters:** When all database logic lives in one file, a schema change forces edits in unrelated code. The single-responsibility principle makes each module independently readable, testable, and replaceable.

**Beginner vs. production:**
- Beginners write long scripts where connection setup, SQL strings, and business logic are all interleaved. Fine for exploration but unmaintainable at scale.
- Production projects (and FastAPI/Django patterns) enforce strict layering: ORM models in `models.py`, data access in a CRUD/repository layer, connection factory isolated in its own module.

---

### 2.2 Connection Management

**What it is:** Creating and releasing database connections in a controlled, predictable way.

**psycopg2 pattern:**
```python
import psycopg2

conn = psycopg2.connect(dsn=DATABASE_URL)
try:
    with conn:               # manages the TRANSACTION — commits on success, rolls back on exception
        with conn.cursor() as cur:
            cur.execute("SELECT ...")
finally:
    conn.close()             # 'with conn:' does NOT close the connection — you must do this manually
```

**SQLAlchemy 2.0 pattern (recommended):**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

with Session(engine) as session:
    result = session.execute(...)
    session.commit()
```

SQLAlchemy's `QueuePool` maintains a pool of persistent connections, eliminating per-request connection overhead.

**Critical psycopg2 distinction:** The `with conn:` context manager manages the transaction but does NOT close the connection. You must call `conn.close()` explicitly or use a connection pool.

**Beginner vs. production:**
- Beginners open a new `psycopg2.connect()` for every query and forget to close it — leaking connections until PostgreSQL's `max_connections` limit is hit.
- Production systems use SQLAlchemy's pool, configure `pool_size`, `max_overflow`, and `pool_timeout`, and never hold connections open outside of an active transaction.

---

### 2.3 Error Handling

**What it is:** Catching specific database exceptions, rolling back on failure, and surfacing meaningful errors — never swallowing them silently.

**psycopg2 exception hierarchy:**
- `psycopg2.DatabaseError` — base class for all DB errors
- `psycopg2.OperationalError` — connection failures, server unavailable
- `psycopg2.ProgrammingError` — SQL syntax errors, missing tables
- `psycopg2.IntegrityError` — constraint violations (duplicate key, foreign key failure)

```python
from psycopg2 import OperationalError, IntegrityError

try:
    with conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
except IntegrityError as e:
    conn.rollback()
    raise ValueError(f"Constraint violation: {e}") from e
except OperationalError as e:
    conn.rollback()
    raise RuntimeError(f"Database unavailable: {e}") from e
```

**SQLAlchemy equivalent:**
```python
from sqlalchemy.exc import IntegrityError

try:
    with Session(engine) as session:
        session.add(obj)
        session.commit()
except IntegrityError as e:
    session.rollback()
    raise
```

**Why it matters:** Catching bare `Exception` and printing the error leaves the connection in a broken transaction state (`InFailedSqlTransaction`). Every subsequent query on that connection will fail until you roll back.

**Beginner vs. production:**
- Beginners catch `Exception` and print, or catch nothing and let the program crash.
- Production code catches specific exceptions, always rolls back on failure, logs the full exception with context, and re-raises or converts to a domain exception. It never swallows exceptions silently.

---

### 2.4 Credentials and Environment Variables

**What it is:** Storing database credentials outside of source code, loaded from the environment at runtime using `python-dotenv`.

**`.env` file (never committed to git):**
```
DATABASE_URL=postgresql://appuser:supersecret@localhost:5432/restaurant_reviews
DB_HOST=localhost
DB_PORT=5432
DB_NAME=restaurant_reviews
DB_USER=appuser
DB_PASSWORD=supersecret
```

**`config.py`:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]  # use [] not .get() — fail fast if the variable is missing
```

**Why it matters:** Hard-coded credentials are the most common cause of credential exposure in public repositories. One accidental `git push` and the credentials must be considered compromised — rotation is required, not just deletion. The Twelve-Factor App methodology (Factor III: Config) mandates strict separation of config from code.

**Beginner vs. production:**
- Beginners hard-code `psycopg2.connect(host="localhost", password="password")` directly in scripts.
- Production systems inject secrets via CI/CD (GitHub Actions secrets, AWS Secrets Manager, HashiCorp Vault). `python-dotenv` is the correct beginner bridge — it mimics the production pattern locally without requiring infrastructure.

---

## 3. SQL Best Practices

### 3.1 Parameterized Queries — SQL Injection Prevention

**What it is:** Using placeholder syntax to pass user-supplied values to queries, never building SQL strings via concatenation.

**Correct psycopg2 pattern:**
```python
cur.execute(
    "SELECT * FROM reviews WHERE restaurant_id = %s AND rating >= %s",
    (restaurant_id, min_rating)
)
```

**Never do this:**
```python
# SQL injection vulnerability
query = f"SELECT * FROM reviews WHERE restaurant_id = {restaurant_id}"
cur.execute(query)
```

**For dynamic identifiers** (table/column names cannot use `%s`) — use `psycopg2.sql`:
```python
from psycopg2 import sql

query = sql.SQL("SELECT {} FROM {}").format(
    sql.Identifier("rating"),
    sql.Identifier("reviews")
)
```

**Why it matters:** String concatenation with user input allows an attacker to inject arbitrary SQL. A value like `'; DROP TABLE users; --` becomes a destructive command. Parameterization treats all user input as data, never as SQL code.

**Beginner vs. production:**
- Beginners believe that validating input (e.g., checking that a value is an integer) makes concatenation safe. It does not — the attack surface shifts with every new input type.
- Production code uses parameterized queries universally, no exceptions. SQLAlchemy ORM handles this automatically for model-based queries, but raw `text()` calls still require explicit `bindparams`.

---

### 3.2 Avoid `SELECT *`

**What it is:** Always explicitly naming the columns you need in SELECT statements.

```sql
-- Avoid
SELECT * FROM reviews WHERE restaurant_id = 1;

-- Correct
SELECT id, rating, body, created_at FROM reviews WHERE restaurant_id = 1;
```

**Why it matters:**
1. `SELECT *` returns all columns including ones you don't need, increasing network payload unnecessarily.
2. If the schema changes — a column is added, removed, or reordered — `SELECT *` silently changes what your application receives, often introducing subtle bugs.
3. Explicit column lists sometimes allow PostgreSQL to use index-only scans, improving query performance.

**Beginner vs. production:**
- Beginners use `*` to avoid typing column names — acceptable at a `psql` prompt for exploration, but should never appear in application code.
- Production code is explicit about every column returned. SQLAlchemy ORM handles this naturally since model queries map specific columns.

---

### 3.3 Transaction Handling

**What it is:** Grouping related SQL operations into atomic units that either all succeed or all fail together.

**psycopg2 — every connection starts a transaction automatically:**
```python
with conn:  # auto-commits on success, rolls back on exception
    cur.execute("INSERT INTO reviews ...")
    cur.execute("UPDATE restaurants SET review_count = review_count + 1 ...")
```

**SQLAlchemy 2.0:**
```python
with engine.begin() as conn:  # auto-commits on exit, rolls back on exception
    conn.execute(insert_review)
    conn.execute(update_restaurant_stats)
```

**Why it matters:** Without transaction boundaries, a crash between two related operations (e.g., inserting a review and updating an aggregate count) leaves the database in an inconsistent state. Transactions guarantee atomicity — all operations succeed, or none of them do.

**Beginner vs. production:**
- Beginners call `conn.commit()` after every single statement, which works for single operations but makes multi-step operations non-atomic.
- Production code groups logically related operations into a single transaction with clear rollback paths. Long-running transactions are avoided because they hold locks and block other writers.

---

### 3.4 NULL Handling

**What it is:** Understanding that `NULL` means "unknown" in SQL — not zero, not empty string — and that it does not behave like a normal value in comparisons.

**Critical rules:**
- `NULL = NULL` evaluates to `NULL` (not `TRUE`) — always use `IS NULL` / `IS NOT NULL`
- A `NULL` in a `WHERE` condition causes the row to be excluded silently
- `NOT IN (...)` with a `NULL` in the subquery returns no rows — a common and silent bug
- `COALESCE(value, default)` returns the first non-NULL argument — use it for safe fallbacks

```sql
-- Wrong — returns NULL, not TRUE, so the row is silently excluded
WHERE review_body = NULL

-- Correct
WHERE review_body IS NULL

-- Safe aggregation with a fallback when there are no reviews
SELECT COALESCE(AVG(rating), 0) AS avg_rating FROM reviews WHERE restaurant_id = $1;
```

**Beginner vs. production:**
- Beginners discover NULL bugs only when unexpected empty results appear. The root cause is usually a `WHERE column != 'value'` that silently excludes NULL rows.
- Production schemas minimize nullable columns by applying `NOT NULL` constraints wherever a value is always required, reducing the surface area for NULL-related bugs from the start.

---

### 3.5 Query Readability

**What it is:** Writing SQL in a consistent, formatted style — uppercase keywords, proper indentation, and meaningful aliases.

```sql
-- Hard to read
select r.id,r.body,r.rating,u.username from reviews r join users u on r.user_id=u.id where r.restaurant_id=1 order by r.created_at desc;

-- Readable
SELECT
    r.id,
    r.body,
    r.rating,
    u.username
FROM reviews AS r
JOIN users AS u ON r.user_id = u.id
WHERE r.restaurant_id = 1
ORDER BY r.created_at DESC;
```

**Why it matters:** SQL is read far more often than it is written. Reviewers, future maintainers, and yourself six months later will thank you. Readable SQL also makes bugs — like a missing `WHERE` clause — far easier to catch in review.

The [SQL Style Guide by Simon Holywell](https://www.sqlstyle.guide/) is the widely adopted community standard for SQL formatting.

---

## 4. Project / Repo Structure

### 4.1 Folder Organization

**Recommended structure for this project:**

```
restaurant-review-system/
├── src/
│   └── restaurant_reviews/
│       ├── __init__.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py     # engine/session factory
│       │   ├── models.py         # SQLAlchemy ORM models
│       │   └── crud.py           # insert_user(), get_reviews(), etc.
│       ├── config.py             # loads env vars, exposes settings
│       └── main.py               # entry point / CLI
├── migrations/                   # Alembic migration files (if used)
│   └── versions/
├── tests/
│   └── test_crud.py
├── vault/                        # reference documents (this file lives here)
├── .env                          # NEVER committed — local secrets
├── .env.example                  # committed — template with dummy values
├── .gitignore
├── requirements.txt              # OR pyproject.toml
└── README.md
```

**Why the `src/` layout:** It prevents the package source from being accidentally imported during testing without installation, catching import errors early. This is the Python Packaging Authority's current recommendation.

**Beginner vs. production:**
- Beginners put all `.py` files in the root directory — this works but conflates package code with config files and tests.
- Production projects use the `src` layout, a separate `tests/` directory, and a `migrations/` directory managed by Alembic for tracked, reversible schema changes.

---

### 4.2 Dependency Management

**`requirements.txt` (beginner-friendly, still widely used in data engineering):**
```
psycopg2-binary==2.9.9
sqlalchemy==2.0.30
python-dotenv==1.0.1
```
Pin exact versions with `pip freeze > requirements.txt`. Install with `pip install -r requirements.txt`.

**`pyproject.toml` (modern standard — PEP 517/518/621):**
```toml
[project]
name = "restaurant-reviews"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "psycopg2-binary>=2.9",
    "sqlalchemy>=2.0",
    "python-dotenv>=1.0",
]
```

**Why it matters:** `pyproject.toml` is the Python Packaging Authority's current standard. It unifies project metadata, dependencies, and build configuration in one file. Tools like `uv`, `hatch`, and `rye` use it natively.

**Beginner vs. production:**
- `requirements.txt` is acceptable and still very common — no shame in starting here.
- Production Python projects increasingly use `pyproject.toml` with a lock file (`uv.lock` or `poetry.lock`) for fully reproducible environments.

---

### 4.3 `.gitignore` for a Python DB Project

**Critical entries:**
```gitignore
# Secrets — must be here BEFORE the first commit
.env
*.env

# Python bytecode
__pycache__/
*.pyc
*.pyo

# Virtual environments
.venv/
venv/
env/

# Distribution / build
dist/
build/
*.egg-info/

# Testing / coverage
.pytest_cache/
.coverage
htmlcov/

# Editor / OS
.DS_Store
.idea/
.vscode/
*.swp
```

**The single most important rule:** `.env` must be in `.gitignore` before the first commit. Once a credential has been committed to git history, it must be considered compromised — deleting it from the latest commit is not enough. Rotation is required.

**Companion file — `.env.example`:** Create this and commit it. It documents what variables are required without exposing real values:
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DB_HOST=localhost
DB_PORT=5432
```

**Beginner vs. production:**
- Beginners add `.env` to `.gitignore` after accidentally committing it once.
- Production systems use tools like `git-secrets` or a `detect-secrets` pre-commit hook to block credentials from being committed at all.

---

### 4.4 Centralized Config Pattern

**What it is:** A single `config.py` that loads and validates all environment variables in one place, so the rest of the application imports from config rather than calling `os.environ` directly throughout the codebase.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]   # KeyError = fail fast on missing config
DB_POOL_SIZE: int = int(os.environ.get("DB_POOL_SIZE", "5"))
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
```

```python
# db/connection.py — imports from config, never reads os.environ directly
from config import DATABASE_URL
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)
```

**Why it matters:** If `os.environ` calls are scattered across the codebase, adding, renaming, or validating an environment variable requires hunting through every file. Centralizing config means one place to audit, one place to add validation, and one place to document required variables.

**Beginner vs. production:**
- Beginners call `os.environ.get("DB_PASSWORD")` directly inside connection functions scattered across files.
- Production uses Pydantic's `BaseSettings` (from `pydantic-settings`) for typed, validated, automatically loaded config — a significant upgrade that provides type coercion and clear error messages on missing or malformed variables.

---

## 5. Beginner-to-Production Summary

| Area | Beginner Starting Point | Production Standard |
|---|---|---|
| **Schema Design** | 3NF tables, basic PKs and FKs | All constraints explicit, `ON DELETE` declared, FK columns indexed, `TIMESTAMPTZ` throughout |
| **Python Code** | Scripts with inline SQL and open connections | Layered modules: config / connection / models / crud; SQLAlchemy session pool |
| **SQL** | Parameterized queries, basic transactions | Explicit column lists, `COALESCE` for NULLs, transactions grouping related operations |
| **Repo Structure** | `requirements.txt`, `.gitignore` | `pyproject.toml` or `uv`, `.env.example`, pre-commit hooks for secrets, `src/` layout |

---

## 6. Sources

- [PostgreSQL Docs: Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL Docs: CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL Wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Percona: Should I Create an Index on Foreign Keys in PostgreSQL?](https://www.percona.com/blog/should-i-create-an-index-on-foreign-keys-in-postgresql/)
- [SQLAlchemy 2.0 Docs: Working with Engines and Connections](https://docs.sqlalchemy.org/en/20/core/connections.html)
- [SQLAlchemy 2.0 Docs: Session Transaction Management](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)
- [psycopg2 Docs: Error Classes](https://www.psycopg.org/docs/errors.html)
- [Real Python: Preventing SQL Injection Attacks With Python](https://realpython.com/prevent-python-sql-injection/)
- [Python Packaging User Guide: Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python Packaging User Guide: src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [SQL Style Guide by Simon Holywell](https://www.sqlstyle.guide/)
- [Twelve-Factor App: Config](https://12factor.net/config)
