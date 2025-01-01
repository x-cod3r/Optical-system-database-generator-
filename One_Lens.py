import pandas as pd
import math

# Given initial conditions
initial_magnification = float(input("Initial Magnification: "))
initial_object_distance = float(input("Initial Object Distance: "))  # cm

# Wavelength of light (in cm) and aperture diameter (D) in cm
wavelength = 0.000055  # Example: 500 nm = 0.0005 cm
aperture_diameter = float(input("Aperture Diameter: "))  # Example: 1 cm

# Calculate initial image distance (I)
I_initial = -initial_magnification * initial_object_distance

# Calculate focal length (F)
F = (I_initial * initial_object_distance) / (I_initial + initial_object_distance)

# Prepare results list
results = []

# Iterate over different object distances (S)
for S in range(10, 100):  # Adjust range as needed
    # Calculate image distance (I) for the current S maintaining the same F
    if S + F == 0:  # Avoid division by zero
        continue
    I = (F * S) / (S - F)
    
    # Calculate magnification (M)
    M = -I / S

    # Calculate diffraction limit
    angular_resolution_rad = 1.22 * (wavelength / aperture_diameter)  # In radians
    angular_resolution_deg = angular_resolution_rad * (180 / math.pi)  # Convert to degrees
    linear_resolution = angular_resolution_rad * S  # In cm
    
    # Store results
    results.append({
        "Object Distance (S)": S,
        "Image Distance (I)": round(I, 2),
        "Magnification (M)": round(M, 2),
        "Focal Length (F)": round(F, 2),
        "Angular Resolution (deg)": round(angular_resolution_deg, 6),
        "Linear Resolution (cm)": round(linear_resolution, 6),
    })

# Convert results to a DataFrame
df = pd.DataFrame(results)

# Export the DataFrame to an Excel file
output_file = "lens_calculations_with_diffraction_degrees.xlsx"
df.to_excel(output_file, index=False)

print(f"Focal Length (F): {round(F, 2)} cm")
print(f"Results with diffraction limits (in degrees) have been exported to '{output_file}'.")
