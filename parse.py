import argparse
import sys
import datetime
import logging
from db_manager import execute_query, check_diary_name_exists


logging.basicConfig(filename='disposal_diary_processor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action, description):
    """Log actions taken by the script."""
    logging.info(f'{action}: {description}')

def validate_header_and_footer(header, footer, record_count):
    """Validate the file header and footer."""
    header_prefix, _ = header.split(',', 1)
    footer_prefix, footer_content = footer.split(',', 1)
    footer_count = int(footer_content.split(',')[1])
    
    if header_prefix != 'H' or footer_prefix != 'T' or footer_count != record_count:
        return False
    return True

def insert_disposal_diary_info(diary_name, record_count):
    """
    Insert metadata about a disposal diary and return its ID, or handle duplicates.
    """
    load_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Assuming 'notes' is an optional field you might want to include
    notes = "Some notes about the diary"
    
    # Ensure the number of parameters matches the placeholders in your SQL statement
    insert_query = """INSERT INTO disposal_diary_info (diary_name, load_date, record_count, notes) VALUES (?, ?, ?, ?);"""
    
    # Corrected to include all necessary parameters
    diary_id = execute_query(insert_query, (diary_name, load_date, record_count, notes))
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

def main():
    parser = argparse.ArgumentParser(description="Disposal Diary Processor")
    parser.add_argument('--file', help="Path to disposal diary file for processing.")
    parser.add_argument('--view', action='store_true', help="View all disposal diaries.")
    parser.add_argument('--delete', type=int, help="Diary ID to delete.")
    
    args = parser.parse_args()

    if args.view:
        view_disposal_diaries()
    elif args.delete:
        delete_disposal_diary(args.delete)
    elif args.file:
        parse_disposal_diary(args.file)
    else:
        print("No action specified. Use --help for more information.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    # Example usage
    parse_disposal_diary('path_to_your_disposal_diary_file.csv')
