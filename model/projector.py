import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split 
from sklearn.metrics import mean_squared_error, r2_score

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

# Get the coefficients
coef = model.coef_[0]

# Create a DataFrame for better visibility
coef_df = pd.DataFrame({
    'Feature': X.columns,
    'Coefficient': coef
})

# Sort by absolute value of the coefficient to see impact
coef_df['Abs_Coefficient'] = coef_df['Coefficient'].abs()
coef_df = coef_df.sort_values(by='Abs_Coefficient', ascending=False)

print(coef_df)

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

# Example input data (e.g., Age=28, Gender=1, Weight=70, Height=1.75, Session Duration=1.2, Workout Frequency=4, BMI=22, Workout Type=Cardio)
new_data = pd.DataFrame([[25, 0, 67, 1.65, 1, 6, 25, 0]], 
                        # Make sure the values are in the same order and have the same number of features as the data used to train the model.
                        columns=['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Session_Duration (hours)', 'Workout_Frequency (days/week)', 'BMI', 'Workout_Type'])

# Scale the new input data using the same scaler as the training data
new_data_scaled = X_scaler.transform(new_data)

# Predict the calorie burn for this new data point
predicted_calories = model.predict(new_data_scaled)

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

# Assign user features
age = new_data['Age'].iloc[0]
sex = "M" if new_data['Gender'].iloc[0] == 1 else "F"
height = float(new_data['Height (m)'].iloc[0] * 100)
weight = float(new_data['Weight (kg)'].iloc[0])

def projector_main():

    # Assign workout type based on data
    if new_data['Workout_Type'].iloc[0] == 0:
        workout_type = "Cardio"
    elif new_data['Workout_Type'].iloc[0] == 1:
        workout_type = "HIIT"
    elif new_data['Workout_Type'].iloc[0] == 2:
        workout_type = "Strength"
    else:
        workout_type = "Yoga"

    # Calculate user BMR
    BMR = float(calculate_bmr(age, sex, height, weight, new_data['Workout_Frequency (days/week)'].iloc[0]))
    calories_burned_per_session = float(predicted_calories[0][0]) / 2 # For more reasonable calories burned
    daily_cal = float(BMR + calories_burned_per_session)

    # Predicted total calories for a week
    workouts_per_week = new_data['Workout_Frequency (days/week)'].iloc[0]
    weekly_calories = float(calories_burned_per_session * int(workouts_per_week))
    
    # Print the predicted result
    print("\nInfo About This Person:\n")
    print("Age:", age)
    print("Gender:", sex)
    print("Weight (kg):", weight)
    print("Height (cm):", height)
    print("Average Session Duration (min):", int((new_data['Session_Duration (hours)'].iloc[0] * 60)))
    print(f"Main Training Type: {workout_type}")
    print("Workout Freqency:", int(new_data['Workout_Frequency (days/week)'].iloc[0]), "days a week")
    print("BMI:", new_data['BMI'].iloc[0])
    print(f"\nPredicted Calories Burned Per Session: {calories_burned_per_session:.2f} kcal")
    print(f"Predicted Weekly Calories Burned (based on sessions): {weekly_calories:.2f} kcal")
    print(f"You average BMR is about: {BMR:.2f} kcal")
    print(f"Your maintance calories are about: {daily_cal:.2f} kcal")

    # Find calories change quantity based on time frame to reach goal weight
    while True:
        try:
            goal_weight = float(input("\nWhat is your goal weight (in kg): ").strip())
            break
        except ValueError: # Request re-input if invalid user input
            print("Invalid input. Please enter a valid number.")
        
    time_frame = int(input("In how how much time would you like to reach this goal (in weeks): "))

    # Calculate caloric change per day needed to attain goal weight
    weight_diff = float(abs(goal_weight - weight))
    weight_change_weekly = float(weight_diff / time_frame)
    caloric_change_weekly = float(weight_change_weekly * 7700) # Average kcal per 1kg
    daily_caloric_change = float(caloric_change_weekly / 7) # Days in a week

    # Display caloric change needed to reach weight but check conditions and warn if change is harmful
    if goal_weight > weight:
        print("Great! So you need to go on a bulking phase.")
        goal_cal = float(daily_cal + daily_caloric_change)
        print(f"You need to eat about {goal_cal:.2f} kcal per day to reach your goal weight of {goal_weight:.2f} kg in {time_frame} weeks.")
        if float(abs(goal_cal - daily_cal)) > 1500:
            print("Would NOT recommend such a caloric surplus. Could be VERY unhealthy.")
    elif goal_weight < weight:
        goal_cal = float(daily_cal - daily_caloric_change)
        print("Great! So you need to go on a cutting phase.")
        print(f"You need to eat about {goal_cal:.2f} kcal per day to reach your goal weight of {goal_weight:.2f} kg in {time_frame} weeks.")
        if float(abs(goal_cal - daily_cal)) > 1500:
            print("Would NOT recommend such a caloric deficit. Could be VERY unhealthy.")
    else:
        print("Oh wow! You already hit your goal. Congrats!")


if __name__ == "__main__":
    projector_main()
