
import pandas as pd
from sympy import symbols, Eq, solve

def refine_results_from_excel(file_name):
    try:
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_name)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        return []
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return []
    
    try:
        # Collect user inputs with validation
        min_magnification = float(input("Input minimum M_total: "))
        max_magnification = float(input("Input maximum M_total: "))
        min_I2 = float(input("Input minimum I2: "))
        max_I2 = float(input("Input maximum I2: "))
        max_Resolution = float(input("Input maximum Resolution: "))
        min_Resolution = float(input("Input minimum Resolution: "))

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
            # Check the filtering conditions
            if min_magnification <= abs(M_total) <= max_magnification and min_I2 <= abs(I2) <= max_I2 and min_Resolution <= abs(Resolution) <= max_Resolution:
                refined_results.append(result)
        except KeyError:
            print("Invalid result entry: missing 'M_total' or 'I2' or 'Resolution'. Skipping...")
        except TypeError:
            print(f"Invalid data type in result: {result}. Skipping...")

    # Convert the refined results back to a DataFrame
    refined_df = pd.DataFrame(refined_results)

    # Save the refined results to a new Excel file
    output_file = "refined_results.xlsx"
    refined_df.to_excel(output_file, index=False)
    print(f"Refined results saved to '{output_file}'.")

    return refined_results

# Example usage
refine_results_from_excel("lens_calculations_raw_results.xlsx")

