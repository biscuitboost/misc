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
    table, last_updated = load_csv_data(env)
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())

@app.route('/uat')
def index_uat():
    env = 'UAT'
    table, last_updated = load_csv_data(env)
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())

@app.route('/prod')
def index_prod():
    env = 'PROD'
    table, last_updated = load_csv_data(env)
    return render_template('index.html', table=table, last_updated=last_updated, ENV=env.upper())


def load_csv_data(env):
    args = setup_args(env)
    DATA_FILE=(args.DATA_FILE)
    directory_list=(args.directory_list)
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)  # Load the analysis results from the file
        df = df.fillna('')  # Replace NaN values with an empty string

        # Get the last modified date of the file
        last_updated = datetime.fromtimestamp(os.path.getmtime(args.DATA_FILE)).strftime('%Y-%m-%d %H:%M:%S')
    else:
        filename = save_analysis_results(DATA_FILE, directory_list)
        if filename:
            df = pd.read_csv(filename)  # Load the analysis results from the file
            df = df.fillna('')  # Replace NaN values with an empty string

            # Get the last modified date of the file
            last_updated = datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            df = pd.DataFrame()
            last_updated = "No data available"
    return df.to_html(classes='data', header="true", escape=False), last_updated

@app.route('/download')
def download():
    env = request.args.get('ENV')
    if not env:
        env = 'SIT'
    args = setup_args(env.upper())

    df = run_analysis(args.directory_list)  # Run analysis and get DataFrame
    filepath = args.xlsx_export
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

