from flask import Flask, render_template, send_file
from directory_analysis import run_analysis, setup_args  # make sure this import is correct

app = Flask(__name__)

@app.route('/')
def index():
    args = setup_args()  # Setup and retrieve arguments
    df = run_analysis(args.inclusion_file)  # Pass the correct string attribute for the file path
    df = df.fillna('')  # Replace NaN values with an empty string
    return render_template('index.html', table=df.to_html(classes='data', header="true"))

@app.route('/download')
def download():
    args = setup_args()
    df = run_analysis(args.inclusion_file)  # Run analysis and get DataFrame
    filepath = 'output.xlsx'
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

