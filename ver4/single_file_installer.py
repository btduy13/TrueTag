import os
import sys
import shutil
import tempfile
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import threading

class SingleFileInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TrueTag v4.1.1 Installer")
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        self.setup_ui()
        
    def setup_ui(self):
        style = ttk.Style()
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="TrueTag v4.1.1", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(main_frame, text="BricsCAD Plugin Setup", font=("Helvetica", 10))
        desc_label.pack(pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(main_frame, text="Ready to install...", font=("Helvetica", 9))
        self.status_label.pack()
        
        self.install_btn = ttk.Button(main_frame, text="Install Now", command=self.start_installation)
        self.install_btn.pack(pady=20)
        
    def _update_status(self, text, progress=None):
        self.status_label.config(text=text)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()

    def start_installation(self):
        self.install_btn.config(state=tk.DISABLED)
        # Run installation in a separate thread to keep UI responsive
        threading.Thread(target=self.run_install_process, daemon=True).start()

    def run_install_process(self):
        try:
            # 1. Locate setup data
            if not getattr(sys, 'frozen', False):
                # Running as script
                base_path = os.path.dirname(os.path.abspath(__file__))
                setup_src = os.path.join(base_path, "TrueTag_Setup")
            else:
                # Running as frozen exe
                base_path = getattr(sys, '_MEIPASS')
                setup_src = os.path.join(base_path, "TrueTag_Setup")

            if not os.path.exists(setup_src):
                raise RuntimeError("Setup data not found! Please contact support.")

            # NEW: Kill any running instances and cleanup old files
            self._update_status("Cleaning up old versions...", 10)
            self._cleanup_old_version()

            # 2. Extract to temp
            self._update_status("Extracting temporary files...", 20)
            temp_dir = tempfile.mkdtemp(prefix="truetag_setup_")
            target_setup = os.path.join(temp_dir, "TrueTag_Setup")
            shutil.copytree(setup_src, target_setup)
            
            # 3. Run installation
            self._update_status("Integrating with BricsCAD...", 50)
            ps_script = os.path.join(target_setup, "install_plugin.ps1")
            
            # Execute PowerShell script
            # We use -ExecutionPolicy Bypass to ensure it runs
            process = subprocess.Popen(
                ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", ps_script],
                cwd=target_setup,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self._update_status("Installation successful!", 100)
                messagebox.showinfo("Success", "TrueTag has been successfully installed and integrated with BricsCAD.\nPlease restart BricsCAD to see the changes.")
                self.root.destroy()
            else:
                raise RuntimeError(f"Installation failed: {stderr or stdout}")

        except Exception as e:
            self._update_status("Error occurred", 0)
            messagebox.showerror("Installation Error", str(e))
            self.install_btn.config(state=tk.NORMAL)

    def _cleanup_old_version(self):
        """Vô hiệu hóa và xóa phiên bản cũ"""
        try:
            # 1. Kill TRUETAG processes
            subprocess.call(["taskkill", "/F", "/IM", "TRUETAG-v4.exe", "/T"], 
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # 2. Delete old exe in default AppData path
            old_exe = os.path.join(os.environ.get('APPDATA', ''), 'TrueTag', 'TRUETAG-v4.exe')
            if os.path.exists(old_exe):
                try:
                    os.remove(old_exe)
                except Exception as e:
                    print(f"Could not delete old exe: {e}")
        except Exception as e:
            print(f"Cleanup error: {e}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = SingleFileInstaller()
    app.run()
