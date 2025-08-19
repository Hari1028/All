import pandas as pd

def merge_and_save_data(df_headers, df_proposals, output_filename, merge_on_id='ID'):
    # check if either of the input DataFrames is empty.
    if df_headers.empty or df_proposals.empty:
        print(f"Warning: One of the DataFrames is empty. Skipping save for {output_filename}.")
        return

    # --- Step 2: Merge and Save ---
    
    try:
        
        # 'how='left'': Ensures all rows from the left DataFrame (df_headers) are kept.
        final_df = pd.merge(df_headers, df_proposals, on=merge_on_id, how='left')
        final_df.to_excel(output_filename, index=False)
        print(f" Merged report saved to '{output_filename}'")
    except Exception as e:
        # ...print a helpful error message explaining what went wrong.
        print(f"ERROR: Could not save the Excel file. Reason: {e}")