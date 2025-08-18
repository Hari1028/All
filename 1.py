import requests
import pandas as pd
import json
import time 

# --- Configuration ---
API_URL = "https://api.openbrewerydb.org/v1/breweries"
PER_PAGE = 200  # The API's maximum results per page
all_breweries = []
current_page = 1

# disabling SSL verification .

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
print("--- Starting Data Extraction ---")
print("Warning: SSL verification is disabled.")

# --- Pagination Loop ---
while True:
    # Set the parameters for the current page
    params = {
        "per_page": PER_PAGE,
        "page": current_page
    }

    try:
        response = requests.get(API_URL, params=params, verify=False)

        # Check for a successful response
        if response.status_code == 200:
            data = response.json()

            # If the API returns an empty list, we've reached the end
            if not data:
                print("\nNo more data found. Reached the last page.")
                break

            # Add the breweries from the current page to our master list
            all_breweries.extend(data)
            print(f"Successfully fetched page {current_page} with {len(data)} breweries.")

            # Increment the page number for the next iteration
            current_page += 1

            # Add a small delay to avoid overwhelming the API
            time.sleep(0.1)  # 100ms delay

        else:
            print(f"Request failed on page {current_page} with status code: {response.status_code}")
            print(f"Error: {response.text}")
            break

    except requests.exceptions.RequestException as e:
        print(f"A network error occurred: {e}")
        break

# --- Data Processing and Saving ---
if all_breweries:
    print(f"\n--- Extraction Complete ---")
    print(f"Total breweries extracted: {len(all_breweries)}")

    # Save the complete raw data to a JSON file
    try:
        with open("all_breweries_data.json", "w") as f:
            json.dump(all_breweries, f, indent=2)
        print("Successfully saved all data to all_breweries_data.json")
    except IOError as e:
        print(f"Error saving JSON file: {e}")


    # 2. Normalize the data into a Pandas DataFrame and save as CSV
    try:
        df = pd.json_normalize(all_breweries)

        # Define the columns you want in your final CSV
        columns_to_keep = [
            'id', 'name', 'brewery_type', 'street', 'city', 'state',
            'postal_code', 'country', 'longitude', 'latitude',
            'phone', 'website_url'
        ]
    
        df_filtered = df[[col for col in columns_to_keep if col in df.columns]]

        df_filtered.to_csv("all_breweries_data.csv", index=False)
        print("Successfully saved all data to all_breweries_data.csv")

    except Exception as e:
        print(f"Error processing data or saving CSV: {e}")

else:
    print("\nNo data was extracted. Please check the API status or your network connection.")