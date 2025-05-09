import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def load_excel_file():
    # Get the file name from the .env file
    file_name = os.getenv("EXCEL_FILE_NAME")
    
    if not file_name:
        raise ValueError("EXCEL_FILE_NAME is not set in the .env file.")
    
    # Read the Excel file
    try:
        data = pd.read_excel(file_name)
        return data  # Return the DataFrame
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_name}' was not found in the current folder.")
    except Exception as e:
        raise Exception(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    try:
        df = load_excel_file()
        print("File loaded successfully!")
        print(df.head())
    except Exception as e:
        print(e)