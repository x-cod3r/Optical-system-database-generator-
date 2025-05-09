import tkinter as tk
from tkinter import ttk, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter

# --- Constants ---
OBJECT_HEIGHT_DEFAULT = 5.0
BASE_IMAGE_SIZE = 100
MAX_IMAGE_SIZE = 500
OBJECT_DISTANCE_DEFAULT = 300.0
FOCAL_LENGTH_LENS1_DEFAULT = 50.0
FOCAL_LENGTH_LENS2_DEFAULT = 20.0
LENS_SEPARATION_DEFAULT = 30.0


# --- Functions ---

def lens_formula(focal_length, object_distance):
    """
    Calculates the image distance (v) using the thin lens formula.

    Args:
        focal_length (float): The focal length of the lens.
        object_distance (float): The object distance (negative for real objects).

    Returns:
        float: The image distance (v).  Returns float('inf') if the
               denominator in the formula is zero.
    """
    try:
        image_distance = 1 / (1 / focal_length - 1 / object_distance)
        return image_distance
    except ZeroDivisionError:
        return float('inf')


def ray_trace_and_plot(f1, f2, lens_separation, u1, object_height):
    """
    Performs ray tracing for a two-lens system and generates a plot.

    Args:
        f1 (float): Focal length of the first lens (objective).
        f2 (float): Focal length of the second lens (eyepiece).
        lens_separation (float): Distance between the two lenses.
        u1 (float): Object distance from the first lens (positive value).
        object_height (float): Height of the object.

    Returns:
        tuple: A tuple containing the matplotlib Figure object and the
               total magnification.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.set_xlim(-u1 - 10, max(f1 + f2 + lens_separation + 50, 100))
    ax.set_ylim(-object_height * 3, object_height * 3)  # Dynamic y-limits
    ax.axhline(0, color='black', lw=0.5)  # Optical axis

    # Lens positions
    lens1_pos = 0
    lens2_pos = lens_separation

    # First lens: Objective
    v1 = lens_formula(f1, -u1)
    img1_pos = lens1_pos + v1

    # Second lens: Eyepiece
    u2 = lens_separation - v1
    v2 = lens_formula(f2, -u2)
    img2_pos = lens2_pos + v2

    # Magnification calculation
    m1 = v1 / u1
    m2 = v2 / u2
    total_magnification = abs(m1 * m2)

    # Draw lenses
    ax.plot([lens1_pos, lens1_pos], [-object_height * 2, object_height * 2], 'b-', lw=2,
            label='Lens 1 (Objective)')
    ax.plot([lens2_pos, lens2_pos], [-object_height * 2, object_height * 2], 'g-', lw=2,
            label='Lens 2 (Eyepiece)')

    # Rays from object
    obj_pos = -u1

    # Ray 1: Parallel to axis
    ax.plot([obj_pos, lens1_pos], [object_height, object_height], 'r-')
    ax.plot([lens1_pos, lens1_pos + f1], [object_height, 0], 'r-')
    ax.plot([lens1_pos + f1, lens2_pos], [0, (lens2_pos - (lens1_pos + f1)) * (object_height / f1)],
            'r--')

    # Ray 2: Through center
    ax.plot([obj_pos, lens2_pos], [object_height, object_height * (lens2_pos - obj_pos) / (lens1_pos - obj_pos)],
            'r-')

    # Ray 3: Through focal point
    ax.plot([obj_pos, lens1_pos], [object_height, 0], 'r-')
    ax.plot([lens1_pos, lens2_pos], [0, 0], 'r-')

    # Mark focal points and images
    ax.plot(lens1_pos + f1, 0, 'bo', label=f'F1 ({f1:.1f} mm)')
    ax.plot(lens2_pos + f2, 0, 'go', label=f'F2 ({f2:.1f} mm)')
    if v1 != float('inf'):
        ax.plot(img1_pos, 0, 'k*', label=f'Image 1 ({v1:.2f} mm)')
    if v2 != float('inf'):
        ax.plot(img2_pos, 0, 'm*', label=f'Image 2 ({v2:.2f} mm)')

    ax.set_xlabel('Distance (mm)')
    ax.set_ylabel('Height (mm)')
    ax.set_title('Ray Tracing: Two-Lens System')
    ax.grid(True)
    ax.legend()

    return fig, total_magnification


def simulate_image(magnification):
    """
    Simulates the perceived image based on the calculated magnification.

    Args:
        magnification (float): The total magnification of the system.

    Returns:
        ImageTk.PhotoImage: APhotoImage object representing the simulated image.
    """
    img = Image.new('RGB', (BASE_IMAGE_SIZE, BASE_IMAGE_SIZE), color='white')
    draw = ImageDraw.Draw(img)

    # Draw a simple "X" as the object
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except OSError:
        font = ImageFont.load_default()
    draw.text((BASE_IMAGE_SIZE // 2 - 10, BASE_IMAGE_SIZE // 2 - 20), "X", font=font, fill='black')

    # Scale the image based on magnification
    new_size = int(BASE_IMAGE_SIZE * magnification), int(BASE_IMAGE_SIZE * magnification)
    if new_size[0] > MAX_IMAGE_SIZE or new_size[1] > MAX_IMAGE_SIZE:  # Cap size
        scale_factor = min(MAX_IMAGE_SIZE / new_size[0], MAX_IMAGE_SIZE / new_size[1])
        new_size = int(new_size[0] * scale_factor), int(new_size[1] * scale_factor)
    simulated_img = img.resize(new_size, Image.LANCZOS)

    # Add slight blur
    simulated_img = simulated_img.filter(ImageFilter.GaussianBlur(radius=0.5))
    return ImageTk.PhotoImage(simulated_img)


def update_plot_and_image():
    """
    Updates the plot and simulated image based on GUI input.
    """
    try:
        f1 = float(entry_f1.get())
        f2 = float(entry_f2.get())
        lens_separation = float(entry_d.get())
        u1 = float(entry_u1.get())
        object_height = float(entry_obj_height.get())

        # Clear previous plot
        for widget in frame_plot.winfo_children():
            widget.destroy()

        # Generate and embed new plot
        fig, magnification = ray_trace_and_plot(f1, f2, lens_separation, u1, object_height)
        canvas = FigureCanvasTkAgg(fig, master=frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas, frame_plot)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Update magnification label
        result_label.config(text=f"Total Magnification: {magnification:.2f}x")

        # Simulate and display image
        img_tk = simulate_image(magnification)
        image_label.config(image=img_tk)
        image_label.image = img_tk  # Keep reference

    except ValueError:
        result_label.config(text="Please enter valid numbers.")


def save_image():
    """Saves the simulated image to a file."""
    try:
        img_tk = image_label.image  # Get the current image from the label
        if img_tk:  # Check if an image exists
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"),
                                                                ("All files", "*.*")])
            if file_path:
                # Convert PhotoImage to PIL Image
                # Workaround for saving PhotoImage, see https://stackoverflow.com/a/74588206
                temp_image = ImageTk.getimage( img_tk )
                temp_image.save(file_path)
    except AttributeError:
        print("No hay imagen que guardar")
    except Exception as e:
        print(f"Error saving image: {e}")

# --- GUI Setup ---

root = tk.Tk()
root.title("Ray Tracing Two-Lens System with Image Simulation")

# Input frame
frame_input = ttk.Frame(root, padding="10")
frame_input.grid(row=0, column=0, sticky="ew")

# Input validation function
def validate_positive_number(value):
    """Validates that the input is a positive number or empty."""
    if value.replace('.', '', 1).isdigit() and float(value) >= 0:
        return True
    elif value == "":
        return True
    return False

vcmd = (root.register(validate_positive_number), '%P')

# --- Sliders and Entry Fields ---

# Focal Length Lens 1
ttk.Label(frame_input, text="Focal Length Lens 1 (mm):").grid(row=0, column=0, sticky="w")
slider_f1 = ttk.Scale(frame_input, from_=1, to=100, orient=tk.HORIZONTAL,
                     command=lambda val: entry_f1.delete(0, tk.END) or entry_f1.insert(0, f"{float(val):.1f}"))
slider_f1.grid(row=0, column=1, padx=5, pady=5)
slider_f1.set(FOCAL_LENGTH_LENS1_DEFAULT)
entry_f1 = ttk.Entry(frame_input, width=5, validate="key", validatecommand=vcmd)
entry_f1.grid(row=0, column=2, padx=5, pady=5)
entry_f1.insert(0, str(FOCAL_LENGTH_LENS1_DEFAULT))

# Focal Length Lens 2
ttk.Label(frame_input, text="Focal Length Lens 2 (mm):").grid(row=1, column=0, sticky="w")
slider_f2 = ttk.Scale(frame_input, from_=1, to=100, orient=tk.HORIZONTAL,
                     command=lambda val: entry_f2.delete(0, tk.END) or entry_f2.insert(0, f"{float(val):.1f}"))
slider_f2.grid(row=1, column=1, padx=5, pady=5)
slider_f2.set(FOCAL_LENGTH_LENS2_DEFAULT)
entry_f2 = ttk.Entry(frame_input, width=5, validate="key", validatecommand=vcmd)
entry_f2.grid(row=1, column=2, padx=5, pady=5)
entry_f2.insert(0, str(FOCAL_LENGTH_LENS2_DEFAULT))

# Lens Separation
ttk.Label(frame_input, text="Lens Separation (mm):").grid(row=2, column=0, sticky="w")
slider_d = ttk.Scale(frame_input, from_=1, to=200, orient=tk.HORIZONTAL,
                    command=lambda val: entry_d.delete(0, tk.END) or entry_d.insert(0, f"{float(val):.1f}"))
slider_d.grid(row=2, column=1, padx=5, pady=5)
slider_d.set(LENS_SEPARATION_DEFAULT)
entry_d = ttk.Entry(frame_input, width=5, validate="key", validatecommand=vcmd)
entry_d.grid(row=2, column=2, padx=5, pady=5)
entry_d.insert(0, str(LENS_SEPARATION_DEFAULT))

# Object Distance
ttk.Label(frame_input, text="Object Distance (mm):").grid(row=3, column=0, sticky="w")
slider_u1 = ttk.Scale(frame_input, from_=1, to=500, orient=tk.HORIZONTAL,
                     command=lambda val: entry_u1.delete(0, tk.END) or entry_u1.insert(0, f"{float(val):.1f}"))
slider_u1.grid(row=3, column=1, padx=5, pady=5)
slider_u1.set(OBJECT_DISTANCE_DEFAULT)
entry_u1 = ttk.Entry(frame_input, width=5, validate="key", validatecommand=vcmd)
entry_u1.grid(row=3, column=2, padx=5, pady=5)
entry_u1.insert(0, str(OBJECT_DISTANCE_DEFAULT))

# Object Height
ttk.Label(frame_input, text="Object Height (mm):").grid(row=4, column=0, sticky="w")
slider_obj_height = ttk.Scale(frame_input, from_=1, to=20, orient=tk.HORIZONTAL,
                              command=lambda val: entry_obj_height.delete(0, tk.END) or entry_obj_height.insert(0,
                                                                                                                  f"{float(val):.1f}"))
slider_obj_height.grid(row=4, column=1, padx=5, pady=5)
slider_obj_height.set(OBJECT_HEIGHT_DEFAULT)
entry_obj_height = ttk.Entry(frame_input, width=5, validate="key", validatecommand=vcmd)
entry_obj_height.grid(row=4, column=2, padx=5, pady=5)
entry_obj_height.insert(0, str(OBJECT_HEIGHT_DEFAULT))

# Update Button
ttk.Button(frame_input, text="Update Plot & Image", command=update_plot_and_image).grid(row=5, column=0,
                                                                                        columnspan=3, pady=10)

# Result label
result_label = ttk.Label(frame_input, text="")
result_label.grid(row=6, column=0, columnspan=3)

# Save Image Button
save_button = ttk.Button(frame_input, text="Save Image", command=save_image)
save_button.grid(row=7, column=0, columnspan=3, pady=5)

# --- Plot Frame ---
frame_plot = ttk.Frame(root)
frame_plot.grid(row=0, column=1, sticky="nsew")

# --- Image Simulation Frame ---
frame_image = ttk.Frame(root)
frame_image.grid(row=1, column=1, sticky="nsew")
ttk.Label(frame_image, text="Simulated Image View").pack()
image_label = ttk.Label(frame_image)
image_label.pack()

# --- Configure Grid Weights ---
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

# --- Initial plot and image ---
update_plot_and_image()

# --- Start GUI ---
root.mainloop()
