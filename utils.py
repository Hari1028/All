# utils.py
# This file contains reusable "helper" or "utility" functions. The main purpose
# is to hold code that can be shared by multiple scripts, avoiding duplication.
# In this case, it handles the final step of merging and saving data.

# Import the pandas library, which is essential for working with DataFrames.
# We use 'pd' as a standard, short alias for pandas.
import pandas as pd

def merge_and_save_data(df_headers, df_proposals, output_filename, merge_on_id='ID'):
    """
    A common utility function to merge header and proposal DataFrames
    and save them to an Excel file.

    Args:
        df_headers (pd.DataFrame): The DataFrame with company header info.
        df_proposals (pd.DataFrame): The DataFrame with proposal details.
        output_filename (str): The name for the final Excel file.
        merge_on_id (str): The column name to join the two DataFrames on.
                           Defaults to 'ID'.
    """
    # --- Step 1: Safety Check ---
    # Before proceeding, check if either of the input DataFrames is empty.
    # This prevents errors from trying to merge nothing.
    if df_headers.empty or df_proposals.empty:
        # Print a warning message and exit the function if data is missing.
        print(f"⚠️ Warning: One of the DataFrames is empty. Skipping save for {output_filename}.")
        return

    # --- Step 2: Merge and Save ---
    # Use a try...except block for robust error handling. If anything fails
    # inside the 'try' block, the program will print an error instead of crashing.
    try:
        # Merge the two DataFrames into one.
        # 'on=merge_on_id': Specifies the common column ('ID') to link the rows.
        # 'how='left'': Ensures all rows from the left DataFrame (df_headers) are kept.
        # For each company header, it finds and attaches all matching proposal rows.
        final_df = pd.merge(df_headers, df_proposals, on=merge_on_id, how='left')
        
        # Save the final, merged DataFrame to an Excel file.
        # 'index=False': This is important to prevent pandas from writing the
        # DataFrame's row numbers (0, 1, 2, etc.) as the first column in the spreadsheet.
        final_df.to_excel(output_filename, index=False)
        
        # Print a success message to the console.
        print(f"✅ Success! Merged report saved to '{output_filename}'")
        
    # If any error (Exception) occurs during the try block...
    except Exception as e:
        # ...print a helpful error message explaining what went wrong.
        print(f"❌ ERROR: Could not save the Excel file. Reason: {e}")