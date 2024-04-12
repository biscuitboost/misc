import os
import sys
import datetime
import pandas as pd
from collections import Counter

def file_age_days(filetime):
    return (datetime.datetime.now() - datetime.datetime.fromtimestamp(filetime)).days

def load_exclusions(file_path):
    with open(file_path, 'r') as file:
        return {line.strip() for line in file if line.strip()}

def analyze_directory(directory):
    filetype_counts = Counter()
    total_folders = 0
    total_files = 0
    older_than_6_months = 0
    from_last_24_hours = 0
    file_ages = []

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
                file_ages.append(file_age)  # Store age of each file
                if file_age > 180:
                    older_than_6_months += 1
                if file_age < 1:
                    from_last_24_hours += 1
            except Exception as e:
                print(f"Error getting stats for file {file_path}: {e}")

    return {
        'Directory': directory,
        'Total Folders': total_folders,
        'Total Files': total_files,
        'Files > 6 Months': older_than_6_months,
        'Files < 24 Hours': from_last_24_hours,
        'Average File Age (Days)': round(sum(file_ages) / len(file_ages), 2) if file_ages else 0,
        **dict(filetype_counts)
    }

def main(top_directory, output_excel, exclusion_file):
    exclusions = load_exclusions(exclusion_file)
    results = []

    for child in next(os.walk(top_directory))[1]:
        child_path = os.path.join(top_directory, child)
        if child_path not in exclusions:
            results.append(analyze_directory(child_path))

    df = pd.DataFrame(results)
    df.fillna(0, inplace=True)  # Replace NaNs with 0s for file types not present

    # Save to Excel with formatting enhancements
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Directory Analysis')
        workbook = writer.book
        worksheet = writer.sheets['Directory Analysis']
        
        # Freeze the top row and enable filters
        worksheet.freeze_panes = 'A2'
        worksheet.auto_filter.ref = worksheet.dimensions
        
        # Setting column width (optional)
        for column_cells in worksheet.columns:
            length = max(len(as_text(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length

def as_text(value):
    """Helper function to deal with None in cell values"""
    if value is None:
        return ""
    return str(value)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <top_level_directory> <output_excel> <exclusion_file>")
        sys.exit(1)

    top_directory = sys.argv[1]
    output_excel = sys.argv[2]
    exclusion_file = sys.argv[3]
    if not os.path.isdir(top_directory):
        print("Provided path is not a directory")
        sys.exit(1)

    main(top_directory, output_excel, exclusion_file)
