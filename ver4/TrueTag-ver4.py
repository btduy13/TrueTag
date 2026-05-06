import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import win32com.client
from win32com.client import GetActiveObject
import os
import sys
import json
import time
from datetime import datetime

# Application version — single source of truth
APP_VERSION = "4.1.1"
from usage_reporting import init as usage_init, record_run as usage_record, shutdown as usage_shutdown, test_email as usage_test_email, send_if_month_end
from config_manager import ConfigManager
from licensing_manager import LicensingManager
import threading

# Check if the application is running from PyInstaller
if getattr(sys, 'frozen', False):
    # When running from PyInstaller bundle
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    PID_SCRIPTS_FOLDER = os.path.join(bundle_dir, 'Scripts', 'PID')
    TML_SCRIPTS_FOLDER = os.path.join(bundle_dir, 'Scripts', 'TML')
    POSITION_SCRIPTS_FOLDER = os.path.join(bundle_dir, 'Scripts', 'Position')
    icon_path = os.path.join(bundle_dir, 'logo.ico')
    logo_path = os.path.join(bundle_dir, 'logo.png')
    # Persisted data should live next to the executable, not in _MEIPASS
    DATA_DIR = os.path.dirname(sys.executable)
else:
    # When running from the script directly
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    PID_SCRIPTS_FOLDER = os.path.join(parent_dir, "Scripts", "PID")
    TML_SCRIPTS_FOLDER = os.path.join(parent_dir, "Scripts", "TML")
    POSITION_SCRIPTS_FOLDER = os.path.join(parent_dir, "Scripts", "Position")
    icon_path = os.path.join(os.path.abspath('.'), 'logo.ico')
    logo_path = os.path.join(os.path.abspath('.'), 'logo.png')
    DATA_DIR = os.path.dirname(os.path.abspath(__file__))

print(f"PID Scripts Folder: {PID_SCRIPTS_FOLDER}")
print(f"TML Scripts Folder: {TML_SCRIPTS_FOLDER}")
print(f"Position Scripts Folder: {POSITION_SCRIPTS_FOLDER}")

# --- Config management ---
config_manager = ConfigManager(os.path.dirname(os.path.abspath(__file__)))

# --- Licensing management ---
licensing_manager = LicensingManager(DATA_DIR)

# Dictionary to hold script categories and their corresponding folders
SCRIPT_CATEGORIES = {
    "PID": PID_SCRIPTS_FOLDER,
    "Position": POSITION_SCRIPTS_FOLDER,
    "TML": TML_SCRIPTS_FOLDER
}

def get_active_cad_application():
    """Try to get the active BricsCAD instance; fall back to launching a new one."""
    prog_id = "BricscadApp.AcadApplication"
    try:
        return GetActiveObject(prog_id)
    except Exception:
        pass
    try:
        return win32com.client.Dispatch(prog_id)
    except Exception:
        pass
    return None

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
            # Status indicators removed
        else:
            selected_script.set('No Scripts Available')
            script_menu['values'] = []
            script_menu.config(state="disabled")
            # Status indicators removed
    except Exception as e:
        messagebox.showerror("Error", f"Cannot load script list from {category}: {e}")
        selected_script.set('Error Loading Scripts')
        script_menu['values'] = []
        script_menu.config(state="disabled")
        # Status indicators removed

def run_selected_script():
    """
    Run the selected script in BricsCAD with the CSV file path if enabled.
    Validation runs on the main thread; the CAD command runs in a background
    thread so the UI stays responsive.
    """
    # --- Single license check ---
    license_info = licensing_manager.get_license_info()
    if not license_info['is_valid']:
        messagebox.showerror(
            "License Error",
            f"Software is not licensed. Please activate a valid license.\n\nDetails: {license_info['message']}"
        )
        return
    if license_info['status'] not in ['licensed', 'trial']:
        messagebox.showerror("License Error", f"Software access denied. Current status: {license_info['status']}")
        return

    category = selected_category.get()
    if category not in SCRIPT_CATEGORIES:
        messagebox.showwarning("No Category Selected", "Please select a script category.")
        return

    selected_file = selected_script.get() + ".lsp"
    if selected_file == "No Scripts Available.lsp" or script_menu['state'] == 'disabled':
        messagebox.showwarning("No Script Selected", "Please select a valid script to run.")
        return

    if not licensing_manager.is_feature_enabled("basic_scripts"):
        messagebox.showerror("Feature Not Available", "Basic scripts feature is not available in your current license.")
        return

    # --- CSV validation ---
    if use_csv.get():
        if not licensing_manager.is_feature_enabled("csv_import"):
            messagebox.showerror("Feature Not Available", "CSV import feature is not available in your current license.")
            return
        csv_file_path = selected_csv.get()
        if not csv_file_path:
            messagebox.showwarning("CSV File Required", "Please select a CSV file or disable CSV usage.")
            return
        if not os.path.exists(csv_file_path):
            messagebox.showwarning(
                "CSV Not Found",
                f"The CSV file no longer exists:\n{csv_file_path}\n\nPlease select a new file."
            )
            return
    else:
        csv_file_path = ''

    scripts_folder = SCRIPT_CATEGORIES[category]
    file_path = os.path.join(scripts_folder, selected_file).replace("\\", "/")
    script_name = selected_script.get()

    if csv_file_path:
        lisp_command = f'(load "{file_path}") (c:{script_name} "{csv_file_path}") '
    else:
        lisp_command = f'(load "{file_path}") (c:{script_name}) '

    # --- Disable UI and show progress ---
    run_button.config(state=DISABLED)
    progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
    progress_bar.start()

    def _finish(message, color):
        """Called from background thread via root.after to update UI safely."""
        run_button.config(state=NORMAL)
        progress_bar.stop()
        progress_bar.pack_forget()
        result_label.config(text=message, foreground=color)

    def _run_in_thread():
        """Execute the CAD command off the main thread."""
        try:
            acad = get_active_cad_application()
            if not acad:
                raise RuntimeError("BricsCAD is not running. Please open BricsCAD and try again.")
            doc = acad.ActiveDocument

            start_time = time.time()
            doc.SendCommand(lisp_command + "\n")
            run_time_seconds = time.time() - start_time

            try:
                usage_record(script_name, run_time_seconds)
            except Exception:
                pass
            try:
                config_manager.record_script_run(script_name)
            except Exception:
                pass

            root.after(0, lambda: _finish(f"Script {selected_file} ran successfully.", '#4CAF50'))
        except Exception as e:
            root.after(0, lambda err=e: _finish(f"An error occurred: {err}", 'red'))

    threading.Thread(target=_run_in_thread, daemon=True).start()

def choose_csv_file():
    """
    Open a file dialog to select a CSV file.
    """
    is_valid, license_message = licensing_manager.is_license_valid()
    if not is_valid:
        messagebox.showerror("License Error", f"CSV feature requires a valid license.\n\nDetails: {license_message}")
        return
    if not licensing_manager.is_feature_enabled("csv_import"):
        messagebox.showerror("Feature Not Available", "CSV import feature is not available in your current license.")
        return
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        csv_file_label.config(text=f"Selected: {os.path.basename(file_path)}", foreground=colors['success'])
        selected_csv.set(file_path)
    else:
        csv_file_label.config(text="No CSV file selected", foreground=colors['muted'])
        selected_csv.set('')

# Headless mode: allow sending report without launching UI
if len(sys.argv) > 1 and sys.argv[1] == "--send-if-month-end":
    try:
        usage_init(config_manager.get_smtp_config(), DATA_DIR)  
        send_if_month_end()
    except Exception:
        pass
    sys.exit(0)

# User Interface - Version 4 (Responsive Layout)
root = tb.Window(themename=config_manager.get_theme())  # United theme by default
root.title("TRUETAG v4.0")
root.geometry(config_manager.get_window_geometry() or "500x680+100+100")  # Restore saved geometry or use default
root.resizable(True, True)  # Enable window resizing for different screen resolutions
root.iconbitmap(icon_path)

# Set minimum window size for usability
root.minsize(450, 600)

# Initialize usage reporter using loaded config
try:
    usage_init(config_manager.get_smtp_config(), DATA_DIR)
except Exception:
    pass


# Install Windows Task Scheduler job on first run (once)
def _install_daily_task_if_needed():
    try:
        if config_manager.config.get("auto_report_task_installed"):
            return
        pythonw = sys.executable
        # If packaged by PyInstaller, prefer running current exe with the flag
        if getattr(sys, 'frozen', False):
            program = sys.executable
            args = " --send-if-month-end"
        else:
            program = pythonw
            this_file = os.path.abspath(__file__)
            args = f' "{this_file}" --send-if-month-end'

        task_name = "TRUETAG Auto Monthly Report"
        import subprocess
        # Create or update task to run daily at 23:55
        cmd = [
            "schtasks", "/Create", "/SC", "DAILY", "/TN", task_name,
            "/TR", f'"{program}{args}"', "/ST", "23:55", "/F", "/RL", "LIMITED"
        ]
        subprocess.run(cmd, capture_output=True)
        config_manager.config["auto_report_task_installed"] = True
        config_manager.save_main_config()
    except Exception:
        pass

_install_daily_task_if_needed()

# Center window if no saved geometry
if not config_manager.get_window_geometry():
    try:
        root.update_idletasks()
        w = 500
        h = 680
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
    except Exception:
        pass

# Modern Professional Styling for Version 4 - Larger fonts, less spacing
font_title = ("Segoe UI", 28, "bold")
font_subtitle = ("Segoe UI", 12, "normal")
font_label = ("Segoe UI", 12, "bold")
font_input = ("Segoe UI", 11, "normal")
font_button = ("Segoe UI", 12, "bold")
font_result = ("Segoe UI", 12, "normal")
font_status = ("Segoe UI", 10, "normal")

# Modern color scheme
colors = {
    'primary': '#2E86AB',      # Professional blue
    'secondary': '#A23B72',    # Accent purple
    'success': '#28A745',      # Success green
    'warning': '#FFC107',      # Warning amber
    'danger': '#DC3545',       # Error red
    'light': '#F8F9FA',        # Light background
    'dark': '#343A40',         # Dark text
    'muted': '#6C757D'        # Muted text
}

# Responsive Main Frame with compact styling
main_frame = ttk.Frame(root, padding=(20, 15))
main_frame.pack(fill=tk.BOTH, expand=True)

# Configure root background
root.configure(bg='#F8F9FA')

# Configure grid weights for responsive layout
main_frame.columnconfigure(0, weight=1)

# Modern Header Card
header_card = ttk.Frame(main_frame, relief='flat', borderwidth=0)
header_card.pack(fill=tk.X, pady=(0, 10))

# Header content with compact styling
header_content = ttk.Frame(header_card)
header_content.pack(fill=tk.X, padx=15, pady=10)

# Logo and Title with better alignment
title_container = ttk.Frame(header_content)
title_container.pack(fill=tk.X)

# Load and display logo if available with larger size
if os.path.exists(logo_path):
    try:
        from PIL import Image, ImageTk
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((70, 70), Image.LANCZOS)  # Increased from 50x50 to 70x70
        logo_photo = ImageTk.PhotoImage(logo_image)
        logo_label = ttk.Label(title_container, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.pack(side=tk.LEFT, padx=(0, 15))  # Increased padding for larger logo
    except Exception:
        pass

# Title section with modern typography
title_section = ttk.Frame(title_container)
title_section.pack(side=tk.LEFT, fill=tk.X, expand=True)

title_label = ttk.Label(title_section, text=f"TrueTag v{APP_VERSION}", font=font_title, foreground=colors['dark'])
title_label.pack(anchor='w')

subtitle_label = ttk.Label(title_section, text="Smart Tag Generator", font=font_subtitle, foreground=colors['muted'])
subtitle_label.pack(anchor='w', pady=(1, 0))

# --- Menu bar ---
menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open CSV...\tCtrl+O", command=lambda: (use_csv.set(True), toggle_csv_selection(), choose_csv_file()))
file_menu.add_separator()
file_menu.add_command(label="Exit\tCtrl+Q", command=lambda: root.event_generate("<<AppQuit>>"))
menubar.add_cascade(label="File", menu=file_menu)

def _apply_theme(name):
    try:
        root.style.theme_use(name)
        config_manager.update_runtime(theme=name)
    except Exception as e:
        messagebox.showerror("Theme Error", f"Cannot apply theme '{name}': {e}")

view_menu = tk.Menu(menubar, tearoff=0)
themes_menu = tk.Menu(view_menu, tearoff=0)
for theme_name in sorted(tb.Style().theme_names()):
    themes_menu.add_command(label=theme_name, command=lambda n=theme_name: _apply_theme(n))
view_menu.add_cascade(label="Theme", menu=themes_menu)
menubar.add_cascade(label="View", menu=view_menu)

def _show_about():
    messagebox.showinfo(
        f"About TrueTag v{APP_VERSION}",
        f"TrueTag Loader v{APP_VERSION}\n\nEnhanced AutoLISP script runner for BricsCAD\nwith improved UI and usage reporting.\n\nFeatures:\n\u2022 United theme by default\n\u2022 Enhanced user interface\n\u2022 Monthly usage reports\n\u2022 CSV file support\n\u2022 Keyboard shortcuts\n\n\u00a9 2025"
    )

def _test_email():
    """Test email functionality."""
    try:
        success, message = usage_test_email()
        if success:
            messagebox.showinfo("Test Email", message)
            _update_status("Test email sent successfully!", '#4CAF50')
        else:
            messagebox.showerror("Test Email Failed", message)
            _update_status("Test email failed", 'red')
    except Exception as e:
        messagebox.showerror("Test Email Error", f"Error testing email: {e}")
        _update_status("Test email error", 'red')

def _show_license_info():
    """Hiển thị thông tin license"""
    try:
        license_info = licensing_manager.get_license_info()
        trial_info = licensing_manager.get_trial_info()
        
        status_text = f"License Status: {license_info['status'].title()}\n"
        status_text += f"Valid: {'Yes' if license_info['is_valid'] else 'No'}\n"
        status_text += f"Message: {license_info['message']}\n\n"
        
        if license_info['license_key']:
            key = license_info['license_key']
            masked_key = key[:4] + "-XXXX-XXXX-" + key[-4:] if len(key) > 8 else "****"
            status_text += f"License Key: {masked_key}\n"
        
        if license_info['activation_date']:
            status_text += f"Activation Date: {license_info['activation_date'][:10]}\n"
        
        if license_info['expiry_date']:
            status_text += f"Expiry Date: {license_info['expiry_date'][:10]}\n"
        
        days_remaining = license_info['days_remaining']
        if days_remaining > 0:
            status_text += f"Days Remaining: {days_remaining}\n"
        elif days_remaining < 0:
            status_text += f"Grace Period: {abs(days_remaining)} days\n"
        
        status_text += f"\nMachine ID: {license_info['machine_id']}\n\n"
        
        status_text += "Available Features:\n"
        features = license_info['features']
        
        # Handle both dict and list formats
        if isinstance(features, list):
            # If features is a list, show all as enabled
            for feature in features:
                status_text += f"  • {feature}: ✓\n"
        elif isinstance(features, dict):
            # If features is a dict, check enabled status
            for feature, enabled in features.items():
                status_text += f"  • {feature}: {'✓' if enabled else '✗'}\n"
        else:
            status_text += "  • Features information not available\n"
        
        if license_info['status'] == 'trial':
            status_text += f"\nTrial Information:\n"
            status_text += f"  • Trial Duration: {trial_info['trial_days']} days\n"
            status_text += f"  • Trial Used: {'Yes' if trial_info['trial_used'] else 'No'}\n"
            status_text += f"  • Grace Period: {trial_info['grace_period_days']} days\n"
        
        messagebox.showinfo("License Information", status_text)
    except Exception as e:
        messagebox.showerror("License Info Error", f"Error getting license info: {e}")

def _activate_license():
    """Cửa sổ kích hoạt license"""
    try:
        # Tạo cửa sổ con cho license activation
        license_window = tb.Toplevel(root)
        license_window.title("Activate License")
        license_window.geometry("500x300+200+200")
        license_window.resizable(False, False)
        license_window.iconbitmap(icon_path)
        
        # Make window modal
        license_window.transient(root)
        license_window.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(license_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="License Activation", font=font_title)
        title_label.pack(pady=(0, 20))
        
        # License key input
        key_frame = ttk.Frame(main_frame)
        key_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(key_frame, text="License Key:", font=font_label).pack(anchor='w')
        license_key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=license_key_var, font=font_input, width=50)
        key_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Info label
        info_label = ttk.Label(main_frame, text="Enter your license key to activate full features", 
                              font=font_subtitle, foreground=colors['muted'])
        info_label.pack(pady=(0, 20))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def activate_license_key():
            license_key = license_key_var.get().strip()
            if not license_key:
                messagebox.showwarning("Invalid Input", "Please enter a license key")
                return
            
            success, message = licensing_manager.activate_license(license_key)
            if success:
                messagebox.showinfo("Activation Successful", message)
                license_window.destroy()
                _update_status("License activated successfully!", colors['success'])
            else:
                messagebox.showerror("Activation Failed", message)
        
        # Buttons
        ttk.Button(button_frame, text="Activate", command=activate_license_key, 
                  bootstyle=SUCCESS, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=license_window.destroy, 
                  bootstyle=SECONDARY, width=15).pack(side=tk.LEFT)
        
        # Focus on entry
        key_entry.focus()
        
    except Exception as e:
        messagebox.showerror("License Activation Error", f"Error opening activation window: {e}")

# Reset trial function removed for security

# License menu
license_menu = tk.Menu(menubar, tearoff=0)
license_menu.add_command(label="License Information", command=_show_license_info)
license_menu.add_command(label="Activate License", command=_activate_license)
# Reset trial menu item removed for security
menubar.add_cascade(label="License", menu=license_menu)

help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="Test Email", command=_test_email)
help_menu.add_separator()
help_menu.add_command(label="About", command=_show_about)
menubar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menubar)

# Modern Script Category Card
category_card = ttk.LabelFrame(main_frame, text="Script Category", padding=15, relief='flat')
category_card.pack(fill=tk.X, pady=(0, 8))

category_label = ttk.Label(category_card, text="Select Category:", font=font_label)
category_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

selected_category = tk.StringVar()
category_menu = ttk.Combobox(category_card, textvariable=selected_category, state="readonly", width=25, font=font_input)
category_menu['values'] = list(SCRIPT_CATEGORIES.keys())
category_menu.grid(row=0, column=1, sticky='ew', pady=5, padx=(0, 15))
category_menu.current(0)  # Set default selection to the first category

# Tooltip for category menu
ToolTip(category_menu, text="Choose a script category to load scripts from")

category_card.columnconfigure(1, weight=1)

# Bind the category selection to load scripts
def on_category_change(event):
    selected = selected_category.get()
    load_available_scripts(selected)

category_menu.bind("<<ComboboxSelected>>", on_category_change)

def on_script_change(event):
    script_name = selected_script.get()
    if script_name and script_name != 'No Scripts Available':
        _update_status(f"Selected: {script_name}", colors['muted'])

# Modern Script Selection Card
script_card = ttk.LabelFrame(main_frame, text="Available Drawing Types", padding=15, relief='flat')
script_card.pack(fill=tk.X, pady=(0, 8))

script_label = ttk.Label(script_card, text="Script Selection:", font=font_label)
script_label.grid(row=0, column=0, sticky='w', padx=(0, 10), pady=5)

selected_script = tk.StringVar()
script_menu = ttk.Combobox(script_card, textvariable=selected_script, state="readonly", width=35, font=font_input)
script_menu.grid(row=0, column=1, sticky='ew', pady=5, padx=(0, 15))

# Bind script selection after script_menu is created
script_menu.bind("<<ComboboxSelected>>", on_script_change)

# Tooltip for script menu
ToolTip(script_menu, text="Choose a script to run")

script_card.columnconfigure(1, weight=1)

# Modern CSV Options Card
csv_card = ttk.LabelFrame(main_frame, text="CSV File Options", padding=15, relief='flat')
csv_card.pack(fill=tk.X, pady=(0, 8))

last_selections = config_manager.get_last_selections()
use_csv = tk.BooleanVar(value=bool(last_selections.get("csv_enabled", False)))

# CSV checkbox with compact styling
csv_checkbox_frame = ttk.Frame(csv_card)
csv_checkbox_frame.pack(fill=tk.X, pady=(0, 5))

use_csv_checkbox = ttk.Checkbutton(csv_checkbox_frame, text="Enable CSV File Input", variable=use_csv, command=lambda: toggle_csv_selection())
use_csv_checkbox.pack(anchor='w')

# Tooltip for CSV checkbox
ToolTip(use_csv_checkbox, text="Check to run the script with a CSV file")

def toggle_csv_selection():
    """
    Enable or disable CSV file selection based on the checkbox state.
    """
    if use_csv.get():
        choose_csv_button.config(state=NORMAL)
        csv_file_label.config(foreground=colors['muted'])
    else:
        choose_csv_button.config(state=DISABLED)
        csv_file_label.config(text="No CSV file selected", foreground=colors['muted'])
        selected_csv.set('')

# CSV file selection section
csv_selection_frame = ttk.Frame(csv_card)
csv_selection_frame.pack(fill=tk.X, pady=(3, 0))

csv_file_label = ttk.Label(csv_selection_frame, text="No CSV file selected", font=font_input, foreground=colors['muted'])
csv_file_label.pack(side=tk.LEFT, padx=(0, 10))

choose_csv_button = ttk.Button(csv_selection_frame, text="Browse CSV File", command=choose_csv_file, bootstyle=PRIMARY, state=DISABLED)
choose_csv_button.pack(side=tk.RIGHT)

# Tooltip for CSV button
ToolTip(choose_csv_button, text="Select a CSV file to use with the script")

# Store the path of the selected CSV file
selected_csv = tk.StringVar()

# Modern Action Section
action_section = ttk.Frame(main_frame)
action_section.pack(fill=tk.X, pady=(15, 10))

# Professional Run button
run_button = ttk.Button(action_section, text="▶ Run Script", command=run_selected_script, bootstyle=SUCCESS, width=30)
run_button.pack()

# Tooltip for Run button
ToolTip(run_button, text="Run the selected script in BricsCAD")

# Progress bar
progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
progress_bar.pack_forget()  # Hide it initially

# Modern Result Section
result_section = ttk.Frame(main_frame)
result_section.pack(fill=tk.X, pady=(8, 10))

result_label = ttk.Label(result_section, text="", wraplength=450, font=font_result, anchor='center', foreground=colors['dark'])
result_label.pack(fill=tk.X)
result_label.bind("<Configure>", lambda e: result_label.config(wraplength=max(1, e.width - 20)))

# Responsive layout with grid weights
main_frame.columnconfigure(0, weight=1)
category_card.columnconfigure(1, weight=1)
script_card.columnconfigure(1, weight=1)
csv_card.columnconfigure(0, weight=1)

# Compact Dock Panel
dock_frame = ttk.Frame(root, relief='flat', borderwidth=0)
dock_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=(0, 1))

# Dock content with minimal spacing
dock_content = ttk.Frame(dock_frame)
dock_content.pack(fill=tk.X, padx=8, pady=3)

# Left side - Empty space (removed status indicators)
status_indicators_frame = ttk.Frame(dock_content)
status_indicators_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Right side - Application status
app_status_frame = ttk.Frame(dock_content)
app_status_frame.pack(side=tk.RIGHT)

# License status label (hidden)
license_status_label = ttk.Label(app_status_frame, text="", font=font_status, foreground=colors['muted'])
# license_status_label.pack(anchor='e')  # Hidden as requested

# App version label
app_status_label = ttk.Label(app_status_frame, text=f"TRUETAG v{APP_VERSION}", font=font_status, foreground=colors['primary'])
app_status_label.pack(anchor='e')

# Update license status in dock
def update_license_status():
    try:
        license_info = licensing_manager.get_license_info()
        status_text = f"License: {license_info['status'].title()}"
        if license_info['days_remaining'] > 0:
            status_text += f" ({license_info['days_remaining']}d)"
        elif license_info['days_remaining'] < 0:
            status_text += f" (Grace: {abs(license_info['days_remaining'])}d)"
        
        license_status_label.config(text=status_text)
        
        # Update color based on status
        if license_info['is_valid']:
            if license_info['status'] == 'licensed':
                license_status_label.config(foreground=colors['success'])
            else:
                license_status_label.config(foreground=colors['warning'])
        else:
            license_status_label.config(foreground=colors['danger'])
            
    except Exception:
        license_status_label.config(text="License: Unknown", foreground=colors['muted'])

# Update license status after UI is ready
root.after(1000, update_license_status)

# Modern Status Bar (for dynamic messages)
status_var = tk.StringVar()
status_var.set("")
status_bar = ttk.Label(root, textvariable=status_var, relief='flat', anchor='w', font=font_status, padding=(8, 4), background=colors['light'])

root.bind_all('<Control-o>', lambda e: (use_csv.set(True), toggle_csv_selection(), choose_csv_file()))
root.bind_all('<Control-r>', lambda e: run_selected_script())
root.bind_all('<Control-q>', lambda e: root.event_generate("<<AppQuit>>"))

def _update_status(text, color=None):
    status_var.set(text)
    try:
        if text:
            # Show the status bar only when there is text to display
            if not status_bar.winfo_ismapped():
                status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            # Hide the status bar when there is no message
            status_bar.pack_forget()
        if color:
            status_bar.configure(foreground=color)
    except Exception:
        pass

def _persist_state_before_exit():
    try:
        # Save runtime settings including window geometry
        config_manager.update_runtime(
            window_geometry=root.winfo_geometry(),
            last_category=selected_category.get() if selected_category.get() in SCRIPT_CATEGORIES else None,
            last_script=selected_script.get(),
            last_csv_path=selected_csv.get(),
            csv_enabled=bool(use_csv.get())
        )
    except Exception:
        pass

def _on_app_quit(event=None):
    _persist_state_before_exit()
    try:
        usage_shutdown()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        os._exit(0)

root.bind("<<AppQuit>>", _on_app_quit)
root.protocol("WM_DELETE_WINDOW", _on_app_quit)

# Initial load of scripts based on default category
if last_selections.get("category") in SCRIPT_CATEGORIES:
    try:
        category_menu.set(last_selections.get("category"))
        load_available_scripts(category_menu.get())
    except Exception:
        load_available_scripts(category_menu.get())
else:
    load_available_scripts(category_menu.get())

if last_selections.get("script"):
    try:
        selected_script.set(last_selections.get("script"))
    except Exception:
        pass

if last_selections.get("csv_path"):
    selected_csv.set(last_selections.get("csv_path"))
    csv_file_label.config(text=f"Selected: {os.path.basename(selected_csv.get())}", foreground=colors['success'])
        # Status indicators removed
if use_csv.get():
    choose_csv_button.config(state=NORMAL)
    # Status indicators removed
else:
    choose_csv_button.config(state=DISABLED)
    # Status indicators removed

# Check license validity on startup (Background) - Moved here to ensure _update_status is defined
def _check_license_async():
    try:
        # Use root.after for thread-safe UI update
        root.after(0, lambda: _update_status("Checking license...", colors['primary']))
        is_valid, license_message = licensing_manager.is_license_valid()
        
        if not is_valid:
            # Show license warning
            root.after(100, lambda: messagebox.showwarning(
                "License Warning", 
                f"License issue detected: {license_message}\n\n"
                "The application will run with limited features.\n"
                "Please activate a valid license to use all functions."
            ))
            root.after(200, lambda: _update_status(f"Issue: {license_message}", colors['warning']))
            
            # Disable functionality
            root.after(300, lambda: run_button.config(state=DISABLED))
        else:
            root.after(200, lambda: _update_status(f"License: {license_message}", colors['success']))
            root.after(300, lambda: run_button.config(state=NORMAL))
        
        # Update dock status
        root.after(500, update_license_status)
    except Exception as e:
        print(f"License check error: {e}")
        root.after(200, lambda: _update_status("License check failed", colors['danger']))

# Start license check in background
threading.Thread(target=_check_license_async, daemon=True).start()

# Start the main loop
root.mainloop()
