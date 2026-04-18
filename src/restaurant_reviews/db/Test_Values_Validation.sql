INSERT INTO users (username, email, password_hash)
VALUES ('testuser', 'test@gmail.com', 'hashedpassword123');

INSERT INTO restaurants (restaurant_name, city, state)
VALUES ('Test Restaurant', 'Austin', 'TX');

INSERT INTO reviews (user_id, restaurant_id, review_text, rating)
VALUES (1, 1, 'Great food!', 4.5);

INSERT INTO reviews (user_id, restaurant_id, review_text, rating)
VALUES (1, 1, 'Different text', 3.0);

INSERT INTO reviews (user_id, restaurant_id, review_text, rating)
VALUES (1, 2, 'Bad rating test', 6.0);

SELECT * FROM reviews WHERE user_id = 1;

DELETE FROM users WHERE user_id = 1;

SELECT * FROM reviews WHERE user_id = 1;