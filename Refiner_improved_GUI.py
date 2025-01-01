import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import sqlite3

class DataRefinerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Refiner")
        self.root.geometry("600x600")
        self.root.grid_rowconfigure(11, weight=1)  # Ensure status label can grow vertically
        self.root.grid_columnconfigure(1, weight=1)  # Allow the column with entry boxes to expand

        # Variables to store user inputs
        self.is_sqlite = tk.BooleanVar(value=False)
        self.file_path = tk.StringVar()
        self.table_name = tk.StringVar(value="results")
        self.min_m_total = tk.StringVar()
        self.max_m_total = tk.StringVar()
        self.min_i2 = tk.StringVar()
        self.max_i2 = tk.StringVar()
        self.min_resolution = tk.StringVar()
        self.max_resolution = tk.StringVar()
        self.min_linear_fov = tk.StringVar()
        self.max_linear_fov = tk.StringVar()

        self._create_widgets()
        
        self.root.bind("<Configure>", self._on_window_resize)


    def _create_widgets(self):
        # File Selection
        ttk.Label(self.root, text="File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.file_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.root, text="Browse", command=self._browse_file).grid(row=0, column=2, padx=5, pady=5)

        # SQLite Checkbox and table name
        ttk.Checkbutton(self.root, text="Is SQLite?", variable=self.is_sqlite, command=self._toggle_table_name).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.root, text="Table Name:").grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.table_name_entry = ttk.Entry(self.root, textvariable=self.table_name, state=tk.DISABLED)
        self.table_name_entry.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        # M_total Input
        ttk.Label(self.root, text="Min M_total:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.min_m_total).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.root, text="Max M_total:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.max_m_total).grid(row=3, column=1, sticky="ew", padx=5, pady=5)

         # I2 Input
        ttk.Label(self.root, text="Min I2:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.min_i2).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.root, text="Max I2:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.max_i2).grid(row=5, column=1, sticky="ew", padx=5, pady=5)

        # Resolution Input
        ttk.Label(self.root, text="Min Resolution:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.min_resolution).grid(row=6, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.root, text="Max Resolution:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.max_resolution).grid(row=7, column=1, sticky="ew", padx=5, pady=5)

         # Linear_FOV Input
        ttk.Label(self.root, text="Min Linear_FOV:").grid(row=8, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.min_linear_fov).grid(row=8, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(self.root, text="Max Linear_FOV:").grid(row=9, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.root, textvariable=self.max_linear_fov).grid(row=9, column=1, sticky="ew", padx=5, pady=5)

        # Process Button
        ttk.Button(self.root, text="Process Data", command=self._process_data).grid(row=10, column=1, pady=20, sticky="ew")

        # Status label
        self.status_label = ttk.Label(self.root, text="", wraplength=500)
        self.status_label.grid(row=11, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def _on_window_resize(self, event):
        self.root.update_idletasks()
        # print (f"width : {event.width} \n height: {event.height}") # used to debug window size
    def _browse_file(self):
        file_types = [
            ("Excel Files", "*.xlsx *.xls"),
            ("SQLite Files", "*.db"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.file_path.set(file_path)

    def _toggle_table_name(self):
        if self.is_sqlite.get():
            self.table_name_entry.config(state=tk.NORMAL)
        else:
            self.table_name_entry.config(state=tk.DISABLED)
            self.table_name.set("results")  # Reset table name to default

    def _process_data(self):
        self.status_label.config(text="Processing...")
        self.root.update()  # Update the status label right away

        file_name = self.file_path.get()
        is_sqlite = self.is_sqlite.get()
        table_name = self.table_name.get()

        if not file_name:
            self._show_error("File selection error", "Please select a file")
            self._update_status("Please select a file")
            return

        if is_sqlite and not table_name:
            self._show_error("Table selection error", "Please enter a table name")
            self._update_status("Please enter a table name")
            return

        try:
            df = self._load_data(file_name, is_sqlite, table_name)
            if df is None:
                self._update_status("Data load failed.")
                return

            filtered_df = self._filter_data(df)
            if filtered_df is None:
                self._update_status("Data filter failed")
                return

            if filtered_df.empty:
                self._update_status("No data matched the filtering criteria.")
                return

            self._save_results(filtered_df)
            self._update_status("Data processing complete.")

        except Exception as e:
            self._show_error("An unexpected error occurred.", str(e))
            self._update_status("Data processing failed with an unexpected error")

    def _load_data(self, file_name, is_sqlite, table_name):
        try:
            if is_sqlite:
                conn = sqlite3.connect(file_name)
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                conn.close()
            else:
                df = pd.read_excel(file_name)
            return df
        except FileNotFoundError:
            self._show_error("File Not Found", f"Could not find {file_name}")
            return None
        except Exception as e:
            self._show_error("Data Load Error", f"Error loading data: {e}")
            return None

    def _filter_data(self, df):
        try:
            min_m_total = self._get_numeric_input(self.min_m_total, "Min M_total", allow_empty=True)
            max_m_total = self._get_numeric_input(self.max_m_total, "Max M_total", allow_empty=True)
            self._validate_range(min_m_total, max_m_total, "M_total")

            min_i2 = self._get_numeric_input(self.min_i2, "Min I2", allow_empty=True)
            max_i2 = self._get_numeric_input(self.max_i2, "Max I2", allow_empty=True)
            self._validate_range(min_i2, max_i2, "I2")

            min_resolution = self._get_numeric_input(self.min_resolution, "Min Resolution", allow_empty=True)
            max_resolution = self._get_numeric_input(self.max_resolution, "Max Resolution", allow_empty=True)
            self._validate_range(min_resolution, max_resolution, "Resolution")

            min_linear_fov = self._get_numeric_input(self.min_linear_fov, "Min Linear_FOV", allow_empty=True)
            max_linear_fov = self._get_numeric_input(self.max_linear_fov, "Max Linear_FOV", allow_empty=True)
            self._validate_range(min_linear_fov, max_linear_fov, "Linear_FOV")

        except ValueError as e:
            self._show_error("Input error", str(e))
            return None

        filtered_results = []
        for _, result in df.iterrows():
            try:
                m_total = result['M_total']
                i2 = result['I2']
                resolution = result['Resolution']
                linear_fov = result['Linear_FOV']

                # Check only if values are provided
                m_total_condition = True
                if min_m_total is not None and max_m_total is not None :
                    m_total_condition = min_m_total <= abs(m_total) <= max_m_total
                    
                i2_condition = True
                if min_i2 is not None and max_i2 is not None:
                   i2_condition = min_i2 <= abs(i2) <= max_i2
                
                resolution_condition = True
                if min_resolution is not None and max_resolution is not None:
                   resolution_condition = min_resolution <= abs(resolution) <= max_resolution
                
                linear_fov_condition = True
                if min_linear_fov is not None and max_linear_fov is not None:
                    linear_fov_condition = min_linear_fov <= abs(linear_fov) <= max_linear_fov
                    
                if  m_total_condition and i2_condition and resolution_condition and linear_fov_condition:
                    filtered_results.append(result)
            except KeyError as e:
                print(f"Invalid result entry: missing column {e}. Skipping...")
            except TypeError as e :
                print (f"Invalid data type in result: {result}. Skipping...")
        return pd.DataFrame(filtered_results)

    def _save_results(self, refined_df):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"refined_results_{timestamp}.xlsx"
        output_db = f"refined_results_{timestamp}.db"

        try:
            refined_df.to_excel(output_file, index=False)
            self._update_status(f"Refined results saved to '{output_file}'.")
        except Exception as e:
            self._show_error("Excel Save Error", f"Error saving to Excel: {e}")
            return

        try:
            conn = sqlite3.connect(output_db)
            refined_df.to_sql('results', conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()
            self._update_status(f"Refined results saved to '{output_db}'.")
        except Exception as e:
            self._show_error("SQLite Save Error", f"Error saving to SQLite: {e}")
            return

    def _get_numeric_input(self, var, name, allow_empty=False):
        try:
            value_str = var.get().strip()
            if not value_str and not allow_empty:
                raise ValueError(f"{name} cannot be empty.")
            if not value_str and allow_empty:
                return None
            return float(value_str)
        except ValueError:
            raise ValueError(f"Invalid value for {name}. Please enter a numeric value.")

    def _validate_range(self, min_val, max_val, name):
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValueError(f"Minimum value for {name} cannot be greater than the maximum value.")

    def _show_error(self, title, message):
        messagebox.showerror(title, message)

    def _update_status(self, message):
        self.status_label.config(text=message)
        self.root.update()

def main():
    root = tk.Tk()
    app = DataRefinerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
