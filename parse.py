import sys
import datetime
from db_manager import execute_query, check_diary_name_exists

def validate_header_and_footer(header, footer, record_count):
    """Validate the file header and footer."""
    # Implement validation logic based on the project requirements
    return True

def insert_disposal_diary_info(diary_name, record_count):
    """Insert metadata about a disposal diary and return its ID, or handle duplicates."""
    # Check if the diary name already exists
    if check_diary_name_exists(diary_name):
        print(f"Diary name '{diary_name}' already exists. Exiting to prevent duplicates.")
        sys.exit(1)  # Exit the script to prevent further processing
    
    load_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    insert_query = """INSERT INTO disposal_diary_info (diary_name, load_date, record_count) VALUES (?, ?, ?);"""
    diary_id = execute_query(insert_query, (diary_name, load_date, record_count))
    return diary_id
    
def parse_disposal_diary(file_path):
    """Parse the disposal diary file and load records into the database."""
    try:
        with open(file_path, 'r') as file:
            records = file.read().split('\n')
            header = records[0]
            footer = records[-1]
            content = records[1:-1]

            # Extract diary name from header
            diary_name = header.split(',')[1] if ',' in header else 'Unknown'

            # Validate header and footer
            if not validate_header_and_footer(header, footer, len(content)):
                raise ValueError("Header or footer validation failed.")

            # Insert disposal diary info and get diary_id
            diary_id = insert_disposal_diary_info(diary_name, len(content))

            for record in content:
                fields = record.split('\x01')
                # Extend the tuple with diary_id before inserting
                fields_tuple = tuple(fields[:11]) + (diary_id,)
                insert_query = """INSERT INTO disposal_diary_records (disposal_diary_id, gdp_tnt, rec_typ_id, platfrm, disposal_ind, disposal_run_dt, tbl_name, idr_typ, idr_col_name, idr_value, juris, diary_info_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                execute_query(insert_query, fields_tuple)

            print(f"{len(content)} records processed and linked to diary ID {diary_id} successfully.")

    except Exception as e:
        print(f"Error processing disposal diary file: {e}")

if __name__ == "__main__":
    # Example usage
    parse_disposal_diary('path_to_your_disposal_diary_file.csv')
