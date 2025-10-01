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
from datetime import datetime
from usage_reporting import init as usage_init, record_run as usage_record, shutdown as usage_shutdown, test_email as usage_test_email, send_if_month_end
from config_manager import ConfigManager

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

# Dictionary to hold script categories and their corresponding folders
SCRIPT_CATEGORIES = {
    "PID": PID_SCRIPTS_FOLDER,
    "Position": POSITION_SCRIPTS_FOLDER,
    "TML": TML_SCRIPTS_FOLDER
}

def get_active_cad_application():
    """Ưu tiên BricsCAD, nếu không có thì thử các CAD khác.

    Thứ tự thử: BricsCAD → AutoCAD → ZWCAD → GStarCAD.
    Mỗi loại thử lấy phiên đang chạy (GetActiveObject), nếu không có thì Dispatch để mở mới.
    """
    ordered_prog_ids = [
        "BricscadApp.AcadApplication",
        "AutoCAD.Application",
        "ZWCAD.Application",
        "GStarCAD.Application",
    ]
    # Thử lấy phiên đang chạy trước
    for pid in ordered_prog_ids:
        try:
            return GetActiveObject(pid)
        except Exception:
            pass
    # Nếu không có phiên đang chạy, thử khởi động mới theo thứ tự
    for pid in ordered_prog_ids:
        try:
            return win32com.client.Dispatch(pid)
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
    Run the selected script in AutoCAD with the CSV file path if enabled.
    """
    try:
        category = selected_category.get()
        if category not in SCRIPT_CATEGORIES:
            messagebox.showwarning("No Category Selected", "Please select a script category.")
            # Status message removed
            return

        selected_file = selected_script.get() + ".lsp"
        if selected_file == "No Scripts Available.lsp" or script_menu['state'] == 'disabled':
            messagebox.showwarning("No Script Selected", "Please select a valid script to run.")
            # Status message removed
            return

        # Check if CSV usage is enabled
        if use_csv.get():
            csv_file_path = selected_csv.get()
            if not csv_file_path:
                messagebox.showwarning("CSV File Required", "Please select a CSV file or disable CSV usage.")
                # Status message removed
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
        # Status message removed

        root.update_idletasks()

        # Ưu tiên BricsCAD; nếu không có sẽ rơi xuống CAD khác
        acad = get_active_cad_application()
        if not acad:
            raise RuntimeError("Không tìm thấy CAD đang chạy hoặc khởi động được (BricsCAD/AutoCAD/ZWCAD/GStarCAD)")
        doc = acad.ActiveDocument

        # Load and run AutoLISP script with or without CSV path
        if csv_file_path:
            # If the script accepts the CSV file as an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()} "{csv_file_path}") '
        else:
            # If no CSV file is provided, do not pass an argument
            lisp_command = f'(load "{file_path}") (c:{selected_script.get()}) '

        # Record start time for run time tracking
        import time
        start_time = time.time()
        
        doc.SendCommand(lisp_command + "\n")
        
        # Calculate run time
        end_time = time.time()
        run_time_seconds = end_time - start_time

        # Record usage by module name (script name) with run time
        try:
            usage_record(selected_script.get(), run_time_seconds)
        except Exception:
            pass

        # Update run count and history only on successful script execution
        try:
            config_manager.record_script_run(selected_script.get())
        except Exception:
            pass

        result_label.config(text=f"Script {selected_file} ran successfully.", foreground='#4CAF50')
        # Status message removed
    except Exception as e:
        result_label.config(text=f"An error occurred: {e}", foreground='red')
        # Status message removed
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
        csv_file_label.config(text=f"Selected: {os.path.basename(file_path)}", foreground=colors['success'])
        selected_csv.set(file_path)
        # Status indicators removed
        # Status message removed
    else:
        csv_file_label.config(text="No CSV file selected", foreground=colors['muted'])
        selected_csv.set('')
        # Status indicators removed
        # Status message removed

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
root.geometry(config_manager.get_window_geometry() or "500x650+100+100")  # Restore saved geometry or use default
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
        h = 650
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

title_label = ttk.Label(title_section, text="TRUETAG", font=font_title, foreground=colors['dark'])
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
        "About TRUETAG v4.0",
        "TRUETAG Loader v4.0\n\nEnhanced AutoLISP script runner for BricsCAD\nwith improved UI and usage reporting.\n\nFeatures:\n• United theme by default\n• Enhanced user interface\n• Monthly usage reports\n• CSV file support\n• Keyboard shortcuts\n\n© 2025"
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

# Bind script selection to update dock status
def on_script_change(event):
    script_name = selected_script.get()
    # Status indicators removed

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
        # Status indicators removed
        # Status message removed
    else:
        choose_csv_button.config(state=DISABLED)
        csv_file_label.config(text="No CSV file selected", foreground=colors['muted'])
        # Status indicators removed
        selected_csv.set('')
        # Status message removed

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
ToolTip(run_button, text="Run the selected script in AutoCAD")

# Progress bar
progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
progress_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
progress_bar.pack_forget()  # Hide it initially

# Modern Result Section
result_section = ttk.Frame(main_frame)
result_section.pack(fill=tk.X, pady=(8, 10))

result_label = ttk.Label(result_section, text="", wraplength=450, font=font_result, anchor='center', foreground=colors['dark'])
result_label.pack()

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

app_status_label = ttk.Label(app_status_frame, text="TRUETAG v4.0", font=font_status, foreground=colors['primary'])
app_status_label.pack(anchor='e')

# Modern Status Bar (for dynamic messages)
status_var = tk.StringVar()
status_var.set("")
status_bar = ttk.Label(root, textvariable=status_var, relief='flat', anchor='w', font=font_status, padding=(8, 4), background=colors['light'])

# Keyboard shortcuts and app quit handling
def _on_quit_event(event=None):
    root.event_generate("<<AppQuit>>")

root.bind_all('<Control-o>', lambda e: (use_csv.set(True), toggle_csv_selection(), choose_csv_file()))
root.bind_all('<Control-r>', lambda e: run_selected_script())
root.bind_all('<Control-q>', _on_quit_event)

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
last_selections = config_manager.get_last_selections()
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

# Start the main loop
root.mainloop()
