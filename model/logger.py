import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder

# Load the data
nutrients_data = pd.read_csv("datasets/foodstruct_nutritional_facts.csv")

# Process the data
nutrients_data_df = pd.DataFrame(nutrients_data)

# Replace all important external features with NaN values to mean values
nutrients_data_df['Calcium'].fillna(nutrients_data_df['Calcium'].mean(), inplace=True)
nutrients_data_df['Cholesterol'].fillna(nutrients_data_df['Cholesterol'].mean(), inplace=True)
nutrients_data_df['Fiber'].fillna(nutrients_data_df['Fiber'].mean(), inplace=True)
nutrients_data_df['Iron'].fillna(nutrients_data_df['Iron'].mean(), inplace=True)
nutrients_data_df['Magnesium'].fillna(nutrients_data_df['Magnesium'].mean(), inplace=True)
nutrients_data_df['Net carbs'].fillna(nutrients_data_df['Net carbs'].mean(), inplace=True)
nutrients_data_df['Saturated Fat'].fillna(nutrients_data_df['Saturated Fat'].mean(), inplace=True)
nutrients_data_df['Sodium'].fillna(nutrients_data_df['Sodium'].mean(), inplace=True)
nutrients_data_df['Trans Fat'].fillna(nutrients_data_df['Trans Fat'].mean(), inplace=True)

if __name__ == "__main__":

    food_log = {}
    total_calories = 0

    # Continuously allow user to enter food until done
    while True:
        food = input("Enter a food to track (or type 'exit' to quit): ").strip()
        if food.lower() == "exit": # Break out if user is done entering foods
            break

        # Fix the string matching issue
        matching_rows = nutrients_data_df[nutrients_data_df['Food Name'].str.contains(food, case=False, na=False)]

        # Display all rows with desired user food
        if not matching_rows.empty:

            valid_choices = {}
            for i, (index, row) in enumerate(matching_rows.iterrows(), start=1):
                print(f"{i}. {row['Food Name']}") # Print the food name
                print(f"Calories(kcal): {row['Calories']}\n") # Print the food calorie count
                valid_choices[i] = row

            while True:
                try:
                    # Allow user to select which food they will log
                    selection = input("\nEnter which food you want to log (or type 'exit' to quit): ").strip()
                    if selection.lower() == 'exit':
                        break
                    
                    selection = int(selection)
                    if selection in valid_choices:
                        selected_food = valid_choices[selection]
                        food_name = selected_food['Food Name']
                        food_cals = selected_food['Calories']
                        food_log[food_name] = food_cals
                        total_calories += food_cals
                        print(f"You added #{selection} - {food_name} to your log.")
                        print(f"\nCurrent food log:\n{food_log}")
                        print(f"Total Calories Today: {total_calories} kcal")
                    else:
                        print("Invalid selectio. Please enter a valid food choice.")
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
                except Exception as e:
                    print(f"Error: {e}")
        else:
            print("Food not found.")
