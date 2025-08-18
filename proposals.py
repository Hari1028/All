# Import the 're' module, which is Python's library for regular expressions.
import re

def extract_proposals(input_file, output_file):
    """
    Finds and extracts specific "proposal" tables from a large text file
    and saves them to a new, cleaner file.

    Args:
        input_file (str): The path to the raw, unstructured text file.
        output_file (str): The path where the cleaned proposal tables will be saved.
    """
    
    # Use a try...except block to handle the case where the input file does not exist.
    try:
        # Open the input file for reading ('r') using 'utf-8' encoding.
        with open(input_file, 'r', encoding='utf-8') as f:
            # Read the entire content of the file into a single string variable.
            content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return # Exit the function if the file isn't found.

    
    # Compile the regular expression for efficiency. This is the core logic of the script.
    # It's designed to find text blocks that start with a specific header and end
    # just before the next header or an end tag.
    pattern = re.compile(
        # --- Main Capturing Group (What we want to extract) ---
        r"(-{50,}\s+Prop\.# Proposal.*?)"
        # --- Stop Condition (Positive Lookahead) ---
        r"(?=\n\s*-{50,}|</TABLE>)",
        # --- Flag ---
        re.DOTALL
    )
    
    # Use findall() to search the entire 'content' string and return a list
    # of all text blocks that match the pattern.
    proposal_blocks = pattern.findall(content)

    # Use another try...except block to handle potential errors when writing the file.
    try:
        # Open the output file for writing ('w'). This will create the file if it doesn't exist.
        with open(output_file, 'w', encoding='utf-8') as f:
            
            # Join all the extracted proposal blocks from the list into a single string,
            # separated by two newlines, and write it to the output file.
            f.write("\n\n".join(proposal_blocks))
            # Add a final separator line at the end of the file for consistency.
            f.write("\n--------------------------------------------------------------------------------------------------------------------------")

        print(f"Proposal tables extracted to '{output_file}'")
    except IOError as e:
        # If there's an issue writing the file (e.g., permissions problem), print an error.
        print(f"Error: Could not write to the file, Reason: {e}")

# This is the standard entry point for a Python script.
# The code inside this block will only run when the script is executed directly.
if __name__ == '__main__':
    # Define the name of the input file.
    input_filename = 'appleton_npx 1 1.txt'
    # Define the name of the output file.
    output_filename = 'proposals.txt'

    # Call the main function to perform the extraction.
    extract_proposals(input_filename, output_filename)