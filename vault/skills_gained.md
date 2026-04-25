# Skills Gained
## Restaurant Review System

A record of every skill area covered over the course of building this project from scratch.

---

## Database Engineering

- **Schema design** — 3NF normalization, identifying what data belongs to each table
- **PostgreSQL DDL** — `CREATE TABLE`, `SERIAL`/`IDENTITY`, `TIMESTAMPTZ`, `VARCHAR`, `NUMERIC`
- **Constraint design** — `PRIMARY KEY`, `FOREIGN KEY`, `NOT NULL`, `UNIQUE`, `CHECK`, composite constraints
- **Foreign key behavior** — `ON DELETE CASCADE` vs `RESTRICT` vs `SET NULL` and when to use each
- **Indexing** — why PostgreSQL does not auto-index FK columns, B-tree indexes, trade-offs of over-indexing
- **Triggers** — writing a `BEFORE UPDATE` trigger to auto-update `updated_at`
- **Aggregates** — `AVG()`, `COALESCE()`, `GROUP BY`, handling NULL in aggregate functions
- **User and permission management** — `GRANT`, `REVOKE`, `ALTER TABLE OWNER`, principle of least privilege

---

## Python & ORM

- **Virtual environments** — isolation, why global installs are dangerous
- **SQLAlchemy 2.0** — `DeclarativeBase`, `Mapped`, `mapped_column`, `relationship`, `back_populates`
- **Session management** — context manager pattern, commit/rollback/close lifecycle, connection pooling (`pool_size`, `max_overflow`, `expire_on_commit`)
- **Error handling** — catching `IntegrityError` specifically, converting database errors to domain exceptions
- **bcrypt** — password hashing, salting, why plaintext storage is never acceptable
- **Environment variables** — `python-dotenv`, fail-fast config with bracket syntax vs silent `.get()`
- **`src` layout** — why it exists, `pyproject.toml`, editable installs with `pip install -e .`
- **Type annotations** — `Mapped[int]`, `Optional[str]`, `str | None`, typed return signatures

---

## API Design

- **FastAPI** — route definitions, path vs query parameters, request/response models
- **Pydantic v2** — `BaseModel`, `from_attributes`, separating input schemas from response schemas
- **REST conventions** — correct HTTP methods (`GET`, `POST`, `PATCH`, `DELETE`), status codes (400 vs 404)
- **Route ordering** — why specific routes must come before parameterized routes in FastAPI/Starlette
- **Pagination** — `limit` and `offset` pattern on list endpoints

---

## Testing

- **pytest** — fixtures, `autouse`, `yield`, arrange/act/assert structure
- **Test isolation** — `TRUNCATE` before and after each test, why order-dependent tests are fragile
- **Edge case testing** — duplicate records, invalid foreign keys, out-of-range values, not-found cases
- **Coverage** — `pytest-cov`, reading coverage output, distinguishing meaningful gaps from expected gaps
- **Coverage configuration** — omitting files in `pyproject.toml`, understanding why 100% is not always the goal

---

## DevOps & Workflow

- **Git** — `.gitignore` before first commit, never committing credentials, why history matters
- **GitHub Actions** — workflow YAML structure, `on: pull_request`, `services:` for dependency containers, job-level `env:`, health checks
- **GitHub Secrets** — storing credentials outside the codebase, referencing them in workflows
- **CI pipelines** — what it means to run tests on a fresh environment, why local-only testing is insufficient
- **Docker (conceptual)** — understanding that service containers are ephemeral and self-contained

---

## Engineering Practices

- **Separation of concerns** — connection, models, CRUD, API, config each in their own layer
- **Fail-fast principle** — surfacing missing config at startup rather than at runtime
- **Least privilege** — application users vs superusers, test users vs application users
- **Reproducibility** — pinned dependencies, fresh clone testing, CI as the source of truth
- **Definition of Done** — treating "it works" as insufficient without checking constraints, edge cases, and standards compliance
