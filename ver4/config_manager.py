import os
import json
from datetime import datetime


class ConfigManager:
    """Manages application configuration with separate persistent and runtime settings."""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, 'config.json')
        self.runtime_path = os.path.join(base_dir, 'runtime_settings.json')
        
        # Load main config (SMTP, email settings, etc.)
        self.config = self._load_main_config()
        
        # Load runtime settings (UI state, window geometry, etc.)
        self.runtime = self._load_runtime_settings()
    
    def _load_main_config(self):
        """Load main configuration (SMTP, email settings) - rarely changes."""
        default_config = {
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": "",
            "smtp_use_tls": True,
            "email_from": "",
            "email_to": "",
            "email_subject_prefix": "TRUETAG",
            "last_report_month": "",
            "install_time": datetime.now().isoformat(),
            "run_count": 0,
            "run_history": []
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        default_config.update(data)
        except Exception:
            pass
        
        return default_config
    
    def _load_runtime_settings(self):
        """Load runtime settings (UI state) - changes frequently."""
        default_runtime = {
            "theme": "united",
            "window_geometry": "",
            "last_category": None,
            "last_script": None,
            "last_csv_path": "",
            "csv_enabled": False
        }
        
        try:
            if os.path.exists(self.runtime_path):
                with open(self.runtime_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        default_runtime.update(data)
        except Exception:
            pass
        
        return default_runtime
    
    def save_main_config(self):
        """Save main configuration (only when SMTP settings change)."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def save_runtime_settings(self):
        """Save runtime settings (UI state, window geometry)."""
        try:
            with open(self.runtime_path, 'w', encoding='utf-8') as f:
                json.dump(self.runtime, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def update_runtime(self, **kwargs):
        """Update runtime settings without touching main config."""
        for key, value in kwargs.items():
            if key in self.runtime:
                self.runtime[key] = value
        self.save_runtime_settings()
    
    def record_script_run(self, script_name):
        """Record a script run in main config (only when script actually runs)."""
        self.config["run_count"] = int(self.config.get("run_count", 0)) + 1
        hist = self.config.get("run_history", [])
        hist.append(datetime.now().isoformat())
        self.config["run_history"] = hist[-50:]  # Keep last 50 runs
        self.save_main_config()
    
    def get_smtp_config(self):
        """Get SMTP configuration for usage reporting."""
        return {
            "smtp_host": self.config.get("smtp_host"),
            "smtp_port": self.config.get("smtp_port", 587),
            "smtp_user": self.config.get("smtp_user"),
            "smtp_password": self.config.get("smtp_password"),
            "smtp_use_tls": self.config.get("smtp_use_tls", True),
            "email_from": self.config.get("email_from"),
            "email_to": self.config.get("email_to"),
            "email_subject_prefix": self.config.get("email_subject_prefix", "TRUETAG"),
            "last_report_month": self.config.get("last_report_month", "")
        }
    
    def update_smtp_config(self, **kwargs):
        """Update SMTP settings in main config."""
        for key, value in kwargs.items():
            if key in ["smtp_host", "smtp_port", "smtp_user", "smtp_password", 
                      "smtp_use_tls", "email_from", "email_to", "email_subject_prefix"]:
                self.config[key] = value
        self.save_main_config()
    
    def get_theme(self):
        """Get current theme from runtime settings."""
        return self.runtime.get("theme", "superhero")
    
    def get_window_geometry(self):
        """Get window geometry from runtime settings."""
        return self.runtime.get("window_geometry", "")
    
    def get_last_selections(self):
        """Get last user selections from runtime settings."""
        return {
            "category": self.runtime.get("last_category"),
            "script": self.runtime.get("last_script"),
            "csv_path": self.runtime.get("last_csv_path"),
            "csv_enabled": self.runtime.get("csv_enabled", False)
        }
