import re
import pandas as pd
from utils import merge_and_save_data

def parse_proposals_with_slicing(proposal_table_text, company_id):
    """
    A specialized function that parses a proposal table using line-by-line
    slicing. It is designed to correctly handle multi-line descriptions.
    """
    # Split the incoming block of text into a list of individual lines.
    lines = proposal_table_text.strip().split('\n')
    proposals_data = [] # An empty list to store the dictionaries for each proposal.

    # Loop through each line of the proposal table.
    for line in lines:
        # Skip any lines that are empty or are part of the table's header.
        if not line.strip() or "Issue No." in line or "Description" in line:
            continue

        # Use fixed-width slicing based on character positions to chop the line into columns.
        issue_no_slice = line[0:10].strip()
        description_slice = line[10:36].strip()
        proponent_slice = line[36:47].strip()
        mgmt_rec_slice = line[47:57].strip()
        vote_cast_slice = line[57:67].strip()
        for_against_slice = line[67:].strip()

        # If the 'issue_no_slice' is not empty, it's a new proposal record.
        if issue_no_slice:
            record = {
                'ID': company_id,
                'IssueNo': issue_no_slice,
                'Description': description_slice,
                'Proponent': proponent_slice,
                'MgmtRec': mgmt_rec_slice,
                'VoteCast': vote_cast_slice,
                'ForAgainstMgmt': for_against_slice
            }
            # Add the new record to our list of proposals.
            proposals_data.append(record)
        # If 'issue_no_slice' is empty but we have a description, it's a continuation.
        elif proposals_data and description_slice:
            # Append this line's description to the 'Description' of the PREVIOUS record.
            # proposals_data[-1] refers to the last item added to the list.
            proposals_data[-1]['Description'] += ' ' + description_slice

    # Return the final list of parsed proposal data for this company.
    return proposals_data

def process_and_parse_report(raw_file_content): #It cleans the raw text, then parses out the header and proposal data into two separate DataFrames.I

    header_pattern = r'^.*?(?=____________________________________________________________________)'
    content_no_header = re.sub(header_pattern, '', raw_file_content, count=1, flags=re.DOTALL)
    # Remove the file footer (everything from the SIGNATURES section to the end).
    footer_pattern = r'<PAGE>\s+SIGNATURES.*'
    cleaned_content = re.sub(footer_pattern, '', content_no_header, flags=re.DOTALL).strip()

    
    # capture all the fields from the multi-line header block.
    header_pattern_re = re.compile(
        r"^(?P<CompanyName>.*?)\n"
        r"Ticker\s+Security ID:\s+Meeting Date\s+Meeting Status\n"
        r"(?P<Ticker>\S*)\s+CUSIP\s+(?P<SecurityID>\S*)\s+(?P<MeetingDate>\S*)\s+(?P<MeetingStatus>\S*)\n"
        r"Meeting Type\s+Country of Trade\n"
        r"(?P<MeetingType>\S*)\s+(?P<CountryOfTrade>.*?)\s*$", re.MULTILINE
    )
    # Split the cleaned text into a list of "blocks", one for each company.
    company_blocks = cleaned_content.split('____________________________________________________________________')
    all_headers_data, all_proposals_data = [], []
    company_id_counter = 0 # Initialize a counter for unique company IDs.

    # Loop through each company block to extract its data.
    for block in company_blocks:
        block = block.strip()
        if not block: continue # Skip any empty blocks.

        company_id_counter += 1 # Increment the ID for the new company.

        # Use the regex to find and extract the header data for this block.
        header_match = header_pattern_re.search(block)
        if header_match:
            # .groupdict() returns a clean dictionary of the captured data.
            header_data = header_match.groupdict()
            header_data['ID'] = company_id_counter # Add the unique ID.
            all_headers_data.append(header_data)

        # Isolate the proposal table text from the bottom of the block.
        proposal_table_text = re.search(r'For/Against\s+Mgmt\n(.*?)$', block, re.DOTALL)
        if proposal_table_text:
            # Call our specialized slicing function to parse the table.
            proposals = parse_proposals_with_slicing(proposal_table_text.group(1), company_id_counter)
            # Add the returned list of proposals to our master list.
            all_proposals_data.extend(proposals)

    # Convert the lists of dictionaries into pandas DataFrames.
    df_headers = pd.DataFrame(all_headers_data)
    df_proposals = pd.DataFrame(all_proposals_data)
    
    print(f"Found {len(df_headers)} company headers in file 2.")
    print(f"Found {len(df_proposals)} proposals in file 2.")
    
    # Return the two completed DataFrames.
    return df_headers, df_proposals

def main():
    input_filename = "txt_2.txt"
    output_filename = "file2_output.xlsx"
    print(f"Starting parser for {input_filename} ")

    try:
        # Read the raw text file into memory.
        with open(input_filename, 'r', encoding='utf-8') as f:
            raw_content = f.read()
    except FileNotFoundError:
        print(f"ERROR: Input file '{input_filename}' not found.")
        return

    # Step 1: Call the main processing function to get the two DataFrames.
    df_headers, df_proposals = process_and_parse_report(raw_content)
    
    # Step 2: Call the shared utility function to merge and save the data.
    merge_and_save_data(df_headers, df_proposals, output_filename)

# Standard entry point for a Python script.
if __name__ == "__main__":
    main()