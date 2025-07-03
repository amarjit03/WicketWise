from flask import Flask, render_template, request
import pandas as pd
import pickle
import math

app = Flask(__name__)

# Load the prediction model
# Assuming pipe.pkl is in the root directory
try:
    with open('pipe.pkl', 'rb') as f:
        pipe = pickle.load(f)
except FileNotFoundError:
    print("ERROR: pipe.pkl not found. Predictions will not be available.")
    pipe = None
except Exception as e:
    print(f"Error loading pipe.pkl: {e}")
    pipe = None

teams = sorted([
    'Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
    'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
    'Rajasthan Royals', 'Delhi Capitals'
])

cities = sorted([
    'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
    'Sharjah', 'Mohali', 'Bengaluru'
])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', teams=teams, cities=cities, prediction_results=None)

@app.route('/predict', methods=['POST'])
def predict():
    prediction_results = {}
    form_values = request.form

    try:
        batting_team = request.form['batting_team']
        bowling_team = request.form['bowling_team']
        selected_city = request.form['selected_city']
        target = int(request.form['target'])
        score = int(request.form['score'])

        overs_str = request.form['overs']
        wickets_out = int(request.form['wickets'])

        # Convert overs_str (e.g., "10.2") to total balls completed
        if '.' in overs_str:
            completed_overs = int(overs_str.split('.')[0])
            completed_balls_in_over = int(overs_str.split('.')[1])
            if completed_balls_in_over > 5:
                 raise ValueError("Balls in an over cannot exceed 5.")
            balls_completed = completed_overs * 6 + completed_balls_in_over
        else:
            completed_overs = int(overs_str)
            balls_completed = completed_overs * 6

        if completed_overs < 0 or completed_overs > 20:
            raise ValueError("Overs must be between 0 and 20.")
        if score < 0:
             raise ValueError("Score cannot be negative.")
        if target <= 0:
            raise ValueError("Target must be a positive number.")
        if wickets_out < 0 or wickets_out > 10:
            raise ValueError("Wickets must be between 0 and 10.")
        if batting_team == bowling_team:
            raise ValueError("Batting and Bowling teams cannot be the same.")


        runs_left = target - score
        balls_left = 120 - balls_completed
        wickets_remaining = 10 - wickets_out

        if runs_left < 0: # Batting team already won
            runs_left = 0

        if balls_left == 0 and runs_left > 0 : # Bowling team won if balls over and runs still left
             prediction_results = {
                'batting_team': batting_team,
                'bowling_team': bowling_team,
                'win_prob': 0.0,
                'loss_prob': 1.0,
                'error': None
            }
             return render_template('index.html', teams=teams, cities=cities, prediction_results=prediction_results, form_values=form_values)


        crr = (score * 6) / balls_completed if balls_completed > 0 else 0
        rrr = (runs_left * 6) / balls_left if balls_left > 0 else float('inf') if runs_left > 0 else 0

        prediction_results.update({
            'batting_team': batting_team,
            'bowling_team': bowling_team,
        })


        if pipe is None:
            prediction_results['error'] = "Prediction model (pipe.pkl) is not loaded. Cannot make predictions."
        else:
            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city': [selected_city],
                'runs_left': [runs_left],
                'balls_left': [balls_left],
                'wickets': [wickets_remaining], # Model expects wickets remaining
                'total_runs_x': [target],
                'crr': [crr],
                'rrr': [rrr]
            })

            result = pipe.predict_proba(input_df)
            loss_prob = result[0][0]
            win_prob = result[0][1]

            prediction_results.update({
                'win_prob': win_prob,
                'loss_prob': loss_prob,
                'error': None
            })

    except ValueError as ve:
        prediction_results['error'] = f"Invalid input: {ve}"
    except Exception as e:
        prediction_results['error'] = f"An error occurred: {e}"
        # Log the full error for debugging
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()


    return render_template('index.html', teams=teams, cities=cities, prediction_results=prediction_results, form_values=form_values)


if __name__ == '__main__':
    app.run(debug=True)
