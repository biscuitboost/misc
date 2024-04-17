import os
import pandas as pd
import datetime

def file_age_days(filetime):
    """Calculate the number of days since the file was last modified."""
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(filetime)).days

def get_folder_size(directory):
    """Calculate the total size of all files in the directory in MB."""
    total_size = 0
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            try:
                total_size += os.path.getsize(filepath)
            except OSError as e:
                print(f"Error accessing file size for {filepath}: {e}")
    return round(total_size / (1024 * 1024), 2)  # Convert bytes to megabytes

def load_directories(directory_list):
    """Load directories from a CSV file."""
    directories = pd.read_csv(directory_list)
    return directories.to_dict('records')

def analyze_filetypes(directory):
    """Analyze the directory for file statistics at the top level only."""
    filetypes = {}
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            filetype = os.path.splitext(filename)[1]
            if filetype == '':
                filetype = 'no_ext'
            filetypes[filetype] = filetypes.get(filetype, 0) + 1
    return filetypes

def analyze_directory(directory):
    """Analyze the directory for file statistics at the top level only."""
    total_files = 0
    newest_file_age = float('inf')
    oldest_file_age = 0
    folder_size_mb = get_folder_size(directory)
    filetypes = analyze_filetypes(directory)  # Call analyze_filetypes

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            total_files += 1
            try:
                file_stats = os.stat(filepath)
                file_age = file_age_days(file_stats.st_mtime)
                newest_file_age = min(newest_file_age, file_age)
                oldest_file_age = max(oldest_file_age, file_age)
            except OSError as e:
                print(f"Error accessing file {filepath}: {e}")

    if total_files == 0:
        newest_file_age = 0
        oldest_file_age = 0

    result = {
        #'Directory': directory,
        'Total Files': total_files,
        'Folder Size (MB)': folder_size_mb,
        'Newest File Age (Days)': newest_file_age,
        'Oldest File Age (Days)': oldest_file_age
    }

    result.update(filetypes)  # Add filetypes to the result
    return result

def run_analysis(directory_list):
    directories = load_directories(directory_list)
    results = []
    for directory in directories:
        included_path = directory['Directory']  # Assuming 'directory' is the column name for the directory path
        if os.path.isdir(included_path):
            result = analyze_directory(included_path)
            result.update(directory)  # Add additional data from the directory
            results.append(result)
        else:
            print(f"Path is not a directory or not accessible: {included_path}")
    df = pd.DataFrame(results)

    # Reorder the columns
    config_columns = list(directories[0].keys())  # Get the column names from the config
    other_columns = [col for col in df.columns if col not in config_columns]  # Get the other column names
    df = df[config_columns + other_columns]  # Concatenate the lists and reorder the columns

    return df

# Save the analysis results to a CSV file
def save_analysis_results(filename, directory_list):
    df = run_analysis(directory_list)
    # check size of df
    if len(df) > 0:
        df.to_csv(filename, index=False)  # Save results to CSV
        return filename
    else:
        print('No data to save')
        return None

def setup_args(env='SIT'):
    """Setup arguments for the Flask call"""
    class Args:
        if env == 'SIT':
            directory_list = 'config/sit.cfg'
            DATA_FILE=".sit_dir_data.tmp"
            xlsx_export = 'analysis_results_sit.xlsx'
        elif env == 'UAT':
            directory_list = 'config/uat.cfg'
            DATA_FILE=".uat_dir_data.tmp"
            xlsx_export = 'analysis_results_uat.xlsx'
        elif env == 'PROD':
            directory_list = 'config/prod.cfg'
            DATA_FILE=".prod_dir_data.tmp"
            xlsx_export = 'analysis_results_prod.xlsx'
        else:
            directory_list = 'config/sit.cfg'  # Default to SIT
            DATA_FILE=".sit_dir_data.tmp"
            xlsx_export = 'analysis_results_sit.xlsx'
    return Args()

