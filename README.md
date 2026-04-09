# Restaurant Review System

## Project Description

The Restaurant Review System is a relational database application that models a public review platform. Users can create accounts and profiles, browse restaurants, and submit one review per restaurant that includes text and images. The system enforces data integrity through database constraints, ensures reviews remain current through update capabilities, and maintains normalization to prevent data redundancy.

This project emphasizes real-world database design patterns and is specifically structured to prepare you for data engineering and backend technical interviews, where schema design is a critical evaluation skill.

## Tools & Architecture

### PostgreSQL
PostgreSQL serves as the relational database management system (RDBMS) and is responsible for:
- Storing all structured data (users, restaurants, reviews)
- Enforcing constraints at the database level (unique constraints, foreign keys, NOT NULL)
- Managing transactions to ensure data integrity during review updates
- Providing ACID guarantees for concurrent user access

### Python with psycopg2 / SQLAlchemy
Python acts as the application layer and bridges user interactions with the database:
- **psycopg2**: A lightweight PostgreSQL adapter for executing raw SQL queries and managing connections
- **SQLAlchemy**: An ORM (Object-Relational Mapping) tool that abstracts database operations into Python objects, reducing boilerplate and providing a higher-level interface

**How They Interact:**
1. User actions (sign up, create review, update review) are captured at the application level
2. Python translates these actions into SQL queries (either raw SQL via psycopg2 or ORM operations via SQLAlchemy)
3. PostgreSQL validates and executes the queries, enforcing all constraints
4. The database returns results, which Python formats and returns to the user interface

## Key Features

- **Schema Design**: Implements a normalized relational schema with users, restaurants, and reviews tables
- **Constraints**: Enforces one review per user/restaurant pair and maintains referential integrity
- **Data Integrity**: Update operations preserve consistency and prevent orphaned records
- **Scalability**: The schema structure supports horizontal scaling and efficient querying

## Expected Outcomes

Upon completion, you will have:

1. **A Production-Ready Schema**: A fully normalized database design that demonstrates understanding of:
   - Table relationships (one-to-many, implicit many-to-many)
   - Constraint design and enforcement
   - Data normalization principles (3NF)

2. **Working Application Logic**: Python code that:
   - Connects reliably to PostgreSQL
   - Handles user registration and authentication workflows
   - Creates, reads, updates, and deletes reviews with proper error handling
   - Validates business logic (one review per user/restaurant)

3. **Interview-Ready Knowledge**: 
   - Ability to explain your design decisions in a technical setting
   - Understanding of why each table and constraint exists
   - Concrete examples of schema evolution and optimization trade-offs
   - Real experience debugging data integrity issues

4. **Portfolio Evidence**: A complete project demonstrating backend database engineering skills that directly addresses common data engineering technical interview questions.

## Why This Matters in 2026

Schema design remains a cornerstone of data engineering and backend interviews. Companies prioritize engineers who can think through data models because poor schema design compounds into technical debt. This project gives you both the practical experience and the narrative to confidently discuss database design with interviewers.