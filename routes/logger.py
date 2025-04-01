import pandas as pd
from flask import Blueprint, render_template, request, jsonify

# Initialize blueprint for logger
logger = Blueprint("logger", __name__)

# Load the data and select only desired columns
nutrients_data = pd.read_csv("datasets/large_food_nutrition_dataset.csv", 
                             usecols=['Name', 'Calories', 'Fat (g)', 
                                      'Protein (g)', 'Carbohydrate (g)', 
                                      'Sugars (g)', 'Fiber (g)', 'Cholesterol (mg)', 
                                      'Saturated Fats (g)', 'Trans Fatty Acids (g)', 
                                      'Sodium (mg)'])

# Process the data
nutrients_data_df = pd.DataFrame(nutrients_data)

# Rename all columns to match consisten and simple values
nutrients_data_df.rename(columns={'Name': 'Food Name',
                                  'Fat (g)': 'Fats',
                                  'Protein (g)': 'Protein',
                                  'Carbohydrate (g)': 'Carbs',
                                  'Sugars (g)': 'Sugars',
                                  'Fiber (g)': 'Fiber',
                                  'Cholesterol (mg)': 'Cholesterol',
                                  'Saturated Fats (g)': 'Saturated Fats',
                                  'Trans Fatty Acids (g)': 'Trans Fats',
                                  'Sodium (mg)': 'Sodium'}, inplace=True)

# Replace all important external features with NaN values to mean values
nutrients_data_df.fillna({'Cholesterol': nutrients_data_df['Cholesterol'].mean()}, inplace=True)
nutrients_data_df.fillna({'Fiber': nutrients_data_df['Fiber'].mean()}, inplace=True)
nutrients_data_df.fillna({'Saturated Fats': nutrients_data_df['Saturated Fats'].mean()}, inplace=True)
nutrients_data_df.fillna({'Sodium': nutrients_data_df['Sodium'].mean()}, inplace=True)
nutrients_data_df.fillna({'Sugars': nutrients_data_df['Sugars'].mean()}, inplace=True)
nutrients_data_df.fillna({'Trans Fats': nutrients_data_df['Trans Fats'].mean()}, inplace=True)

# Selection option column for food search
options = nutrients_data_df['Food Name'].astype(str).tolist()

# Connect flask routes
@logger.route("/")
def index():
    return render_template("nutrition.html")

# Route to search for the food and return the found list
@logger.route("/search")
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return jsonify([])
    
    # Filter options as user inputs text
    results = [option for option in options if query in option.lower()]
    return jsonify(results[:20]) # Limits to 20 results

# Route the to the food entries
@logger.route("log_food", methods=['POST'])
def log_food():
    # Assign values from frontend inputs
    food_name = jsonify.json.get('food_name')
    grams = jsonify.json.get('grams')

    # Match the food name input to the correct dataset value
    matching_rows = nutrients_data_df[nutrients_data_df['Food Name'].str.contains(food_name, case=False, na=False)]

    # Check for error in locating food
    if matching_rows.empty:
        return jsonify({"error": "Food not found"}), 404
    
    # Select first matching food from search
    selected_food = matching_rows.iloc[0]
    grams_ratio = grams / 100

    # Extract and asign components of selected food
    food_name = selected_food['Food Name']
    food_cals = selected_food['Calories'] * grams_ratio # Adjust the calories based on grams
    food_protein = selected_food['Protein'] * grams_ratio # Adjust the protein based on grams
    food_carbs = selected_food['Carbs'] * grams_ratio # Adjust the carbs based on grams
    food_fats = selected_food['Fats'] * grams_ratio # Adjust the fat based on grams

    # Return the calculated values
    return jsonify({
        "food_name": selected_food['Food Name'],
        "calories": round(food_cals, 2),
        "protein": round(food_protein, 2),
        "carbs": round(food_carbs, 2),
        "fats": round(food_fats, 2),
        "grams": grams
    })

# Initialize the food log
food_log = []

# Get the food log based on user rinput
@logger.route("/get_food_log", methods=['POST'])
def get_food_log():
    return jsonify(food_log)

# Clear the food log when needed
@logger.route("/clear_food_log", methods=["POST"])
def clear_food_log():
    global food_log
    food_log = []  # Clear the food log
    return jsonify({"message": "Food log cleared"})

# Flask app execution
def logger_main():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(logger, url_prefix="/logger")

    app.run(debug=True)


# mae: 41.61904761904762 rmse: 71.62451695174934 mape: 13.25802978184093

