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
    PID_SCRIPTS_FOLDER = os.path.join(sys._MEIPASS, 'Tổng hợp', 'PID')  # Folder containing PID AutoLISP files
    TML_SCRIPTS_FOLDER = os.path.join(sys._MEIPASS, 'Tổng hợp', 'TML')  # Folder containing TML AutoLISP files
    POSITION_SCRIPTS_FOLDER = os.path.join(sys._MEIPASS, 'Tổng hợp', 'POSITION')  # Folder containing TML AutoLISP files
    # Idemitsu_SCRIPTS_FOLDER = os.path.join(sys._MEIPASS, 'Idemitsu_Tool', 'Reviewed')  # Folder containing Idemitsu scripts
    icon_path = os.path.join(sys._MEIPASS, 'logo.ico')  # Path to the new icon file
    logo_path = os.path.join(sys._MEIPASS, 'logo.png')  # Path to logo image
else:
    # When running from the script directly
    PID_SCRIPTS_FOLDER = r"C:\Users\PC\Desktop\Auto App\Tổng hợp\PID"  # Base folder path for VSP
    TML_SCRIPTS_FOLDER = r"C:\Users\PC\Desktop\Auto App\Tổng hợp\TML"  # Base folder path for VSP
    POSITION_SCRIPTS_FOLDER = r"C:\Users\PC\Desktop\Auto App\Tổng hợp\Position"  # Base folder path for VSP
    # Idemitsu_SCRIPTS_FOLDER = r"C:\Users\USER\Desktop\AUTOCAD_test\Idemitsu_Tool\Reviewed"  # Base folder path for Idemitsu
    icon_path = os.path.join(os.path.abspath('.'), 'logo.ico')  # Path to the new icon file
    logo_path = os.path.join(os.path.abspath('.'), 'logo.png')  # Path to logo image

# Dictionary to hold script categories and their corresponding folders
SCRIPT_CATEGORIES = {
    "PID": PID_SCRIPTS_FOLDER,
    # "Idemitsu": Idemitsu_SCRIPTS_FOLDER,
    "Position": POSITION_SCRIPTS_FOLDER,
    "TML":TML_SCRIPTS_FOLDER
}

def load_available_scripts(category):
    """
    Load available scripts into the dropdown menu based on the selected category.
    """
    scripts_folder = SCRIPT_CATEGORIES.get(category, PID_SCRIPTS_FOLDER)
    try:
        lisp_files = [f[:-4] for f in os.listdir(scripts_folder) if f.endswith(".lsp")]
        if lisp_files:
            selected_script.set(lisp_files[0])
            script_menu['values'] = lisp_files
            script_menu.config(state="readonly")
            status_var.set(f"Loaded {len(lisp_files)} scripts from {category}.")
        else:
            selected_script.set('No Scripts Available')
            script_menu['values'] = []
            script_menu.config(state="disabled")
            status_var.set(f"No scripts found in {category}.")
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load script list from {category}: {e}")
        selected_script.set('Error Loading Scripts')
        script_menu['values'] = []
        script_menu.config(state="disabled")
        status_var.set(f"Error loading scripts from {category}.")

def run_selected_script():
    """
    Run the selected script in AutoCAD with the CSV file path if enabled.
    """
    try:
        category = selected_category.get()
        if category not in SCRIPT_CATEGORIES:
            messagebox.showwarning("No Category Selected", "Please select a script category.")
            status_var.set("No category selected.")
            return

        selected_file = selected_script.get() + ".lsp"
        if selected_file == "No Scripts Available.lsp" or script_menu['state'] == 'disabled':
            messagebox.showwarning("No Script Selected", "Please select a valid script to run.")
            status_var.set("No valid script selected.")
            return

        # Check if CSV usage is enabled
        if use_csv.get():
            csv_file_path = selected_csv.get()
            if not csv_file_path:
                messagebox.showwarning("CSV File Required", "Please select a CSV file or disable CSV usage.")
                status_var.set("CSV file not selected.")
                return
        else:
            csv_file_path = ''

        scripts_folder = SCRIPT_CATEGORIES[category]
        file_path = os.path.join(scripts_folder, selected_file)
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

def choose_csv_file():
    """
    Open a file dialog to select a CSV file.
    """
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        csv_file_label.config(text=f"Selected: {os.path.basename(file_path)}", foreground='#4CAF50')
        selected_csv.set(file_path)
        status_var.set(f"CSV file selected: {os.path.basename(file_path)}")
    else:
        csv_file_label.config(text="No CSV file selected", foreground='red')
        selected_csv.set('')
        status_var.set("No CSV file selected.")

# User Interface
root = tb.Window(themename="superhero")  # You can choose different themes
root.title("TRUETAG")
root.geometry("400x600")  # Increased window size for better layout
root.resizable(True, True)  # Allow window to be resizable
root.iconbitmap(icon_path)

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
if os.path.exists(logo_path):
    from PIL import Image, ImageTk  # Ensure PIL is installed
    logo_image = Image.open(logo_path)
    logo_image = logo_image.resize((50, 50), Image.ANTIALIAS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = ttk.Label(header_frame, image=logo_photo)
    logo_label.image = logo_photo  # Keep a reference
    logo_label.pack(side=tk.LEFT, padx=(0, 10))

# Title label
title_label = ttk.Label(header_frame, text="TRUE TAG LOADER", font=font_title)
title_label.pack(side=tk.LEFT, anchor='w')

# Script category selection frame
category_frame = ttk.LabelFrame(main_frame, text="Script Category", padding=15)
category_frame.pack(fill=tk.X, pady=10)

category_label = ttk.Label(category_frame, text="Select Category:", font=font_label)
category_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

selected_category = tk.StringVar()
category_menu = ttk.Combobox(category_frame, textvariable=selected_category, state="readonly", width=20, font=font_label)
category_menu['values'] = list(SCRIPT_CATEGORIES.keys())
category_menu.grid(row=0, column=1, sticky='w', pady=5)
category_menu.current(0)  # Set default selection to the first category

# Tooltip for category menu
ToolTip(category_menu, text="Choose a script category to load scripts from")

category_frame.columnconfigure(1, weight=1)

# Bind the category selection to load scripts
def on_category_change(event):
    selected = selected_category.get()
    load_available_scripts(selected)

category_menu.bind("<<ComboboxSelected>>", on_category_change)

# Script selection frame
script_frame = ttk.LabelFrame(main_frame, text="Available Drawing Types", padding=15)
script_frame.pack(fill=tk.X, pady=10)

script_label = ttk.Label(script_frame, text="Script selection:", font=font_label)
script_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

selected_script = tk.StringVar()
script_menu = ttk.Combobox(script_frame, textvariable=selected_script, state="readonly", width=40, font=font_label)
script_menu.grid(row=0, column=1, sticky='ew', pady=5)

# Tooltip for script menu
ToolTip(script_menu, text="Choose a script to run")

script_frame.columnconfigure(1, weight=1)

# Use CSV File Checkbox
csv_option_frame = ttk.Frame(main_frame, padding=15)
csv_option_frame.pack(fill=tk.X, pady=10)

use_csv = tk.BooleanVar()
use_csv_checkbox = ttk.Checkbutton(csv_option_frame, text="Use CSV File", variable=use_csv, command=lambda: toggle_csv_selection())
use_csv_checkbox.grid(row=0, column=0, sticky='w', pady=5)

# Tooltip for CSV checkbox
ToolTip(use_csv_checkbox, text="Check to run the script with a CSV file")

def toggle_csv_selection():
    """
    Enable or disable CSV file selection based on the checkbox state.
    """
    if use_csv.get():
        choose_csv_button.config(state=NORMAL)
        csv_file_label.config(state=NORMAL)
        status_var.set("CSV usage enabled.")
    else:
        choose_csv_button.config(state=DISABLED)
        csv_file_label.config(text="No CSV file selected", foreground='red')
        selected_csv.set('')
        status_var.set("CSV usage disabled.")

# Choose CSV file section
csv_frame = ttk.Frame(csv_option_frame)
csv_frame.grid(row=1, column=0, sticky='w', pady=(10, 0))

csv_file_label = ttk.Label(csv_frame, text="No CSV file selected", font=font_label)
csv_file_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

choose_csv_button = ttk.Button(csv_frame, text="Choose CSV File", command=choose_csv_file, bootstyle=PRIMARY, state=DISABLED)
choose_csv_button.grid(row=0, column=1, sticky='e', pady=5)

# Tooltip for CSV button
ToolTip(choose_csv_button, text="Select a CSV file to use with the script")

# Store the path of the selected CSV file
selected_csv = tk.StringVar()

# Run button with enhanced styling
run_button = ttk.Button(main_frame, text="Run Script", command=run_selected_script, bootstyle=SUCCESS, width=20)
run_button.pack(pady=20)

# Tooltip for Run button
ToolTip(run_button, text="Run the selected script in AutoCAD")

# Progress bar
progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
progress_bar.pack_forget()  # Hide it initially

# Result label
result_label = ttk.Label(main_frame, text="", wraplength=600, font=font_result, anchor='center')
result_label.pack(pady=10)

# Configure grid weights for responsiveness
main_frame.columnconfigure(0, weight=1)
category_frame.columnconfigure(1, weight=1)
script_frame.columnconfigure(1, weight=1)
csv_option_frame.columnconfigure(0, weight=1)
csv_frame.columnconfigure(1, weight=1)

# Add a status bar
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = ttk.Label(root, textvariable=status_var, relief=SUNKEN, anchor='w', font=("Arial", 10))
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Initial load of scripts based on default category
load_available_scripts(category_menu.get())

# Start the main loop
root.mainloop()
