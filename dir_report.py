import os
import sys
import datetime
import pandas as pd
from collections import Counter
import argparse
import logging

def setup_logging():
    """Setup basic configuration for logging."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def file_age_days(filetime):
    """Calculate the number of days since the file was last modified."""
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(filetime)).days

def get_folder_size(start_path):
    """Calculate the total size of all files in the directory in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError as e:
                    logging.error(f"Error accessing file size for {fp}: {e}")
    return round(total_size / (1024 * 1024), 2)  # Convert bytes to megabytes and round to two decimal places

def load_exclusions(file_path):
    """Load exclusion list from a file."""
    try:
        with open(file_path, 'r') as file:
            return {line.strip() for line in file if line.strip()}
    except FileNotFoundError:
        logging.warning(f"No exclusion file found at {file_path}. Proceeding without exclusions.")
        return set()

def analyze_directory(directory):
    """Analyze the directory for file statistics and information."""
    logging.info(f"Analyzing directory {directory}")
    filetype_counts = Counter()
    total_folders = 0
    total_files = 0
    older_than_6_months = 0
    from_last_24_hours = 0
    file_ages = []
    newest_file_age = float('inf')
    oldest_file_age = 0
    folder_size_mb = get_folder_size(directory)

    for root, dirs, files in os.walk(directory):
        total_folders += len(dirs)
        total_files += len(files)
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].strip('.')
            filetype_counts[file_extension] += 1

            try:
                file_stats = os.stat(file_path)
                file_age = file_age_days(file_stats.st_mtime)
                file_ages.append(file_age)
                newest_file_age = min(newest_file_age, file_age)
                oldest_file_age = max(oldest_file_age, file_age)
                if file_age > 180:
                    older_than_6_months += 1
                if file_age < 1:
                    from_last_24_hours += 1
            except OSError as e:
                logging.error(f"Error accessing file {file_path}: {e}")

    # Adjust for no files case
    if not file_ages:
        newest_file_age = 0
        oldest_file_age = 0

    return {
        'Directory': directory,
        'Total Folders': total_folders,
        'Total Files': total_files,
        'Folder Size (MB)': folder_size_mb,
        'Files > 6 Months': older_than_6_months,
        'Files < 24 Hours': from_last_24_hours,
        'Newest File Age (Days)': newest_file_age,
        'Oldest File Age (Days)': oldest_file_age,
        **dict(filetype_counts)
    }

def main(args):
    exclusions = load_exclusions(args.exclusion_file)
    results = []

    for child in next(os.walk(args.top_directory))[1]:
        child_path = os.path.join(args.top_directory, child)
        if child_path not in exclusions:
            results.append(analyze_directory(child_path))

    df = pd.DataFrame(results)
    df.fillna(0, inplace=True)

    with pd.ExcelWriter(args.output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description='Analyze directories for file and folder statistics.')
    parser.add_argument('top_directory', type=str, help='Top level directory to analyze')
    parser.add_argument('--output_excel', type=str, default='output.xlsx', help='Output Excel file name (default: output.xlsx)')
    parser.add_argument('--exclusion_file', type=str, default='exclusions.txt', help='File containing directories to exclude (default: exclusions.txt)')

    args = parser.parse_args()

    if not os.path.isdir(args.top_directory):
        logging.error("Provided path is not a directory")
        sys.exit(1)

    main(args)
