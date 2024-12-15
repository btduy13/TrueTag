import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import win32com.client
import os
import sys

# Check if the application is running from PyInstaller
if hasattr(sys, '_MEIPASS'):
    # When running from PyInstaller bundle
    SCRIPTS_FOLDER = os.path.join(sys._MEIPASS, 'Tổng hợp')  # Folder containing AutoLISP files
    # icon_path = os.path.join(sys._MEIPASS, 'logo.ico')  # Path to the new icon file
    # logo_path = os.path.join(sys._MEIPASS, 'logo.png')  # Path to logo image
else:
    # When running from the script directly
    SCRIPTS_FOLDER = r"C:\Users\USER\Desktop\Auto App\Tổng hợp"  # Base folder path
    # icon_path = os.path.join(os.path.abspath('.'), 'logo.ico')  # Path to the new icon file
    # logo_path = os.path.join(os.path.abspath('.'), 'logo.png')  # Path to logo image

# Load available scripts into the dropdown menu
def load_available_scripts():
    """Load available scripts into the dropdown menu."""
    try:
        lisp_files = [f[:-4] for f in os.listdir(SCRIPTS_FOLDER) if f.endswith(".lsp")]
        if lisp_files:
            selected_script.set(lisp_files[0])
            script_menu['values'] = lisp_files
        else:
            selected_script.set('No Scripts Available')
            script_menu['values'] = []
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load script list: {e}")

# Run the selected script in AutoCAD with the CSV file path
def run_selected_script():
    """Run the selected script in AutoCAD with the CSV file path."""
    try:
        selected_file = selected_script.get() + ".lsp"
        if selected_file == "No Scripts Available.lsp":
            messagebox.showwarning("No Script Selected", "Please select a script to run")
            return

        csv_file_path = selected_csv.get()
        # If the CSV file is not required for the script, or is optional
        file_path = os.path.join(SCRIPTS_FOLDER, selected_file)
        file_path = file_path.replace("\\", "/")

        # Disable the run button and show progress bar
        run_button.config(state=DISABLED)
        progress_bar.grid()
        progress_bar.start()

        root.update_idletasks()

        # Connect to AutoCAD
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument

        # Load and run AutoLISP script with or without CSV path
        if csv_file_path:
            # If the script accepts the CSV file as an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()} "{csv_file_path}") '
        else:
            # If no CSV file is provided, do not pass an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()}) '

        doc.SendCommand(lisp_command + "\n")

        result_label.config(text=f"Script {selected_file} ran successfully.", foreground='#4CAF50')
    except Exception as e:
        result_label.config(text=f"An error occurred: {e}", foreground='red')
    finally:
        # Re-enable the run button and stop progress bar
        run_button.config(state=NORMAL)
        progress_bar.stop()
        progress_bar.grid_remove()

# Open a file dialog to choose a CSV file and automatically save the path
def choose_csv_file():
    """Open a file dialog to select a CSV file."""
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        csv_file_label.config(text=f"Selected: {os.path.basename(file_path)}", foreground='#4CAF50')
        selected_csv.set(file_path)

# User Interface
root = tb.Window(themename="superhero")  # You can choose different themes
root.title(" TRUETAG ")
root.geometry("700x380")  # Increased window size for better layout
root.resizable(True, True)  # Allow window to be resizable
# root.iconbitmap(icon_path)

# Styling
font_title = ("Arial", 20, "bold")
font_label = ("Arial", 12)
font_button = ("Arial", 12, "bold")
font_result = ("Arial", 12, "italic")

# Main Frame with padding
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

# Logo and Title Frame
header_frame = ttk.Frame(main_frame)
header_frame.pack(fill=tk.X, pady=(0, 20))

# Load and display logo if available
# if os.path.exists(logo_path):
#     from PIL import Image, ImageTk  # Ensure PIL is installed
#     logo_image = Image.open(logo_path)
#     logo_image = logo_image.resize((50, 50), Image.ANTIALIAS)
#     logo_photo = ImageTk.PhotoImage(logo_image)
#     logo_label = ttk.Label(header_frame, image=logo_photo)
#     logo_label.image = logo_photo  # Keep a reference
#     logo_label.pack(side=tk.LEFT, padx=(0, 10))

# Title label
title_label = ttk.Label(header_frame, text="TRUE TAG LOADER", font=font_title)
title_label.pack(side=tk.LEFT, anchor='w')

# Script selection frame
script_frame = ttk.LabelFrame(main_frame, text="Available Drawing Types", padding=15)
script_frame.pack(fill=tk.X, pady=10)

script_label = ttk.Label(script_frame, text="Script election:", font=font_label)
script_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

selected_script = tk.StringVar()
script_menu = ttk.Combobox(script_frame, textvariable=selected_script, state="readonly", width=40, font=font_label)
script_menu.grid(row=0, column=1, sticky='ew', pady=5)

# Tooltip for script menu
ToolTip(script_menu, text="Choose a script to run")

script_frame.columnconfigure(1, weight=1)

# Choose CSV file section
csv_frame = ttk.LabelFrame(main_frame, text="CSV File Selection", padding=15)
csv_frame.pack(fill=tk.X, pady=10)

csv_file_label = ttk.Label(csv_frame, text="No CSV file selected", font=font_label)
csv_file_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

choose_csv_button = ttk.Button(csv_frame, text="Choose CSV File", command=choose_csv_file, bootstyle=PRIMARY)
choose_csv_button.grid(row=0, column=1, sticky='e', pady=5)

# Tooltip for CSV button
ToolTip(choose_csv_button, text="Select a CSV file to use with the script")

csv_frame.columnconfigure(1, weight=1)

# Run button with enhanced styling
run_button = ttk.Button(main_frame, text="Run Script", command=run_selected_script, bootstyle=SUCCESS, width=20)
run_button.pack(pady=20)

# Tooltip for Run button
ToolTip(run_button, text="Run the selected script in AutoCAD")

# Progress bar
progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
progress_bar.pack_forget()  # Hide it initially

# Store the path of the selected CSV file
selected_csv = tk.StringVar()

# Result label
result_label = ttk.Label(main_frame, text="", wraplength=600, font=font_result, anchor='center')
result_label.pack(pady=10)

# Configure grid weights for responsiveness
main_frame.columnconfigure(0, weight=1)
script_frame.columnconfigure(1, weight=1)
csv_frame.columnconfigure(1, weight=1)

# Load available scripts
load_available_scripts()

# Add a status bar
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = ttk.Label(root, textvariable=status_var, relief=SUNKEN, anchor='w', font=("Arial", 10))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Update status messages in functions
def run_selected_script():
    """Run the selected script in AutoCAD with the CSV file path."""
    try:
        selected_file = selected_script.get() + ".lsp"
        if selected_file == "No Scripts Available.lsp":
            messagebox.showwarning("No Script Selected", "Please select a script to run")
            status_var.set("No script selected.")
            return

        csv_file_path = selected_csv.get()
        # If the CSV file is not required for the script, or is optional
        file_path = os.path.join(SCRIPTS_FOLDER, selected_file)
        file_path = file_path.replace("\\", "/")

        # Disable the run button and show progress bar
        run_button.config(state=DISABLED)
        progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
        progress_bar.start()
        status_var.set("Running script...")

        root.update_idletasks()

        # Connect to AutoCAD
        acad = win32com.client.Dispatch("AutoCAD.Application")
        doc = acad.ActiveDocument

        # Load and run AutoLISP script with or without CSV path
        if csv_file_path:
            # If the script accepts the CSV file as an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()} "{csv_file_path}") '
        else:
            # If no CSV file is provided, do not pass an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()}) '

        doc.SendCommand(lisp_command + "\n")

        result_label.config(text=f"Script {selected_file} ran successfully.", foreground='#4CAF50')
        status_var.set("Script ran successfully.")
    except Exception as e:
        result_label.config(text=f"An error occurred: {e}", foreground='red')
        status_var.set("Error occurred during script execution.")
    finally:
        # Re-enable the run button and stop progress bar
        run_button.config(state=NORMAL)
        progress_bar.stop()
        progress_bar.pack_forget()

# Bind the updated run_selected_script with status updates
root.mainloop()
