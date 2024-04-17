#app.py
from flask import Flask, render_template, send_file, request, redirect, url_for
from directory_analysis import run_analysis, setup_args, save_analysis_results 
from apscheduler.schedulers.background import BackgroundScheduler
import pandas as pd
import os
from datetime import datetime


app = Flask(__name__)
scheduler = BackgroundScheduler()

# Scheduled task to run the analysis every 15 minutes
scheduler.add_job(func=save_analysis_results, args=['.sit_dir_data.tmp', 'config/sit.cfg'], trigger="interval", minutes=10)
scheduler.add_job(func=save_analysis_results, args=['.uat_dir_data.tmp', 'config/uat.cfg'], trigger="interval", minutes=10)
scheduler.add_job(func=save_analysis_results, args=['.prod_dir_data.tmp', 'config/prod.cfg'], trigger="interval", minutes=10)
scheduler.start()

@app.route('/')
def index():
    # 301 redirect to /SIT
    return redirect(url_for('index_sit'))

@app.route('/sit')
def index_sit():
    env = 'SIT'
    args = setup_args(env.upper())
    table, last_updated = load_csv_data(args.data_file, args.directory_list)
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())

@app.route('/uat')
def index_uat():
    env = 'UAT'
    args = setup_args(env.upper())
    table, last_updated = load_csv_data(args.data_file, args.directory_list)    
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())

@app.route('/prod')
def index_prod():
    env = 'PROD'
    args = setup_args(env.upper())
    table, last_updated = load_csv_data(args.data_file, args.directory_list)
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())


def load_csv_data(data_file, directory_list):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)  # Load the analysis results from the file
        df = df.fillna('')  # Replace NaN values with an empty string

        # Get the last modified date of the file
        last_updated = datetime.fromtimestamp(os.path.getmtime(data_file)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        filename = save_analysis_results(data_file, directory_list)
        if filename:
            df = pd.read_csv(filename)  # Load the analysis results from the file
            df = df.fillna('')  # Replace NaN values with an empty string

            # Get the last modified date of the file
            last_updated = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            df = pd.DataFrame()
            last_updated = "No data available"
    return df.to_html(classes='data', header="true", escape=False), last_updated

# Download DF as an excel spreadsheet
@app.route('/download')
def download():
    env = request.args.get('env')
    args = setup_args(env.upper())

    df = run_analysis(args.directory_list)  # Run analysis and get DataFrame
    filepath = args.xlsx_export
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

