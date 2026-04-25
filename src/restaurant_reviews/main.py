import restaurant_reviews.db.crud as crud
import json
import os
def main():
    # Example usage
    
    file_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    with open(file_path, "r") as file:
        data = json.load(file)

    for user_data in data["users"]:
        crud.create_user(user_data["username"], user_data["email"], user_data["password"])

    for restaurant_data in data["restaurants"]:
        crud.create_restaurant(
            restaurant_data["restaurant_name"],
            restaurant_data["address"],
            restaurant_data["city"],
            restaurant_data["state"]
        )
    
    for review_data in data["reviews"]:
        user = crud.get_user_by_username(review_data["username"])
        restaurant = crud.get_restaurant_by_name(review_data["restaurant_name"])
        crud.create_review(
            user.user_id,
            restaurant.restaurant_id,
            review_data["rating"],
            review_data.get("review_text")
        )

    print("========================================================================================================================")
    print("                                  USERS                ")
    print("                 Username         Email              Created At")
    print("--------------------------------------------------------------------------------------------------------")
    for user in crud.list_users():
        print(f"{user.username:<15}  |  {user.email:<25}  |  {str(user.created_at):<25}")
    print("========================================================================================================================")




    print("========================================================================================================================")
    print("                                                                 RESTAURANTS              ")
    print("           Restaurant_id       Restaurant Name      Address                 City            State       Created At")
    print("--------------------------------------------------------------------------------------------------------")
    for restaurant in crud.list_restaurants():
        print(f"{restaurant.restaurant_id:<10}  |  {restaurant.restaurant_name:<25}  |  {restaurant.address:<25}  |  {restaurant.city:<20}  |  {restaurant.state:<40}  |  {str(restaurant.created_at):<50}")

    print("========================================================================================================================")




    print("========================================================================================================================")
    print("                                                             REVIEWS              ")
    print("     User_id      Restaurant_id      Rating      Review Text        Created At          Updated At")
    print("--------------------------------------------------------------------------------------------------------")
    for review in crud.list_reviews():
        print(f"{review.user_id:<10}  |  {review.restaurant_id:<10} |   {review.rating:<5}   {review.review_text:<40}    | {str(review.created_at):<50}  |  {str(review.updated_at):<50}")

    print("========================================================================================================================")




    print("========================================================================================================================")
    print("            AVERAGE RATINGS          ")
    print("Restaurant Name   Average Rating")
    print("--------------------------------------------------------------------------------------------------------")

    for average_rating in crud.list_average_ratings():
        print(f"{average_rating[0]:<15}  |  {average_rating[1]:.2f} stars")

    print("========================================================================================================================")




    print("========================================================================================================================")
    print("                             REVIEW HISTORY           ")
    print("User_id  Restaurant Name      Rating      Review Text                    Created At")
    print("--------------------------------------------------------------------------------------------------------")
    for user in crud.list_users():
        for review in crud.get_review_history(user.user_id):
            print(f"{user.user_id:<10} | {review.restaurant_name:<15} | {float(review.rating):.1f} stars  |  {str(review.review_text):<40}  |  {str(review.created_at):<50} ")

    print("========================================================================================================================")

    print("\nTesting duplicate review rejection...")
    try:
        user = crud.get_user_by_username("john_doe")
        restaurant = crud.get_restaurant_by_name("Pizza Palace")
        crud.create_review(user.user_id, restaurant.restaurant_id, 2.0, "Trying to submit a second review!")
    except ValueError as e:
        print(f"Correctly rejected: {e}")


    
if __name__ == "__main__":
    main()