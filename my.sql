-- Table for storing metadata about each disposal diary processed
CREATE TABLE disposal_diary_info (
    diary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    diary_name TEXT NOT NULL,
    load_date TEXT NOT NULL,
    record_count INTEGER,
    notes TEXT, 
    status INTEGER)
    
-- Table for storing disposal diary records, updated to include a reference to the disposal_diary_info
CREATE TABLE IF NOT EXISTS disposal_diary_records (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    disposal_diary_id TEXT,
    gdp_tnt TEXT,
    rec_typ_id INTEGER,
    platfrm TEXT,
    disposal_ind TEXT,
    disposal_run_dt TEXT,
    tbl_name TEXT,
    idr_typ TEXT,
    idr_col_name TEXT,
    idr_value TEXT,
    idr_sta_dt TEXT,
    idr_end_dt TEXT,
    juris TEXT,
    found BOOLEAN DEFAULT 0,
    marked_for_deletion BOOLEAN DEFAULT 0,
    deleted BOOLEAN DEFAULT 0,
    diary_info_id INTEGER,
    FOREIGN KEY(diary_info_id) REFERENCES disposal_diary_info(diary_id)
);

-- Lookup table for folder name mappings
CREATE TABLE IF NOT EXISTS folder_lookup (
    tbl_name TEXT PRIMARY KEY,
    actual_folder_name TEXT
);

-- Lookup table for column name mappings
CREATE TABLE IF NOT EXISTS column_lookup (
    idr_col_name TEXT PRIMARY KEY,
    actual_col_name TEXT
);

-- Audit log for tracking actions on records
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    action TEXT,
    action_date TEXT,
    status TEXT,
    description TEXT,
    FOREIGN KEY(record_id) REFERENCES disposal_diary_records(record_id)
);
