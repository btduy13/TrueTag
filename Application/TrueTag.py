import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import win32com.client
import os
import sys
from config import SCRIPT_CATEGORIES, RESOURCES_PATH

_plugin = None

def TRUETAG(args):
    """Command handler for TRUETAG command"""
    try:
        print("Starting TrueTag plugin...")
        global _plugin
        if _plugin is None:
            _plugin = TrueTagPlugin()
        _plugin.initialize()
        print("TrueTag plugin initialized successfully.")
        return True
    except Exception as e:
        print(f"Error in TRUETAG command: {e}")
        return False

class TrueTagPlugin:
    def __init__(self):
        self.root = None
        self.acad = None
        self.doc = None
        self.selected_category = None
        self.selected_script = None
        self.selected_csv = None
        self.use_csv = None
        
    def initialize(self):
        """Initialize BricsCAD connection and setup UI"""
        try:
            # Connect to BricsCAD
            self.acad = win32com.client.Dispatch("BricscadApp.AcadApplication")
            self.doc = self.acad.ActiveDocument
            if not self.doc:
                raise Exception("No active document found")
            
            # Create and show the main window
            self.create_main_window()
            
        except Exception as e:
            print(f"Error initializing BricsCAD: {e}")
            raise
            
    def create_main_window(self):
        """Create the main application window"""
        self.root = tb.Window(themename="superhero")
        self.root.title("TRUETAG")
        self.root.geometry("400x600")
        self.root.resizable(True, True)
        
        if os.path.exists(os.path.join(RESOURCES_PATH, "logo.ico")):
            self.root.iconbitmap(os.path.join(RESOURCES_PATH, "logo.ico"))
            
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add header with logo if available
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        logo_path = os.path.join(RESOURCES_PATH, "logo.png")
        if os.path.exists(logo_path):
            from PIL import Image, ImageTk
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((50, 50), Image.ANTIALIAS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(header_frame, image=logo_photo)
            logo_label.image = logo_photo
            logo_label.pack(side=tk.LEFT, padx=(0, 10))
            
        # Title
        title_label = ttk.Label(header_frame, text="TRUE TAG LOADER", font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT, anchor='w')
        
        # Category selection
        category_frame = ttk.LabelFrame(main_frame, text="Script Category", padding=15)
        category_frame.pack(fill=tk.X, pady=10)
        
        self.selected_category = tk.StringVar()
        category_menu = ttk.Combobox(category_frame, textvariable=self.selected_category, 
                                   state="readonly", width=20, font=("Arial", 12))
        category_menu['values'] = list(SCRIPT_CATEGORIES.keys())
        category_menu.grid(row=0, column=1, sticky='w', pady=5)
        category_menu.current(0)
        
        # Script selection
        script_frame = ttk.LabelFrame(main_frame, text="Available Drawing Types", padding=15)
        script_frame.pack(fill=tk.X, pady=10)
        
        self.selected_script = tk.StringVar()
        self.script_menu = ttk.Combobox(script_frame, textvariable=self.selected_script, 
                                      state="readonly", width=40, font=("Arial", 12))
        self.script_menu.grid(row=0, column=1, sticky='ew', pady=5)
        
        # CSV options
        csv_frame = ttk.LabelFrame(main_frame, text="CSV Options", padding=15)
        csv_frame.pack(fill=tk.X, pady=10)
        
        self.use_csv = tk.BooleanVar()
        use_csv_checkbox = ttk.Checkbutton(csv_frame, text="Use CSV File", 
                                         variable=self.use_csv, 
                                         command=self.toggle_csv_selection)
        use_csv_checkbox.pack(anchor='w')
        
        self.selected_csv = tk.StringVar()
        self.csv_button = ttk.Button(csv_frame, text="Choose CSV File", 
                                   command=self.choose_csv_file, 
                                   state=DISABLED)
        self.csv_button.pack(pady=5)
        
        self.csv_label = ttk.Label(csv_frame, text="No CSV file selected", 
                                 font=("Arial", 10))
        self.csv_label.pack()
        
        # Run button
        self.run_button = ttk.Button(main_frame, text="Run Script", 
                                   command=self.run_selected_script, 
                                   style='success.TButton', 
                                   width=20)
        self.run_button.pack(pady=20)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor='w', 
                             font=("Arial", 10))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        category_menu.bind("<<ComboboxSelected>>", self.on_category_change)
        
        # Load initial scripts
        self.load_available_scripts()
        
        self.root.mainloop()
        
    def on_category_change(self, event):
        """Handle category selection change"""
        self.load_available_scripts()
        
    def load_available_scripts(self):
        """Load available scripts for the selected category"""
        try:
            category = self.selected_category.get()
            scripts_folder = SCRIPT_CATEGORIES[category]
            lisp_files = [f[:-4] for f in os.listdir(scripts_folder) if f.endswith(".lsp")]
            
            if lisp_files:
                self.selected_script.set(lisp_files[0])
                self.script_menu['values'] = lisp_files
                self.script_menu.config(state="readonly")
                self.status_var.set(f"Loaded {len(lisp_files)} scripts from {category}.")
            else:
                self.selected_script.set('No Scripts Available')
                self.script_menu['values'] = []
                self.script_menu.config(state="disabled")
                self.status_var.set(f"No scripts found in {category}.")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load script list: {e}")
            self.status_var.set("Error loading scripts.")
            
    def toggle_csv_selection(self):
        """Enable/disable CSV file selection"""
        if self.use_csv.get():
            self.csv_button.config(state=NORMAL)
            self.status_var.set("CSV usage enabled.")
        else:
            self.csv_button.config(state=DISABLED)
            self.csv_label.config(text="No CSV file selected")
            self.selected_csv.set('')
            self.status_var.set("CSV usage disabled.")
            
    def choose_csv_file(self):
        """Open file dialog to select CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.csv_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.selected_csv.set(file_path)
            self.status_var.set(f"CSV file selected: {os.path.basename(file_path)}")
        else:
            self.csv_label.config(text="No CSV file selected")
            self.selected_csv.set('')
            self.status_var.set("No CSV file selected.")
            
    def run_selected_script(self):
        """Run the selected script in BricsCAD"""
        try:
            selected_file = self.selected_script.get() + ".lsp"
            if selected_file == "No Scripts Available.lsp":
                messagebox.showwarning("No Script Selected", "Please select a script to run")
                return
                
            category = self.selected_category.get()
            file_path = os.path.join(SCRIPT_CATEGORIES[category], selected_file)
            file_path = file_path.replace("\\", "/")
            
            # Check CSV requirements
            if self.use_csv.get() and not self.selected_csv.get():
                messagebox.showwarning("CSV Required", "Please select a CSV file or disable CSV usage")
                return
                
            # Disable run button during execution
            self.run_button.config(state=DISABLED)
            self.status_var.set("Running script...")
            self.root.update_idletasks()
            
            # Run the script
            if self.use_csv.get():
                lisp_command = f'(load "{file_path}") (c:{self.selected_script.get()} "{self.selected_csv.get()}") '
            else:
                lisp_command = f'(load "{file_path}") (c:{self.selected_script.get()}) '
                
            self.doc.SendCommand(lisp_command + "\n")
            
            messagebox.showinfo("Success", f"Script {selected_file} ran successfully.")
            self.status_var.set("Script ran successfully.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.status_var.set("Error occurred during script execution.")
            
        finally:
            self.run_button.config(state=NORMAL) 