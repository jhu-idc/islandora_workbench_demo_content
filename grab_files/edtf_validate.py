#!/usr/bin/env python3
import re
import csv

# EDTF Validator
def is_edtf(date_str):
    # Extended patterns for common EDTF formats
    patterns = [
        r"^\d{4}$",  # YYYY
        r"^\d{4}-\d{2}$",  # YYYY-MM
        r"^\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD
        r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",  # YYYY-MM-DDTHH:MM:SS
        r"^-?\d{4}-\d{2}-\d{2}/-?\d{4}-\d{2}-\d{2}$",  # YYYY-MM-DD/YYYY-MM-DD (interval)
        r"^\d{4}-\d{2}-\d{2}~/\d{4}-\d{2}-\d{2}~$",  # YYYY-MM-DD/YYYY-MM-DD (approximate interval)
        r"^\d{4}-\d{2}-\d{2}?\d{4}-\d{2}-\d{2}?$",  # YYYY-MM-DD/YYYY-MM-DD (uncertain interval)
        r"^-?\d{4}-\d{2}-\d{2}~/-?\d{4}-\d{2}-\d{2}~?$",  # YYYY-MM-DD/YYYY-MM-DD (approximate and uncertain interval)
        r"^\d{4}S\d{2}$",  # YYYY with season (e.g., 2021-21 for Spring 2021)
        # ... (you can add more patterns as needed)
    ]
    
    for pattern in patterns:
        if re.match(pattern, date_str):
            return True
            
    return False

# CSV Validator
def validate_edtf_in_csv(file_path, column_name):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        non_compliant_dates = []
        # Debug statement to print the headers/column names
        print("Available columns:", reader.fieldnames)
        for row in reader:
            date_str = row[column_name]
            if not is_edtf(date_str):
                non_compliant_dates.append(date_str)                
    return non_compliant_dates

# To use the script:
non_compliant_dates = validate_edtf_in_csv('islandora_objects.csv', 'field_years')
if non_compliant_dates:
    print("Found non-compliant EDTF dates:", non_compliant_dates)
else:
    print("All dates in the column are EDTF compliant!")
