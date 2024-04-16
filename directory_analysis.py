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

def load_inclusions(inclusion_file):
    """Load inclusions from a CSV file."""
    inclusions = pd.read_csv(inclusion_file)
    return inclusions.to_dict('records')

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

def run_analysis(inclusion_file):
    inclusions = load_inclusions(inclusion_file)
    results = []
    for inclusion in inclusions:
        included_path = inclusion['Directory']  # Assuming 'directory' is the column name for the directory path
        if os.path.isdir(included_path):
            result = analyze_directory(included_path)
            result.update(inclusion)  # Add additional data from the inclusion
            results.append(result)
        else:
            print(f"Path is not a directory or not accessible: {included_path}")
    df = pd.DataFrame(results)

    # Reorder the columns
    config_columns = list(inclusions[0].keys())  # Get the column names from the config
    other_columns = [col for col in df.columns if col not in config_columns]  # Get the other column names
    df = df[config_columns + other_columns]  # Concatenate the lists and reorder the columns

    return df

def setup_args():
    """Setup arguments for the Flask call"""
    class Args:
        inclusion_file = 'config.txt'  # Path to your inclusions file
    return Args()

