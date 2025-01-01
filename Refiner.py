
import pandas as pd
from sympy import symbols, Eq, solve
import sqlite3
from datetime import datetime

def refine_results(file_name, is_sqlite=False, table_name=None) :
    try:
        # Load the data based on file type
        if is_sqlite:
            if not table_name :
                raise ValueError("Table name must be provided for SQLite database.")
            # Connect to the SQLite database
            conn = sqlite3.connect(file_name)
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
            conn.close()
        else:
            # Load the Excel file
            df = pd.read_excel(file_name)
    except FileNotFoundError :
        print(f"File not found : {file_name}")
        return []
    except Exception as e :
        print(f"An error occurred while reading the file: {e}")
        return []
    
    try :
        # Collect user inputs with validation
        min_magnification = float(input("Input minimum M_total: "))
        max_magnification = float(input("Input maximum M_total: "))
        min_I2 = float(input("Input minimum I2: "))
        max_I2 = float(input("Input maximum I2: "))
        max_Resolution = float(input("Input maximum Resolution: "))
        min_Resolution = float(input("Input minimum Resolution: "))
        max_Linear_FOV = float(input("Input maximum Linear_FOV: "))
        min_Linear_FOV = float(input("Input minimum Linear_FOV: "))

    except ValueError:
        print("Invalid input. Please enter numeric values only.")
        return []

    refined_results = []

    for _, result in df.iterrows():
        try:
            # Ensure M_total and I2 are valid numbers
            M_total = result['M_total']
            I2 = result['I2']
            Resolution = result['Resolution']
            Linear_FOV = result['Linear_FOV']
            # Check the filtering conditions
            if min_magnification <= abs(M_total) <= max_magnification and min_I2 <= abs(I2) <= max_I2 and min_Resolution <= abs(Resolution) <= max_Resolution and min_Linear_FOV <= abs(Linear_FOV) <= max_Linear_FOV: 
                refined_results.append(result)
        except KeyError:
            print("Invalid result entry: missing 'M_total' or 'I2' or 'Resolution'. Skipping...")
        except TypeError:
            print(f"Invalid data type in result: {result}. Skipping...")

    # Convert the refined results back to a DataFrame
    refined_df = pd.DataFrame(refined_results)
    timestamp = datetime.now().strftime("%Y-%m_%H-%M-%S")
    try:
    # Save the refined results to a new Excel file
        output_file = f"refined_results_{timestamp}.xlsx"
        refined_df.to_excel(output_file, index=False)
        print(f"Refined results saved to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred while saving the refined results as excel: {e}")
    # Save the refined results to a new database file
    try:
        output_db = f"refined_results_{timestamp}.db"
        conn = sqlite3.connect(output_db)
        refined_df.to_sql('results', conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
        print(f"Refined results saved to '{output_db}'.")
    except Exception as e:
        print(f"An error occurred while saving the refined results as database: {e}")

    return refined_results

# Example usage:
# Get user input for SQLite and table name
is_sqlite_input = input("Is the file an SQLite database? (True/False): ").strip().lower()
is_sqlite = is_sqlite_input in ["true", "True", "yes", "Yes" , "y" , "Y" , "T" , "t"]

table_name = "results"
db_name = "refined_results.db"
refined_results_processed = False
if is_sqlite:

    # Call the function
    try :
        if db_name == "refined_results.db" :
            refine_results("refined_results.db", is_sqlite=is_sqlite, table_name=table_name)
            refined_results_processed = True
            print("Refined results processed.")

    except FileNotFoundError :
        print(f"File not found : {db_name}")
    if not refined_results_processed :
            print("Refined results not processed. Processing lens_calculations_raw_results.db")
            try :
                refine_results("lens_calculations_raw_results.db", is_sqlite=is_sqlite, table_name=table_name)                
                print("Lens_calculations_raw_results.db processed.")

            except FileNotFoundError :
                print(f"File not found : lens_calculations_raw_results.db")
        
else :
    refine_results("lens_calculations_raw_results.xlsx")
