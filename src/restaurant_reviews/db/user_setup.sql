-- Run this after creating your database user and running schema.sql
GRANT CONNECT ON DATABASE restaurant_reviews TO "your_db_user";
GRANT USAGE ON SCHEMA public TO "your_db_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "your_db_user";
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO "your_db_user";
