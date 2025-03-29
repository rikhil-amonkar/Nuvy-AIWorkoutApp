import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

# Load data
food_data = pd.read_csv('datasets/All_Diets.csv')

# Process the initial data
food_data_df = pd.DataFrame(food_data)
food_data_df = food_data_df.dropna() # Data has no missing values but saftey measure

# Calculate calories for meals
food_data_df['Calories(kcal)'] = (food_data_df['Fat(g)'] * 9) + (food_data_df['Carbs(g)'] * 4) + (food_data_df['Protein(g)'] * 4)

# Split the data into features and target
features = food_data_df[['Calories(kcal)']].values

# Standardize the features
scalar = StandardScaler()
features = scalar.fit_transform(features)

# Calculate the nearest neighbors
knn = NearestNeighbors(n_neighbors=5)
knn.fit(features)

# Calculate the nearest neighbors
def recommend_meals(calories_left, meals_wanted):
    if calories_left <= 0:
        return None, 0
    
    # Normalize the calories
    user_input = np.array([[calories_left / meals_wanted]]) # Divide calories left into even meals
    user_input = scalar.transform(user_input)

    # Find the nearest neighbors and retrieve the meal name
    distances, indices = knn.kneighbors(user_input, n_neighbors=meals_wanted)

    # Extract the indices
    neighbor_indices = indices[0]

    # For each meal recommended, add calories and name to final list
    plan_meals = []
    for index in neighbor_indices:
        rec_meal = food_data_df.iloc[index]
        meal_name = rec_meal['Recipe_name']

        # Check for meal duplicates
        if meal_name in plan_meals:
            continue

        meal_calories = float(rec_meal['Calories(kcal)'])
        meal_protein  = float(rec_meal['Protein(g)'])
        meal_carbs  = float(rec_meal['Carbs(g)'])
        meal_fat  = float(rec_meal['Fat(g)'])
        meal_diet = str(rec_meal['Diet_type'])
        plan_meals.append((meal_name, meal_calories, meal_protein, meal_carbs, meal_fat, meal_diet))

        if len(plan_meals) >= meals_wanted:
            break

    return plan_meals

# Calculate the average bmr without activity level
def calculate_bmr(user_age, user_sex, user_height, user_weight):
    
    # Basal Metabolic Rate (BMR) calculation based on sex and Harris-Benedict equation
    if user_sex.upper() == "M":
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) + 5
        daily_bmr = BMR * 1.2
    else:
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) - 161
        daily_bmr = BMR * 1.2

    return daily_bmr

# Calculate the daily calories for user based on activity level
def calculate_daily_calories(daily_bmr, activity_level):
    if activity_level == 1:
        daily_cal = daily_bmr * 1.05
    elif activity_level == 2:
        daily_cal = daily_bmr * 1.15
    elif activity_level == 3:
        daily_cal = daily_bmr * 1.30
    elif activity_level == 4:
        daily_cal = daily_bmr * 1.45
    else:
        daily_cal = daily_bmr * 1.585

    return daily_cal

def recommendor_projection():
    # User body composition
    user_age = int(input("Enter your age: "))
    user_sex = str(input("Enter your sex (M/F): "))
    user_height = int(input("Enter your height in cm: "))
    user_weight = int(input("Enter your weight in kg: "))

    return user_age, user_sex, user_height, user_weight 
    
# Run the program
def recommender_main():

    user_age, user_sex, user_height, user_weight = recommendor_projection()
    daily_bmr = calculate_bmr(user_age, user_sex, user_height, user_weight)

    # Calculate daily calories with activity level
    print(f"\nYour daily BMR is: {daily_bmr:.2f} kcal")
    print("This represents the number of calories your body needs without exercise taken into account.\n")
    print("Now to calculate your daily calories, we need to know your activity level.")
    print("\n1. Sedentary (little or no exercise)")
    print("\n2. Lightly active (light exercise/sports 1-3 days/week)")
    print("\n3. Moderately active (moderate exercise/sports 3-5 days/week)")
    print("\n4. Very active (hard exercise/sports 6-7 days a week)")
    print("\n5. Super active (very hard exercise & physical job or 2x training)")
    activity_level = int(input("\nEnter your activity level: "))
    daily_cal = calculate_daily_calories(daily_bmr, activity_level)

    # Calculate cutting and bulking calories
    print(f"\nThe daily calories you need to maintain your weight is: {daily_cal:.2f} kcal")
    cutting_calories = daily_cal - 500
    bulk_calories = daily_cal + 500
    print(f"\nTo lose 1 lb per week, you need to consume {cutting_calories:.2f} kcal daily.")
    print(f"To gain 1 lb per week, you need to consume {bulk_calories:.2f} kcal daily.")

    # Calculate the calories left for the user
    calories_consumed = int(input("\nEnter the number of calories you have consumed today: "))
    calories_left = daily_cal - calories_consumed

    # Make sure the user has calories left
    if calories_left >= 0:

        # Ask user for their number of meals
        meals_wanted = int(input("How many more meals do you want to eat today?: "))
        print(f"\nHere is a meal plan consisting of {meals_wanted} meals to reach your {calories_left:.2f} kcal for the day:\n")

        # Update the nearest-neighbor meal based on meals wanted
        plan_meals = recommend_meals(calories_left, meals_wanted)
        for i, (meal_name, meal_calories, meal_protein, meal_carbs, meal_fats, meal_diet) in enumerate(plan_meals, start=1):
            if meal_name is None:
                print("No suitable meal found.")
                break

            # Print each meal and update new calories left
            print(f"{i}. {meal_name}\n   Diet Type: {meal_diet}\n   Calories(kcal): {meal_calories:.2f}\n   Protein(g): {meal_protein:.2f}\n   Carbs(g): {meal_carbs:.2f}\n   Fats(g): {meal_fats:.2f}\n")
            calories_left -= meal_calories

            if calories_left <= 0:
                break
    
    else:
        print("You have exceeded your daily calorie intake. Please try again tomorrow.")
        print("Thank you for using the meal recommendation system!")

    return user_age, user_sex, user_height, user_weight

def run_recommender():
    recommender_main()

if __name__ == "__main__":
    run_recommender()
