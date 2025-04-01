import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split 
from sklearn.metrics import mean_squared_error, r2_score
from flask import Blueprint, render_template, request, jsonify

# Initialize blueprint for recommender
projector = Blueprint("projector", __name__)

# Load the data
gym_members_data = pd.read_csv("datasets/gym_members_exercise_tracking.csv")

# Process the data
gym_members_data_df = pd.DataFrame(gym_members_data)

# One-hot encode all non-numeric values
label_encoder = LabelEncoder()
gym_members_data_df['Gender'] = label_encoder.fit_transform(gym_members_data_df['Gender'])
gym_members_data_df['Workout_Type'] = label_encoder.fit_transform(gym_members_data_df['Workout_Type'])

print(label_encoder.classes_)

# Select features
X = gym_members_data_df[['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Session_Duration (hours)', 'Workout_Frequency (days/week)', 'BMI', 'Workout_Type']]
y = gym_members_data_df[['Calories_Burned']]

# Split the data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Scale data
scaler = StandardScaler()
X_scaler = scaler.fit(X_train)
X_train_scaled = X_scaler.transform(X_train)
X_test_scaled = X_scaler.transform(X_test)

# Create a linear regression model and fit the data
model = LinearRegression()
model.fit(X_train_scaled, y_train)

# Make predicitions
predicition = model.predict(X_test_scaled)

# Calculate evaluation metrics
mse = mean_squared_error(y_test, predicition)
r2 = r2_score(y_test, predicition)

print(f"\nMean Squared Error: {mse:.2f}")
print(f"R² Score: {r2:.4f}")
accuracy_score = r2 * 100
print(f"This model is {accuracy_score:.2f}% accurate.")

#********TEST THE MODEL********

# Define activity factor based on workout frequency
def get_activity_factor(workout_frequency):
    if workout_frequency >= 7:
        return 1.725  # Highly active
    elif workout_frequency >= 5:
        return 1.55  # Active
    elif workout_frequency >= 3:
        return 1.375  # Moderately active
    else:
        return 1.2  # Sedentary

# Calculate the average bmr without activity level
def calculate_bmr(user_age, user_sex, user_height, user_weight, workout_frequency):
    
    # Basal Metabolic Rate (BMR) calculation based on sex and Harris-Benedict equation
    if user_sex.upper() == "M":
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) + 5
    else:
        BMR = (10 * user_weight) + (6.25 * user_height) - (5 * user_age) - 161

    # Multiply by level of activity
    activity_factor = get_activity_factor(workout_frequency)
    daily_bmr = BMR * activity_factor

    return daily_bmr

# # Assign user features
# age = new_data['Age'].iloc[0]
# sex = "M" if new_data['Gender'].iloc[0] == 1 else "F"
# height = float(new_data['Height (m)'].iloc[0] * 100)
# weight = float(new_data['Weight (kg)'].iloc[0])

@projector.route("/get_projection", methods=['POST'])
def get_projection():
    # Recieve the user data from the frontend
    data = request.get_json()
    age = data.get('user_age')
    sex = data.get('user_sex').upper()
    sex_int = 1 if sex == "Male" else 0
    height = data.get('user_height')
    weight = data.get('user_weight')
    session_duration = data.get('user_hours')
    workout_frequency = data.get('user_days')
    bmi = weight / ((height / 100) ** 2)
    workout_type = data.get('user_workout')

    user_data = pd.DataFrame([[age, sex_int, weight, (height / 100), session_duration, workout_frequency, bmi, workout_type]], columns=['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Session_Duration (hours)', 'Workout_Frequency (days/week)', 'BMI', 'Workout_Type'])

    # Scale the new input data using the same scaler as the training data
    user_data_scaled = X_scaler.transform(user_data)

    # Predict the calorie burn for this new data point
    predicted_calories = model.predict(user_data_scaled)

    # Calculate user BMR
    BMR = float(calculate_bmr(age, sex, height, weight, workout_type))
    calories_burned_per_session = float(predicted_calories[0][0]) / 2 # For more reasonable calories burned
    daily_cal = float(BMR + calories_burned_per_session)

    # Recieve goal weight and timeframe from frontend
    goal_weight = data.get('user_goal')
    time_frame = data.get('user_weeks')

    # Caculate caloric changed and goal calorie inputs
    weight_diff = abs(goal_weight - weight)
    caloric_change = (weight_diff / time_frame) * 7700 / 7
    goal_cal = daily_cal + caloric_change if goal_weight > weight else daily_cal - caloric_change

    # Return the jsonified calculated results
    return jsonify({
        "predicted_calories_burned": round(predicted_calories, 2),
        "BMR": round(BMR, 2),
        "daily_caloric_needs": round(daily_cal, 2),
        "goal_caloric_intake": round(goal_cal, 2),
        "workout_type": ["Cardio", "HIIT", "Strength", "Yoga"][workout_type]
    })

@projector.route("/")
def index():
    return render_template("workouts.html")
