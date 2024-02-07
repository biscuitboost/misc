import sqlite3
from sqlite3 import Error
import argparse
import datetime
import logging
import subprocess

DATABASE_PATH = 'my.db'

def create_connection():
    """Create a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")

def execute_query(query, params=()):
    """Execute a single query against the database."""
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        log_action(f'Error executing query: {e}', 'ERROR')
    finally:
        if conn:
            conn.close()

def execute_select_query(query, params=()):
    """Execute a SELECT query and return the results."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            return cur.fetchall()
    except Error as e:
        log_action(f'Error executing SELECT query: {e}', 'ERROR')
        return None

def add_field_mapping(idr_col_name, actual_col_name):
    """Add a field mapping to the database."""
    insert_query = """INSERT INTO column_lookup (idr_col_name, actual_col_name) VALUES (?, ?);"""
    rows = execute_query(insert_query, (idr_col_name, actual_col_name))
    if rows is not None:
        log_action(f'Added {rows} field mapping: {idr_col_name} -> {actual_col_name}')
        return rows
    else:
        log_action(f'Error adding field mapping: {idr_col_name} -> {actual_col_name}', 'ERROR')
        return None


def add_ag_mapping(tbl_name, actual_folder_name):
    """Add an AG mapping to the database."""
    insert_query = """INSERT INTO folder_lookup (tbl_name, actual_folder_name) VALUES (?, ?);"""
    rows = execute_query(insert_query, (tbl_name, actual_folder_name))
    if rows is not None:
        log_action(f'Added {rows} AG mapping: {tbl_name} -> {actual_folder_name}')
        return rows
    else:
        log_action(f'Error adding AG mapping: {tbl_name} -> {actual_folder_name}', 'ERROR')
        return None
    
def get_field_mappings(idr_col_name=None):
    """Get all field mappings from the database, or only those for a specific name if provided."""
    if idr_col_name is None:
        query = "SELECT * FROM column_lookup"
        results = execute_select_query(query, ())
        log_action(f'All Field mappings: {results}')
        return results or None
    else:
        query = "SELECT actual_col_name FROM column_lookup WHERE idr_col_name = ?"
        results = execute_select_query(query, (idr_col_name,))
        log_action(f'Field mappings lookup{idr_col_name}: {results}')
        return results[0][0] if results else None
    
def get_ag_mappings(tbl_name=None):
    """Get all AG mappings from the database, or only those for a specific name if provided."""
    if tbl_name is None:
        query = "SELECT * FROM folder_lookup"
        results = execute_select_query(query, ())
        log_action(f'All AG mappings: {results}')
        return results or None
    else:
        query = "SELECT actual_folder_name FROM folder_lookup WHERE tbl_name = ?"
        results = execute_select_query(query, (tbl_name,))
        log_action(f'AG mappings lookup{tbl_name}: {results}')
        return results[0][0] if results else None
    
def delete_field_mapping(idr_col_name):
    """Delete a field mapping from the database."""
    delete_query = "DELETE FROM column_lookup WHERE idr_col_name = ?"
    rows = execute_query(delete_query, (idr_col_name,))
    if rows is not None:
        log_action(f'Deleted {rows} field mapping: {idr_col_name}')
        return rows
    else:
        log_action(f'Error deleting field mapping: {idr_col_name}', 'ERROR')
        return None

def delete_ag_mapping(tbl_name):
    """Delete an AG mapping from the database."""
    delete_query = "DELETE FROM folder_lookup WHERE tbl_name = ?"
    rows = execute_query(delete_query, (tbl_name,))
    if rows is not None:
        log_action(f'Deleted {rows} AG mapping: {tbl_name}')
        return rows
    else:
        log_action(f'Error deleting AG mapping: {tbl_name}', 'ERROR')
        return None

def check_correct_num_columns(fields):
    """Check if the correct number of columns are present."""
    if len(fields) != 13:
        log_action(f'Incorrect number of columns: {len(fields)}', 'ERROR')
        return False
    return True

def view_disposal_diaries():
    """View all disposal diaries."""
    query = "SELECT * FROM disposal_diary_info"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Error as e:
        log_action(f'Error retrieving diaries: {e}', 'ERROR')
    finally:
        if conn:
            conn.close()

def get_disposal_diary_records():
    """Retrieve all records for current disposal diary.
    ensure status = 0 and return an error if multiple or no diaries are found.
    return data in a dictionary format
    """
    query = "SELECT * FROM disposal_diary_info WHERE status = 0"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        if len(rows) == 1:
            diary_id = rows[0][0]
            diary_name = rows[0][1]
            query = "SELECT * FROM disposal_diary_records WHERE diary_info_id = ?"
            cur.execute(query, (diary_id,))
            records = cur.fetchall()
            return {'diary_id': diary_id
                    ,'diary_name': diary_name
                    ,'records': records}
        elif len(rows) > 1:
            log_action(f'Error retrieving diary records: Multiple diaries found', 'ERROR')
            return None
        else:
            log_action(f'Error retrieving diary records: No diaries found', 'ERROR')
            return None
    except Error as e:
        log_action(f'Error retrieving diary records: {e}', 'ERROR')
    finally:
        if conn:
            conn.close()


def delete_disposal_diary(diary_id):
    """Delete a disposal diary and its records."""
    delete_info_query = "DELETE FROM disposal_diary_info WHERE diary_id = ?"
    delete_records_query = "DELETE FROM disposal_diary_records WHERE diary_info_id = ?"
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(delete_records_query, (diary_id,))
        cur.execute(delete_info_query, (diary_id,))
        conn.commit()
        log_action(f'Deleted diary and records for diary_id {diary_id}')
    except Error as e:
        log_action(f'Error deleting diary: {e}', 'ERROR')
    finally:
        if conn:
            conn.close()

log_filename = 'grms_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def log_action(description, level='INFO'):
    """Log actions taken by the script."""
    if level == 'INFO':
        logging.info(f'{description}')
    elif level == 'ERROR':
        logging.error(f'{description}')
    elif level == 'WARN':
        logging.warning(f'{description}')
    else:
        logging.info(f'{description}')

def validate_header_and_footer(filename, header, footer, record_count):
    """Validate the file header and footer."""
    header_prefix, _ = header.split(',', 1)
    header_name = header.split(',')[1] if ',' in header else 'Unknown'
    footer_prefix, footer_content = footer.split(',', 1)
    footer_count = int(footer_content.split(',')[1])
       
    if header_prefix != 'H':
        log_action('Header validation failed: Invalid header prefix.', 'ERROR')
        return False
    
    if footer_prefix != 'T':
        log_action('Footer validation failed: Invalid footer prefix.', 'ERROR')
        return False
    
    if footer_count != record_count:
        log_action('Footer validation failed: Invalid record count.', 'ERROR')
        return False
    else:
        log_action(f'Record count in footer ({footer_count}) matches actual content rows ({record_count}).')
    
    if filename != header_name:
        log_action(f'Header validation failed: Filename ({filename}) does not match header ({header_name}).', 'ERROR')
        return False
    
    log_action('Header and footer validation passed.')
    return True

def insert_disposal_diary_info(diary_name, record_count, status):
    """
    Insert metadata about a disposal diary and return its ID, or handle duplicates.
    """
    load_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    notes = ""
    # Ensure the number of parameters matches the placeholders in your SQL statement
    insert_query = """INSERT INTO disposal_diary_info (diary_name, load_date, record_count, notes, status) VALUES (?, ?, ?, ?, ?);"""
    
    # Corrected to include all necessary parameters
    diary_id = execute_query(insert_query, (diary_name, load_date, record_count, notes, status))
    return diary_id

def current_disposal_diary_info():
    """Get metadata about a disposal diary."""
    query = "SELECT * FROM disposal_diary_info WHERE status = 0"
    results = execute_select_query(query,)
    if results is not None and len(results) == 1:
        #log_action(f'Diary info: {results}')
        return results
    elif results is not None and len(results) > 1:
        #log_action(f'Error retrieving diary info: Multiple diaries found', 'ERROR')
        return None
    else:
        #log_action(f'Error retrieving diary info', 'ERROR')
        return None
    
def parse_disposal_diary(file_path):
    """Parse the disposal diary file and load records into the database.
    status = 0 - not processed
    status = 1 - processed successfully
    status = 2 - processed with errors
    """
    status = 0
    filename = file_path.split('/')[-1]
    try:
        with open(file_path, 'r') as file:
            records = file.read().split('\n')
            header = records[0]
            footer = records[-1]
            content = records[1:-1]
            num_rows = len(content)

            # Extract diary name from header
            diary_name = header.split(',')[1] if ',' in header else 'Unknown'

            # Validate header and footer
            if not validate_header_and_footer(filename, header, footer, num_rows):
                raise ValueError("Header or footer validation failed.")

            # Check for existing in-progress diary
            result = current_disposal_diary_info()
            if result:
                log_action(f'In-progress diary found: {result}')
                raise ValueError("An in-progress diary already exists.")
                
            
            # Check if the correct number of columns are present on all rows
            for record in content:
                fields = record.split('\\u0001')
                if not check_correct_num_columns(fields):
                    raise ValueError("Incorrect number of columns in record.")
            try:
                # Insert disposal diary info and get diary_id
                diary_id = insert_disposal_diary_info(diary_name, num_rows, status)
                log_action(f'Inserted diary info for diary_id {diary_id}')
                for record in content:
                    fields = record.split('\\u0001')
                    # Extend the tuple with diary_id before inserting
                    fields_tuple = tuple(fields[:13]) + (diary_id,)
                    insert_query = """INSERT INTO disposal_diary_records (disposal_diary_id, gdp_tnt, rec_typ_id, platfrm, disposal_ind, disposal_run_dt, tbl_name, idr_typ, idr_col_name, idr_value, idr_sta_dt, idr_end_dt, juris,diary_info_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
                    execute_query(insert_query, fields_tuple)
                log_action(f'Inserted {num_rows} records for diary_id {diary_id}')
            except Exception as e:
                log_action(f'Processing records for diary_id {diary_id} failed - cleaning up', 'ERROR')
                if diary_id:
                    delete_disposal_diary(diary_id)
                    log_action(f'Deleted diary and records for diary_id {diary_id}')
                    

    except Exception as e:
        log_action(f'Error processing disposal diary file: {e}', 'ERROR')

def check_records_exist():
    """Check if diary records exist in CMOD.
    update found flag to 1 in disposal_diary_records"""
    diary_data = get_disposal_diary_records()
    if diary_data:
        diary_id = diary_data['diary_id']
        diary_name = diary_data['diary_name']
        records = diary_data['records']
        log_action(f'Loaded diary found: {diary_name} with {len(records)} records')
        for record in records:
            
            tbl_name = record[7]
            idr_col_name = record[9]
            idr_value = record[10]

            application_group = get_ag_mappings(tbl_name)
            field_name = get_field_mappings(idr_col_name)
            field_value = idr_value

            # run CMOD arsdoc get to check if record exists
            #output = subprocess.run(['arsdoc', 'get', '-f', application_group, '-d', field_name, '-v', field_value], capture_output=True, text=True)
            output = subprocess.run(['echo', 'arsdoc', 'get', '-f', application_group, '-d', field_name, '-v', field_value], capture_output=True, text=True)
            if output.returncode == 0:
                log_action(f'Record found in CMOD: {field_name} = {field_value}')
                update_query = "UPDATE disposal_diary_records SET found = 1 WHERE diary_info_id = ? AND tbl_name = ? AND idr_col_name = ? AND idr_value = ?"
                execute_query(update_query, (diary_id, tbl_name, idr_col_name, idr_value))
            else:
                log_action(f'Record not found in CMOD: {field_name} = {field_value}')
    else:
        log_action(f'Error retrieving diary records', 'ERROR')
        return None
   

def main():
    parser = argparse.ArgumentParser(description="Disposal Diary Processor")
    # Disposal Diary functions
    parser.add_argument('--load_diary', help="Path to disposal diary file for processing.")
    parser.add_argument('--check_records_exist',  action='store_true', help="Check if diary records exist in CMOD.")
    parser.add_argument('--view_diary', action='store_true', help="View all disposal diaries.")
    parser.add_argument('--delete_diary', type=int, help="Diary ID to delete.")
   
    # Field Mapping functions
    parser.add_argument('--add_field_mapping', nargs=2, metavar=('name', 'mapped_name'), help="Mapping disposal diary field to CMOD field.")
    parser.add_argument('--view_field_mappings', action='store_true', help="View all field mappings.")
    parser.add_argument('--delete_field_mapping', help="Field mapping to delete.")
    
    # AG Mapping functions
    parser.add_argument('--add_ag_mapping', nargs=2, metavar=('name', 'mapped_name'), help="Mapping disposal diary name to CMOD AG name.")
    parser.add_argument('--view_ag_mappings', action='store_true', help="View all AG mappings.")
    parser.add_argument('--delete_ag_mapping', help="AG mapping to delete.")    
    
    args = parser.parse_args()
    if args.view_diary:
        view_disposal_diaries()
    elif args.check_records_exist:
        print(check_records_exist())
    elif args.delete_diary:
        delete_disposal_diary(args.delete_diary)
    elif args.load_diary:
        parse_disposal_diary(args.load_diary)
    elif args.add_field_mapping:
        name, mapped_name = args.add_field_mapping
        add_field_mapping(name, mapped_name)
    elif args.add_ag_mapping:
        name, mapped_name = args.add_ag_mapping
        add_ag_mapping(name, mapped_name)
    elif args.view_field_mappings:
        print(get_field_mappings())
    elif args.view_ag_mappings:
        print(get_ag_mappings())
    elif args.delete_field_mapping:
        name = args.delete_field_mapping
        delete_field_mapping(name)
    elif args.delete_ag_mapping:
        name = args.delete_ag_mapping
        delete_ag_mapping(name)
    else:
        print("No action specified. Use --help for more information.")

if __name__ == "__main__":
    main()
