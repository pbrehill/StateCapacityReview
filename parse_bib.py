#!/usr/bin/env python3

import sys
import csv
import bibtexparser

def bibtex_to_csv(bib_file_path, csv_file_path):
    """
    Reads a BibTeX file and writes a CSV file with all the fields found.

    :param bib_file_path: path to the .bib file
    :param csv_file_path: path to the output .csv file
    """
    # Read the bib file
    with open(bib_file_path, 'r', encoding='utf-8') as bib_file:
        bib_database = bibtexparser.load(bib_file)
    
    # Collect all possible fields from all bib entries
    all_fields = set()
    for entry in bib_database.entries:
        for field_name in entry.keys():
            all_fields.add(field_name)
    
    # Sort fields for consistent ordering (optional)
    fieldnames = sorted(all_fields)
    
    # Write to CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for entry in bib_database.entries:
            # Write each entry (DictWriter will match keys to columns)
            writer.writerow(entry)

def main():
    """
    Usage: python bib_to_csv.py input.bib output.csv
    """
    if len(sys.argv) < 3:
        print("Usage: python bib_to_csv.py <input.bib> <output.csv>")
        sys.exit(1)
    
    bib_file_path = sys.argv[1]
    csv_file_path = sys.argv[2]
    
    # Convert the BibTeX file to CSV
    bibtex_to_csv(bib_file_path, csv_file_path)
    print(f"Successfully created CSV file: {csv_file_path}")

if __name__ == "__main__":
    main()

