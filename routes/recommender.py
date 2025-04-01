import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from flask import Blueprint, render_template, request, jsonify

# Initialize blueprint for recommender
recommender = Blueprint("recommender", __name__)

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

# Route the recommended meals using the nearest neighbors
@recommender.route("/recommend_meals", methods=['POST'])
def recommend_meals(calories_left, meals_wanted):
    # Recieve data from frontend
    data = request.get_data()
    calories_left = data.get("calories_left", 0)
    meals_wanted = data.get("meals_wanted", 1)

    # Check if no calories are left to make meals
    if calories_left <= 0:
        return jsonify({"error": "No calories left to allocate"}), 400
    
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

        # Avoid meal duplicates
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

    return jsonify({"recommended meals": plan_meals})

# Route to average BMR from user data
@recommender.route("/calculate_bmr", methods=['POST'])
def calculate_bmr():
    # Recieve the data from the frontend
    data = request.get_json()
    user_age = data.get("age")
    user_sex = data.get("sex")
    user_height = data.get("height")
    user_weight = data.get("weight")
    
    # Check for missing values
    if not all([user_age, user_sex, user_height, user_weight]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Convert sex to proper numeric value and calculate BMR
    if user_sex == "Male":
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) + 5
    else:
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) - 161
    
    daily_bmr = BMR * 1.2
    return jsonify({"BMR": daily_bmr})

# Route to calculate daily calories from user data
@recommender.route("/calculate_daily_calories", methods=['POST'])
def calculate_daily_calories():
    # Recieve user data from the frontend
    data = request.get_json()
    daily_bmr = data.get("daily_bmr")
    activity_level = data.get("activity_level")
    
    # Check for no bmr or activity level conditions
    if daily_bmr is None or activity_level is None:
        return jsonify({"error": "Missing required parameters"}), 400

    # Multiply BMR for activity level measures
    activity_multipliers = {1: 1.05, 2: 1.15, 3: 1.30, 4: 1.45, 5: 1.585}
    daily_cal = daily_bmr * activity_multipliers.get(activity_level, 1.2)
    
    return jsonify({"daily_calories": daily_cal})

@recommender.route("/")
def index():
    return render_template("meal-recommender.html")

# Time without KNN: 0.000570 seconds
# Time with KNN: 0.000311 seconds
# 45.44% improvement in time spent planning

