CREATE TABLE users (
user_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
username VARCHAR(32) NOT NULL,
email VARCHAR(256) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE restaurants (
restaurant_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
restaurant_name varchar(64) NOT NULL,
city varchar(64) NOT NULL,
state varchar(2) NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reviews (
user_id int references users(user_id) on delete cascade,
restaurant_id int references restaurants(restaurant_id) on delete cascade,
review_text varchar(1024) DEFAULT NULL,
rating NUMERIC(2,1) CHECK (rating between 1 and 5) NOT NULL,
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (user_id, restaurant_id)
);

CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_restaurant_id ON reviews(restaurant_id);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_updated_at
BEFORE UPDATE ON reviews
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();