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

# Select features
X = gym_members_data_df[['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Session_Duration (hours)', 'Workout_Frequency (days/week)', 'BMI']]
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

# Example input data (e.g., Age=28, Gender=1, Weight=70, Height=1.75, Session Duration=1.2, Workout Frequency=4, BMI=22)
new_data = pd.DataFrame([[28, 1, 70, 1.75, 1.2, 4, 22]], 
                        # Make sure the values are in the same order and have the same number of features as the data used to train the model.
                        columns=['Age', 'Gender', 'Weight (kg)', 'Height (m)', 'Session_Duration (hours)', 'Workout_Frequency (days/week)', 'BMI'])

# Scale the new input data using the same scaler as the training data
new_data_scaled = X_scaler.transform(new_data)

# Predict the calorie burn for this new data point
predicted_calories = model.predict(new_data_scaled)

# Print the predicted result
print("\nInfo About This Person:\n")
print("Age:", new_data['Age'].iloc[0])
print("Gender:", "Male" if new_data['Gender'].iloc[0] == 1 else "Female")
print("Weight (kg):", new_data['Weight (kg)'].iloc[0])
print("Height (cm):", (new_data['Height (m)'].iloc[0] * 100))
print("Session Duration (min):", int((new_data['Session_Duration (hours)'].iloc[0] * 60)))
print("Workout Freqency:", int(new_data['Workout_Frequency (days/week)'].iloc[0]), "days a week")
print("BMI:", new_data['BMI'].iloc[0])
print(f"\nPredicted Calories Burned: {predicted_calories[0][0]:.2f} kcal")


