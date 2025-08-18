# parser_file_1.py
# This script is specifically designed to parse the 'appleton_npx 1 1.txt' file format.
# It uses a multi-step process to handle the file's unique structure.

import re
import pandas as pd
# Import the shared function from our utility file to handle the final merge and save.
from utils import merge_and_save_data

def create_proposals_file(input_file, temp_proposals_file):
    """
    Step 1: Isolates proposal tables from the raw file and saves them
    to a temporary file. This makes the main parsing logic simpler.
    """
    try:
        # Open the raw input file using 'latin-1' encoding to prevent errors
        # from special characters (like curly apostrophes).
        with open(input_file, 'r', encoding='latin-1') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
        return False

    # This regex pattern finds all text blocks that start with a dashed line
    # and "Prop.# Proposal", capturing everything until the next dashed line or the end tag.
    pattern = re.compile(r"(-{50,}\s+Prop\.# Proposal.*?)(?=\n\s*-{50,}|</TABLE>)", re.DOTALL)
    proposal_blocks = pattern.findall(content)

    try:
        # Write the extracted proposal blocks into a new, temporary file.
        # We use 'utf-8' for writing as it's a standard format.
        with open(temp_proposals_file, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(proposal_blocks))
        return True # Indicate success
    except IOError as e:
        print(f"Error: Could not write to the file {temp_proposals_file}, Reason: {e}")
        return False # Indicate failure

def extract_company_headers(input_file):
    """
    Step 2: Extracts the main company header information (name, ticker, etc.)
    from the raw input file using a detailed regex pattern.
    """
    # Open the raw input file again, using 'latin-1' to avoid encoding errors.
    with open(input_file, "r", encoding="latin-1") as file:
        text = file.read()

    # This single, large regex captures all the labeled fields in a company's header block.
    # It uses named capture groups like (?P<Company>...) to easily identify each piece of data.
    pattern = re.compile(
        r"\n\s*(?P<Company>[A-Z0-9 .,()&\-]+?)\s+Agenda Number:\s+(?P<Agenda>\d+).*?"
        r"Security:\s+(?P<Security>\S+).*?"
        r"Meeting Type:\s+(?P<MeetingType>.*?)\s+"
        r"Meeting Date:\s+(?P<MeetingDate>.*?)\s+"
        r"Ticker:\s+(?P<Ticker>.*?)\s+"
        r"ISIN:\s+(?P<ISIN>\S+)",
        re.DOTALL
    )
    # findall() returns a list of all matches found in the text.
    data = pattern.findall(text)
    # Define the column names for our future DataFrame.
    columns = ["Company Name", "Agenda Number", "Security", "Meeting Type", "Meeting Date", "Ticker", "ISIN"]
    # Create the DataFrame from the extracted data.
    df_headers = pd.DataFrame(data, columns=columns)
    # Add a unique ID column that we will use to merge with the proposals later.
    df_headers['IDs'] = range(1, len(df_headers) + 1)
    print("Company headers extracted from file 1.")
    return df_headers

def extract_proposals(proposals_file):
    """
    Step 3: Reads the temporary proposals file and parses it line-by-line using
    fixed-width slicing to create a "rough draft" of the proposal data.
    """
    # Read all lines from the cleaner, temporary proposal file.
    with open(proposals_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    rough_data = [] # A list to hold the raw dictionaries of proposal data.
    company_id = 0  # A counter to assign an ID to each company's set of proposals.
    JUNK_PATTERNS = ["* Management", "----", "</TABLE>"] # A list of text to ignore.

    # Loop through every line in the temporary file.
    for line in lines:
        line_clean = line.strip()
        # Skip any line that is empty or contains junk text.
        if not line_clean or any(junk in line_clean for junk in JUNK_PATTERNS):
            continue

        # Check for the two specific lines that make up the table header.
        is_header_line_1 = "Prop.#" in line and "Proposal" in line
        is_header_line_2 = line_clean.startswith("Type") and line_clean.endswith("Management")

        # If it's the first line of a header, we've found a new company's table.
        # Increment the company ID counter and skip to the next line.
        if is_header_line_1:
            company_id += 1
            continue
        # If it's the second line of the header, just skip it.
        elif is_header_line_2:
            continue
        
        # This prevents any stray lines before the first table from being processed.
        if company_id == 0:
            continue
        
        # Slice the line into columns based on fixed character positions.
        # Each slice corresponds to a column in the table.
        record = {
            'IDs': company_id,
            'Prop.#': line[0:7].strip(),
            'Proposal': line[7:58].strip(),
            'Proposal Type': line[58:72].strip(),
            'Proposal Vote': line[72:95].strip(),
            'For/Against Management': line[95:].strip()
        }
        # Add the parsed record to our list of rough data.
        rough_data.append(record)
    return rough_data

def post_process_proposals(rough_data):
    """
    Step 4: Cleans up the "rough draft" proposal data, handling multi-line descriptions
    AND the special edge case where a proposal is a list of directors.
    """
    final_data = [] # A list to hold the cleaned, final proposal records.
    # A flag to track if we are inside a "DIRECTOR" proposal.
    # Think of this like a light switch: it's off until we see the word DIRECTOR.
    is_in_director_list = False
    
    # Loop through each raw record we extracted.
    for record in rough_data:
        # If a line has a proposal number, it's a new item, so turn the switch off.
        if record['Prop.#']:
            is_in_director_list = False
        
        # If the proposal is "DIRECTOR", turn the switch on.
        if record['Prop.#'] and record['Proposal'].strip().upper() == 'DIRECTOR':
            is_in_director_list = True
            
        # If this is the very first record, just add it to our list.
        if not final_data:
            final_data.append(record)
            continue
            
        # If the line has no proposal number...
        if not record['Prop.#']:
            # ...and the "DIRECTOR" switch is on, it's a director's name.
            # Add it as a NEW row to our final data.
            if is_in_director_list:
                final_data.append(record)
            # ...and the switch is off, it's a continuation of a normal proposal's description.
            # Append the text to the PREVIOUS record's 'Proposal' field.
            else:
                final_data[-1]['Proposal'] += ' ' + record['Proposal']
        # Otherwise, it's a new proposal, so add it to the list.
        else:
            final_data.append(record)

    # Final cleanup loop to normalize text.
    for record in final_data:
        # Remove any extra spaces from the 'Proposal' description.
        record['Proposal'] = ' '.join(record.get('Proposal', '').split())
        # For the main "DIRECTOR" line, clear out other columns as they don't apply.
        if record['Proposal'].upper() == 'DIRECTOR':
            record['Proposal Type'] = ''
            record['Proposal Vote'] = ''
            record['For/Against Management'] = ''
            
    # Convert the final list of dictionaries into a DataFrame.
    df_proposals = pd.DataFrame(final_data)
    # Forward-fill the 'IDs' column to ensure all rows have the correct company ID.
    df_proposals['IDs'] = df_proposals['IDs'].ffill().astype(int)
    return df_proposals


def main():
    """
    Step 5: The main function that orchestrates the entire process, calling
    each helper function in the correct order.
    """
    # Define the file names used in the script.
    input_file = "appleton_npx 1 1.txt"
    temp_proposals_file = "proposals.txt" # An intermediate file to store cleaned tables.
    output_file = "appleton_output.xlsx"
    print(f"--- Starting parser for {input_file} (with final corrected logic) ---")
    
    # Execute Step 1: Create the temporary file. If it fails, stop the script.
    if not create_proposals_file(input_file, temp_proposals_file):
        return

    # Execute Step 2: Extract the company headers.
    df_headers = extract_company_headers(input_file)
    # Execute Step 3: Extract the raw proposal data from the temporary file.
    rough_proposals = extract_proposals(temp_proposals_file)
    # Execute Step 4: Clean and process the raw proposal data.
    df_proposals = post_process_proposals(rough_proposals)
    
    # Finally, call the SHARED function from utils.py to merge the two
    # DataFrames and save the final report to Excel.
    merge_and_save_data(df_headers, df_proposals, output_file, merge_on_id='IDs')

# This is the standard entry point for a Python script. The 'main' function
# will be called only when you run this file directly from the command line.
if __name__ == "__main__":
    main()