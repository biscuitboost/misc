CREATE TABLE disposal_diary_records (
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
    found BOOLEAN,
    marked_for_deletion BOOLEAN,
    deleted BOOLEAN
);

-- Lookup table for folder name mappings
CREATE TABLE folder_lookup (
    tbl_name TEXT PRIMARY KEY,
    actual_folder_name TEXT
);

-- Lookup table for column name mappings
CREATE TABLE column_lookup (
    idr_col_name TEXT PRIMARY KEY,
    actual_col_name TEXT
);

-- Audit log for tracking actions on records
CREATE TABLE audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER,
    action TEXT,
    action_date TEXT,
    status TEXT,
    description TEXT,
    FOREIGN KEY(record_id) REFERENCES disposal_diary_records(record_id)
);

-- Table for storing metadata about each disposal diary processed
CREATE TABLE disposal_diary_info (
    diary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    diary_name TEXT NOT NULL,
    load_date TEXT NOT NULL,
    record_count INTEGER,
    notes TEXT
);

-- Modify the existing disposal_diary_records table to include a reference to the disposal_diary_info
ALTER TABLE disposal_diary_records ADD COLUMN diary_info_id INTEGER;
ALTER TABLE disposal_diary_records ADD FOREIGN KEY (diary_info_id) REFERENCES disposal_diary_info(diary_id);
