import pandas as pd

# Load the data
nutrients_data = pd.read_csv("datasets/ultimate_food_data.csv")

# Process the data
nutrients_data_df = pd.DataFrame(nutrients_data)

# Remove all duplicate food names from the combined dataset
nutrients_data_df['Food Name'] = nutrients_data_df['Food Name'].str.lower()
nutrients_data_df = nutrients_data_df.drop_duplicates(subset=['Food Name'], keep='first')  # Keeps the first occurrence

# Replace all important external features with NaN values to mean values
nutrients_data_df.fillna({'Cholesterol': nutrients_data_df['Cholesterol'].mean()}, inplace=True)
nutrients_data_df.fillna({'Fiber': nutrients_data_df['Fiber'].mean()}, inplace=True)
nutrients_data_df.fillna({'Saturated Fat': nutrients_data_df['Saturated Fat'].mean()}, inplace=True)
nutrients_data_df.fillna({'Sodium': nutrients_data_df['Sodium'].mean()}, inplace=True)
nutrients_data_df.fillna({'Sugar': nutrients_data_df['Sugar'].mean()}, inplace=True)

# Running the entire program
if __name__ == "__main__":

    # Set initial empty values for food log and macros
    food_log = {}
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

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
                print(f"\n{i}. {row['Food Name']}") # Print the food name
                print(f"Calories(kcal) per 100(g): {row['Calories']}") # Print the food calorie count
                valid_choices[i] = row

            while True:
                try:
                    # Allow user to select which food they will log
                    selection = input("\nEnter which food you want to log (or type 'exit' to quit): ").strip()
                    if selection.lower() == 'exit':
                        break
                    
                    # Process the selection and display components of food
                    selection = int(selection)
                    if selection in valid_choices:
                        grams = int(input("Enter the amount you consumed (grams): "))
                        selected_food = valid_choices[selection]
                        grams_ratio = grams / 100 # Ratio the grams consumed based on 100g kcal averages
                        
                        # Extract and asign components of selected food
                        food_name = selected_food['Food Name']
                        food_cals = selected_food['Calories'] * grams_ratio # Adjust the calories based on grams
                        food_protein = selected_food['Protein'] * grams_ratio # Adjust the protein based on grams
                        food_carbs = selected_food['Carbs'] * grams_ratio # Adjust the carbs based on grams
                        food_fats = selected_food['Fats'] * grams_ratio # Adjust the fat based on grams

                        # Log the food, calories, and grams into a nested dictionary
                        food_log[food_name] = {"Calories(kcal)": food_cals, "Grams(g)": grams}

                        total_calories += food_cals # Update total calories
                        total_protein += food_protein # Update total protein
                        total_carbs += food_carbs # Update total carbs
                        total_fats += food_fats # Update total fat

                        print(f"You added {grams} of {food_name} to your log.")
                        print(f"\nCurrent food log:\n{food_log}")
                        print(f"\nTotal Calories Today: {total_calories:.2f} kcal")
                        print(f"Total Protien Intake Today: {total_protein:.2f} g")
                        print(f"Total Carb Intake Today: {total_carbs:.2f} g")
                        print(f"Total Fat Intake Today: {total_fats:.2f} g")
                    else:
                        print("Invalid selectio. Please enter a valid food choice.")
                except ValueError: # Check for input error
                    print("Invalid input. Please enter a numeric value.")
                except Exception as e: # Check for input error
                    print(f"Error: {e}")
        else:
            print("Food not found.")
