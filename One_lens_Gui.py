import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import math

def get_float_input(prompt, entry):
    """Gets a float input from the user with error handling in GUI context."""
    try:
        value = float(entry.get())
        if value <= 0:
            messagebox.showerror("Error", f"Invalid input for {prompt}. Please enter a positive number.")
            return None
        return value
    except ValueError:
        messagebox.showerror("Error", f"Invalid input for {prompt}. Please enter a number.")
        return None


def calculate_focal_length(initial_magnification, initial_object_distance):
    """Calculates the focal length based on initial conditions."""
    # Calculate initial image distance (I)
    I_initial = -initial_magnification * initial_object_distance
    # Calculate focal length (F)
    F = (I_initial * initial_object_distance) / (I_initial + initial_object_distance)
    return F


def calculate_lens_properties(focal_length, wavelength, aperture_diameter, object_distance_start, object_distance_end):
    """Calculates lens properties for varying object distances, given a focal length."""
    results = []

    for S in range(object_distance_start, object_distance_end + 1):
         # Avoid division by zero
        if S == focal_length:
            print(f"Skipping object distance S = {S} cm because S - F results in 0.")
            continue
        
        # Calculate image distance (I) for the current S maintaining the same F
        I = (focal_length * S) / (S - focal_length)
        # Calculate magnification (M)
        M = -I / S
        # Calculate diffraction limit
        angular_resolution_rad = 1.22 * (wavelength / aperture_diameter)  # In radians
        angular_resolution_deg = angular_resolution_rad * (180 / math.pi)  # Convert to degrees
        linear_resolution = angular_resolution_rad * S  # In cm
        
        # Store results
        results.append({
            "Object Distance (S) cm": S,
            "Image Distance (I) cm": round(I, 2),
            "Magnification (M)": round(M, 2),
            "Focal Length (F) cm": round(focal_length, 2),
            "Angular Resolution (deg)": round(angular_resolution_deg, 6),
            "Linear Resolution (cm)": round(linear_resolution, 6),
        })

    return results

def export_to_excel(df, filename="One_lens_calculations_GUI.xlsx"):
    """Exports a DataFrame to an Excel file."""
    try:
        df.to_excel(filename, index=False)
        messagebox.showinfo("Success", f"Results have been exported to '{filename}'.")
    except Exception as e:
        messagebox.showerror("Error", f"Error exporting to excel: {e}")


def calculate_and_export():
    """Handles the entire calculation and export process."""
    initial_magnification = get_float_input("Initial Magnification", initial_magnification_entry)
    initial_object_distance = get_float_input("Initial Object Distance (cm)", initial_object_distance_entry)
    aperture_diameter = get_float_input("Aperture Diameter (cm)", aperture_diameter_entry)
    
    if None in (initial_magnification, initial_object_distance, aperture_diameter):
        return  # Exit if input is invalid

    wavelength = 0.000055  # cm
    
    try:
       object_distance_start = int(object_distance_start_entry.get())
       object_distance_end = int(object_distance_end_entry.get())
       if object_distance_start < 0 or object_distance_end < 0:
           messagebox.showerror("Error", "Object distance start and end values must be positive integers")
           return
    except ValueError:
         messagebox.showerror("Error", "Please enter a positive integer for Object distance start and end values.")
         return

    focal_length = calculate_focal_length(initial_magnification, initial_object_distance)
    results = calculate_lens_properties(focal_length, wavelength, aperture_diameter, object_distance_start, object_distance_end)
    
    if results:
      df = pd.DataFrame(results)
      export_to_excel(df)
      messagebox.showinfo("Focal Length", f"Focal Length (F): {focal_length:.2f} cm")
    else:
       messagebox.showinfo("Error", "No data to export.")

# ----- Tkinter GUI Setup -----
root = tk.Tk()
root.title("Lens Calculator")

# --- Input Fields ---
ttk.Label(root, text="Initial Magnification:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
initial_magnification_entry = ttk.Entry(root)
initial_magnification_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)

ttk.Label(root, text="Initial Object Distance (cm):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
initial_object_distance_entry = ttk.Entry(root)
initial_object_distance_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)

ttk.Label(root, text="Aperture Diameter (cm):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
aperture_diameter_entry = ttk.Entry(root)
aperture_diameter_entry.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)

ttk.Label(root, text="Starting Object Distance (cm):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
object_distance_start_entry = ttk.Entry(root)
object_distance_start_entry.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)

ttk.Label(root, text="Ending Object Distance (cm):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
object_distance_end_entry = ttk.Entry(root)
object_distance_end_entry.grid(row=4, column=1, sticky=tk.E, padx=5, pady=5)


# --- Calculation Button ---
calculate_button = ttk.Button(root, text="Calculate and Export", command=calculate_and_export)
calculate_button.grid(row=5, column=0, columnspan=2, pady=10)


root.mainloop()
