"""
License Generator for TRUETAG v4.0
Tạo và quản lý license keys
"""

import os
import json
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import uuid
from version import APP_VERSION

class LicenseGenerator:
    """Generator để tạo license keys cho TRUETAG"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.license_db_file = os.path.join(data_dir, 'license_database.json')
        self.config_file = os.path.join(data_dir, 'license_config.json')
        
        # Load configuration
        self.config = self._load_config()
        
        # Load license database
        self.license_db = self._load_license_db()
        
        # License types và features
        self.license_types = {
            "trial": {
                "duration_days": 30,
                "features": ["basic_scripts", "csv_import"],
                "description": "30-day trial license",
                "max_uses": 1
            },
            "basic": {
                "duration_days": 365,
                "features": ["basic_scripts", "csv_import"],
                "description": "Basic license - 1 year",
                "max_uses": 1
            },
            "professional": {
                "duration_days": 365,
                "features": ["basic_scripts", "csv_import", "advanced_scripts", "batch_processing"],
                "description": "Professional license - 1 year",
                "max_uses": 1
            },
            "enterprise": {
                "duration_days": 365,
                "features": ["basic_scripts", "csv_import", "advanced_scripts", "batch_processing", "api_access", "priority_support", "cloud_sync"],
                "description": "Enterprise license - 1 year",
                "max_uses": 1
            },
            "demo": {
                "duration_days": 7,
                "features": ["basic_scripts", "csv_import"],
                "description": "7-day demo license",
                "max_uses": 1
            },
            "developer": {
                "duration_days": 30,
                "features": ["basic_scripts", "csv_import", "advanced_scripts", "batch_processing", "api_access"],
                "description": "Developer license - 30 days",
                "max_uses": 3
            }
        }
    
    def _load_config(self) -> Dict:
        """Load cấu hình license generator"""
        default_config = {
            "product_key": "TRUETAG-V4",
            "version": APP_VERSION,
            "secret_key": "TRUETAG-SECRET-2025",
            "license_prefix": "TRUETAG",
            "key_length": 4,
            "key_count": 5,
            "encryption_salt": "TRUETAG-SALT-2025"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            else:
                # Save default config
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def _load_license_db(self) -> Dict:
        """Load database license"""
        default_db = {
            "licenses": {},
            "statistics": {
                "total_generated": 0,
                "total_activated": 0,
                "by_type": {},
                "created_date": datetime.now().isoformat()
            }
        }
        
        try:
            if os.path.exists(self.license_db_file):
                with open(self.license_db_file, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                    default_db.update(db)
            else:
                # Save default database
                with open(self.license_db_file, 'w', encoding='utf-8') as f:
                    json.dump(default_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading license database: {e}")
        
        return default_db
    
    def _save_license_db(self):
        """Lưu database license"""
        try:
            with open(self.license_db_file, 'w', encoding='utf-8') as f:
                json.dump(self.license_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving license database: {e}")
    
    def generate_license_key(self) -> str:
        """Tạo license key mới"""
        # Format: TRUETAG-XXXX-XXXX-XXXX-XXXX
        prefix = self.config["license_prefix"]
        key_length = self.config["key_length"]
        key_count = self.config["key_count"]
        
        # Generate random segments
        segments = []
        for i in range(key_count):
            segment = ''.join(random.choices(string.ascii_uppercase + string.digits, k=key_length))
            segments.append(segment)
        
        license_key = f"{prefix}-{'-'.join(segments)}"
        return license_key
    
    def create_license(self, license_type: str, customer_info: Dict = None, 
                      custom_duration: int = None, notes: str = "") -> Tuple[bool, str, Dict]:
        """
        Tạo license mới
        Returns: (success, message, license_data)
        """
        try:
            # Validate license type
            if license_type not in self.license_types:
                return False, f"Invalid license type: {license_type}", {}
            
            # Generate unique license key
            license_key = self.generate_license_key()
            
            # Check if key already exists
            while license_key in self.license_db["licenses"]:
                license_key = self.generate_license_key()
            
            # Get license type info
            type_info = self.license_types[license_type]
            
            # Calculate expiry date
            duration_days = custom_duration or type_info["duration_days"]
            expiry_date = datetime.now() + timedelta(days=duration_days)
            
            # Create license data
            license_data = {
                "license_key": license_key,
                "license_type": license_type,
                "status": "active",
                "created_date": datetime.now().isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "duration_days": duration_days,
                "features": type_info["features"].copy(),
                "customer_info": customer_info or {},
                "notes": notes,
                "max_uses": type_info["max_uses"],
                "current_uses": 0,
                "activations": [],
                "checksum": ""
            }
            
            # Calculate checksum
            license_data["checksum"] = self._calculate_license_checksum(license_data)
            
            # Add to database
            self.license_db["licenses"][license_key] = license_data
            
            # Update statistics
            self.license_db["statistics"]["total_generated"] += 1
            if license_type not in self.license_db["statistics"]["by_type"]:
                self.license_db["statistics"]["by_type"][license_type] = 0
            self.license_db["statistics"]["by_type"][license_type] += 1
            
            # Save database
            self._save_license_db()
            
            return True, f"License created successfully: {license_key}", license_data
            
        except Exception as e:
            return False, f"Error creating license: {e}", {}
    
    def validate_license(self, license_key: str, machine_id: str = None) -> Tuple[bool, str, Dict]:
        """
        Validate license key
        Returns: (valid, message, license_data)
        """
        try:
            # Check if license exists
            if license_key not in self.license_db["licenses"]:
                return False, "License key not found", {}
            
            license_data = self.license_db["licenses"][license_key]
            
            # Check license status
            if license_data["status"] != "active":
                return False, f"License is {license_data['status']}", license_data
            
            # Check expiry date
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            if datetime.now() > expiry_date:
                return False, "License has expired", license_data
            
            # Validate integrity before trusting machine bindings or usage data.
            stored_checksum = license_data.get("checksum", "")
            calculated_checksum = self._calculate_license_checksum(license_data)
            if stored_checksum != calculated_checksum:
                return False, "License integrity check failed", license_data

            # A machine that is already bound must remain valid even when the
            # activation limit has been reached.
            if machine_id:
                activations = license_data.get("activations", [])
                if activations:
                    # Check if machine is already activated
                    for activation in activations:
                        if activation["machine_id"] == machine_id:
                            return True, "License validated successfully", license_data
                    
                    # Check if we can add new activation
                    if len(activations) >= license_data["max_uses"]:
                        return False, "Maximum activations reached", license_data
            elif license_data["current_uses"] >= license_data["max_uses"]:
                return False, "License usage limit exceeded", license_data
            
            return True, "License validated successfully", license_data
            
        except Exception as e:
            return False, f"Validation error: {e}", {}
    
    def activate_license(self, license_key: str, machine_id: str, customer_name: str = "") -> Tuple[bool, str]:
        """
        Activate license on machine
        Returns: (success, message)
        """
        try:
            # Validate license first
            is_valid, message, license_data = self.validate_license(license_key, machine_id)
            if not is_valid:
                return False, f"License validation failed: {message}"
            
            # Check if already activated on this machine
            activations = license_data.get("activations", [])
            for activation in activations:
                if activation["machine_id"] == machine_id:
                    return True, "License already activated on this machine"
            
            # Add new activation
            activation_data = {
                "machine_id": machine_id,
                "activation_date": datetime.now().isoformat(),
                "customer_name": customer_name,
                "ip_address": "unknown",  # Could be added if needed
                "user_agent": "TRUETAG-v4.0"
            }
            
            activations.append(activation_data)
            license_data["activations"] = activations
            license_data["current_uses"] = len(activations)
            
            # Update database
            self.license_db["licenses"][license_key] = license_data
            self.license_db["statistics"]["total_activated"] += 1
            
            self._save_license_db()
            
            return True, "License activated successfully"
            
        except Exception as e:
            return False, f"Activation error: {e}"
    
    def _calculate_license_checksum(self, license_data: Dict) -> str:
        """Tính checksum cho license"""
        # Create string from key data (excluding checksum itself)
        data_str = f"{license_data['license_key']}{license_data['license_type']}{license_data['expiry_date']}{self.config['secret_key']}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def get_license_info(self, license_key: str) -> Dict:
        """Lấy thông tin chi tiết của license"""
        if license_key in self.license_db["licenses"]:
            return self.license_db["licenses"][license_key]
        return {}
    
    def list_licenses(self, license_type: str = None, status: str = None) -> List[Dict]:
        """Liệt kê tất cả license với filter"""
        licenses = []
        
        for key, data in self.license_db["licenses"].items():
            # Apply filters
            if license_type and data["license_type"] != license_type:
                continue
            if status and data["status"] != status:
                continue
            
            # Add summary info
            license_summary = {
                "license_key": key,
                "license_type": data["license_type"],
                "status": data["status"],
                "created_date": data["created_date"],
                "expiry_date": data["expiry_date"],
                "current_uses": data["current_uses"],
                "max_uses": data["max_uses"],
                "customer_info": data.get("customer_info", {}),
                "notes": data.get("notes", "")
            }
            licenses.append(license_summary)
        
        # Sort by created date (newest first)
        licenses.sort(key=lambda x: x["created_date"], reverse=True)
        return licenses
    
    def update_license_status(self, license_key: str, status: str) -> Tuple[bool, str]:
        """Cập nhật trạng thái license"""
        try:
            if license_key not in self.license_db["licenses"]:
                return False, "License not found"
            
            valid_statuses = ["active", "inactive", "expired", "revoked"]
            if status not in valid_statuses:
                return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            
            self.license_db["licenses"][license_key]["status"] = status
            self._save_license_db()
            
            return True, f"License status updated to {status}"
            
        except Exception as e:
            return False, f"Error updating status: {e}"
    
    def revoke_license(self, license_key: str, reason: str = "", admin_name: str = "") -> Tuple[bool, str]:
        """
        Thu hồi license (revoke)
        Returns: (success, message)
        """
        try:
            if license_key not in self.license_db["licenses"]:
                return False, "License not found"
            
            license_data = self.license_db["licenses"][license_key]
            
            # Check if already revoked
            if license_data["status"] == "revoked":
                return False, "License is already revoked"
            
            # Add revoke information
            revoke_info = {
                "revoked_date": datetime.now().isoformat(),
                "reason": reason,
                "admin_name": admin_name,
                "previous_status": license_data["status"]
            }
            
            # Update license data
            license_data["status"] = "revoked"
            license_data["revoke_info"] = revoke_info
            
            # Save database
            self._save_license_db()
            
            return True, f"License {license_key} has been revoked successfully"
            
        except Exception as e:
            return False, f"Error revoking license: {e}"
    
    def unrevoke_license(self, license_key: str, admin_name: str = "", reason: str = "") -> Tuple[bool, str]:
        """
        Khôi phục license đã bị revoke
        Returns: (success, message)
        """
        try:
            if license_key not in self.license_db["licenses"]:
                return False, "License not found"
            
            license_data = self.license_db["licenses"][license_key]
            
            # Check if license is revoked
            if license_data["status"] != "revoked":
                return False, "License is not revoked"
            
            # Check if license is expired
            expiry_date_str = license_data.get("expiry_date", "")
            if expiry_date_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_date_str)
                    if datetime.now() > expiry_date:
                        return False, "Cannot unrevoke expired license"
                except:
                    pass
            
            # Restore previous status or set to active
            previous_status = license_data.get("revoke_info", {}).get("previous_status", "active")
            license_data["status"] = previous_status
            
            # Add unrevoke information
            unrevoke_info = {
                "unrevoked_date": datetime.now().isoformat(),
                "admin_name": admin_name,
                "reason": reason
            }
            
            # Keep revoke history but add unrevoke info
            if "revoke_history" not in license_data:
                license_data["revoke_history"] = []
            
            if license_data.get("revoke_info"):
                license_data["revoke_history"].append(license_data["revoke_info"])
            
            license_data["unrevoke_info"] = unrevoke_info
            
            # Save database
            self._save_license_db()
            
            return True, f"License {license_key} has been unrevoked and restored to {previous_status}"
            
        except Exception as e:
            return False, f"Error unrevoking license: {e}"
    
    def get_revoked_licenses(self) -> List[Dict]:
        """Lấy danh sách license đã bị revoke"""
        try:
            revoked_licenses = []
            
            for license_key, license_data in self.license_db["licenses"].items():
                if license_data.get("status") == "revoked":
                    revoke_info = {
                        "license_key": license_key,
                        "license_type": license_data.get("license_type", ""),
                        "revoked_date": license_data.get("revoke_info", {}).get("revoked_date", ""),
                        "reason": license_data.get("revoke_info", {}).get("reason", ""),
                        "admin_name": license_data.get("revoke_info", {}).get("admin_name", ""),
                        "previous_status": license_data.get("revoke_info", {}).get("previous_status", ""),
                        "customer_info": license_data.get("customer_info", {}),
                        "expiry_date": license_data.get("expiry_date", "")
                    }
                    revoked_licenses.append(revoke_info)
            
            # Sort by revoked date (newest first)
            revoked_licenses.sort(key=lambda x: x["revoked_date"], reverse=True)
            return revoked_licenses
            
        except Exception as e:
            print(f"Error getting revoked licenses: {e}")
            return []
    
    def revoke_license_bulk(self, license_keys: List[str], reason: str = "", admin_name: str = "") -> Dict[str, str]:
        """
        Thu hồi nhiều license cùng lúc
        Returns: Dict with license_key -> result_message
        """
        results = {}
        
        for license_key in license_keys:
            success, message = self.revoke_license(license_key, reason, admin_name)
            results[license_key] = message
        
        return results
    
    def get_license_revoke_history(self, license_key: str) -> List[Dict]:
        """Lấy lịch sử revoke của license"""
        try:
            if license_key not in self.license_db["licenses"]:
                return []
            
            license_data = self.license_db["licenses"][license_key]
            history = []
            
            # Add current revoke info if exists
            if license_data.get("status") == "revoked" and license_data.get("revoke_info"):
                history.append(license_data["revoke_info"])
            
            # Add revoke history
            if license_data.get("revoke_history"):
                history.extend(license_data["revoke_history"])
            
            # Add unrevoke info if exists
            if license_data.get("unrevoke_info"):
                history.append({
                    "type": "unrevoke",
                    "date": license_data["unrevoke_info"]["unrevoked_date"],
                    "admin_name": license_data["unrevoke_info"]["admin_name"],
                    "reason": license_data["unrevoke_info"]["reason"]
                })
            
            # Sort by date
            history.sort(key=lambda x: x.get("date", x.get("revoked_date", "")), reverse=True)
            return history
            
        except Exception as e:
            print(f"Error getting revoke history: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Lấy thống kê license"""
        stats = self.license_db["statistics"].copy()
        
        # Add real-time stats
        total_licenses = len(self.license_db["licenses"])
        active_licenses = len([l for l in self.license_db["licenses"].values() if l["status"] == "active"])
        expired_licenses = len([l for l in self.license_db["licenses"].values() if l["status"] == "expired"])
        
        stats.update({
            "total_licenses": total_licenses,
            "active_licenses": active_licenses,
            "expired_licenses": expired_licenses,
            "last_updated": datetime.now().isoformat()
        })
        
        return stats
    
    def export_licenses(self, filename: str = None) -> str:
        """Export tất cả license ra file"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"licenses_export_{timestamp}.json"
            
            filepath = os.path.join(self.data_dir, filename)
            
            export_data = {
                "export_date": datetime.now().isoformat(),
                "total_licenses": len(self.license_db["licenses"]),
                "statistics": self.get_statistics(),
                "licenses": self.license_db["licenses"]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise Exception(f"Export error: {e}")
    
    def import_licenses(self, filepath: str) -> Tuple[bool, str]:
        """Import license từ file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if "licenses" not in import_data:
                return False, "Invalid license file format"
            
            imported_count = 0
            skipped_count = 0
            
            for license_key, license_data in import_data["licenses"].items():
                if license_key not in self.license_db["licenses"]:
                    self.license_db["licenses"][license_key] = license_data
                    imported_count += 1
                else:
                    skipped_count += 1
            
            self._save_license_db()
            
            return True, f"Imported {imported_count} licenses, skipped {skipped_count} existing"
            
        except Exception as e:
            return False, f"Import error: {e}"
    
    def get_license_types(self) -> Dict:
        """Lấy danh sách các loại license"""
        return self.license_types.copy()
    
    def create_bulk_licenses(self, license_type: str, count: int, 
                           customer_info: Dict = None, notes: str = "") -> List[Dict]:
        """Tạo nhiều license cùng lúc"""
        created_licenses = []
        
        for i in range(count):
            success, message, license_data = self.create_license(
                license_type, customer_info, notes=notes
            )
            if success:
                created_licenses.append(license_data)
            else:
                print(f"Failed to create license {i+1}: {message}")
        
        return created_licenses
