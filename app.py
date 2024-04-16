from flask import Flask, render_template, send_file
from directory_analysis import run_analysis, setup_args  # make sure this import is correct
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os

app = Flask(__name__)
scheduler = BackgroundScheduler()
DATA_FILE="~directory_analysis.tmp"

# Save the analysis results to a CSV file
def save_analysis_results(filename):
    args = setup_args()
    df = run_analysis(args.inclusion_file)
    # check size of df
    if len(df) > 0:
        df.to_csv(filename, index=False)  # Save results to CSV
        return filename
    else:
        print('No data to save')
        return None

# Scheduled task to run the analysis every 15 minutes
scheduler.add_job(func=save_analysis_results, args=[DATA_FILE], trigger="interval", minutes=10)
scheduler.start()

@app.route('/')
def index():
    args = setup_args()  # Setup and retrieve arguments
    #df = run_analysis(args.inclusion_file)  # Pass the correct string attribute for the file path
    # if csv file exists, load it
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)  # Load the analysis results from the file
        df = df.fillna('')  # Replace NaN values with an empty string
        return render_template('index.html', table=df.to_html(classes='data', header="true"))
    else:
        filename = save_analysis_results(DATA_FILE)
        if filename:
            df = pd.read_csv(filename)  # Load the analysis results from the file
            df = df.fillna('')  # Replace NaN values with an empty string
            return render_template('index.html', table=df.to_html(classes='data', header="true"))
        else:
            return "No analysis results available."



@app.route('/download')
def download():
    args = setup_args()
    df = run_analysis(args.inclusion_file)  # Run analysis and get DataFrame
    filepath = 'analysis_results.xlsx'
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

