"""
Licensing Manager for TRUETAG v4.0
Quản lý license, activation và trial period
"""

import os
import json
import hashlib
import datetime
from typing import Dict, Optional, Tuple
import uuid
import base64
import winreg
import subprocess

class LicensingManager:
    """Quản lý licensing cho TRUETAG"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.license_file = os.path.join(data_dir, 'license.json')
        self.config_file = os.path.join(data_dir, 'license_config.json')
        
        # Load license configuration
        self.config = self._load_config()
        
        # Load current license
        self.license_data = self._load_license()
    
    def _load_config(self) -> Dict:
        """Load cấu hình licensing"""
        default_config = {
            "trial_days": 30,
            "grace_period_days": 7,
            "license_server": "https://api.truetag.com/license",
            "product_key": "TRUETAG-V4",
            "version": "4.0",
            "features": {
                "basic_scripts": True,
                "csv_import": True,
                "advanced_scripts": False,
                "batch_processing": False,
                "api_access": False
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            else:
                # Save default config
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading license config: {e}")
        
        return default_config
    
    def _load_license(self) -> Dict:
        """Load thông tin license hiện tại"""
        default_license = {
            "status": "trial",
            "license_key": "",
            "activation_date": "",
            "expiry_date": "",
            "machine_id": self._get_machine_id(),
            "features": self.config["features"].copy(),
            "trial_used": False,
            "last_check": "",
            "checksum": ""
        }
        
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    license_data = json.load(f)
                    # Merge with defaults
                    default_license.update(license_data)
                    # Verify license integrity
                    if not self._verify_license_integrity(default_license):
                        print("License integrity check failed, using trial mode")
                        default_license["status"] = "trial"
                        default_license["trial_used"] = False
            else:
                # Initialize trial license
                default_license = self._initialize_trial_license(default_license)
        except Exception as e:
            print(f"Error loading license: {e}")
            default_license = self._initialize_trial_license(default_license)
        
        return default_license
    
    def _get_machine_id(self) -> str:
        """Lấy Machine ID duy nhất của máy tính"""
        try:
            # Try to get machine GUID from Windows registry
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   r"SOFTWARE\Microsoft\Cryptography")
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                winreg.CloseKey(key)
                return hashlib.md5(machine_guid.encode()).hexdigest()[:16]
            except:
                # Fallback: use CPU serial + motherboard serial
                cpu_id = self._get_wmic_value("cpu", "ProcessorId")
                motherboard_id = self._get_wmic_value("baseboard", "SerialNumber")
                combined = f"{cpu_id}-{motherboard_id}"
                return hashlib.md5(combined.encode()).hexdigest()[:16]
        except:
            # Final fallback: use random UUID
            return str(uuid.uuid4()).replace('-', '')[:16]
    
    def _get_wmic_value(self, alias: str, property_name: str) -> str:
        """Lấy giá trị từ WMIC command"""
        try:
            result = subprocess.run(
                ['wmic', alias, 'get', property_name, '/value'],
                capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    if key.strip() == property_name:
                        return value.strip()
            return "unknown"
        except:
            return "unknown"
    
    def _initialize_trial_license(self, license_data: Dict) -> Dict:
        """Khởi tạo license trial"""
        license_data["status"] = "trial"
        license_data["activation_date"] = datetime.datetime.now().isoformat()
        license_data["expiry_date"] = (
            datetime.datetime.now() + 
            datetime.timedelta(days=self.config["trial_days"])
        ).isoformat()
        license_data["trial_used"] = True
        license_data["features"] = self.config["features"].copy()
        license_data["last_check"] = datetime.datetime.now().isoformat()
        license_data["checksum"] = self._calculate_checksum(license_data)
        
        self._save_license(license_data)
        return license_data
    
    def _calculate_checksum(self, license_data: Dict) -> str:
        """Tính toán checksum để bảo mật license"""
        # Create a string from license data excluding checksum itself
        data_str = f"{license_data['license_key']}{license_data['machine_id']}{license_data['status']}{license_data['expiry_date']}"
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _verify_license_integrity(self, license_data: Dict) -> bool:
        """Xác minh tính toàn vẹn của license"""
        try:
            stored_checksum = license_data.get("checksum", "")
            calculated_checksum = self._calculate_checksum(license_data)
            return stored_checksum == calculated_checksum
        except:
            return False
    
    def _save_license(self, license_data: Dict):
        """Lưu thông tin license"""
        try:
            # Update checksum before saving
            license_data["checksum"] = self._calculate_checksum(license_data)
            license_data["last_check"] = datetime.datetime.now().isoformat()
            
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving license: {e}")
    
    def is_license_valid(self) -> Tuple[bool, str]:
        """
        Kiểm tra license có hợp lệ không
        Returns: (is_valid, message)
        """
        try:
            # Check if license file exists
            if not os.path.exists(self.license_file):
                return False, "License file not found"
            
            # Check license integrity
            if not self._verify_license_integrity(self.license_data):
                return False, "License integrity check failed"
            
            # Check machine ID
            current_machine_id = self._get_machine_id()
            if self.license_data.get("machine_id") != current_machine_id:
                return False, "License is not valid for this machine"
            
            # Check expiry date
            if self.license_data.get("status") in ["trial", "licensed"]:
                expiry_date_str = self.license_data.get("expiry_date", "")
                if expiry_date_str:
                    try:
                        expiry_date = datetime.datetime.fromisoformat(expiry_date_str)
                        if datetime.datetime.now() > expiry_date:
                            # Check grace period
                            grace_period_end = expiry_date + datetime.timedelta(days=self.config["grace_period_days"])
                            if datetime.datetime.now() > grace_period_end:
                                return False, "License has expired"
                            else:
                                days_left = (grace_period_end - datetime.datetime.now()).days
                                return True, f"License expired, grace period: {days_left} days left"
                    except:
                        return False, "Invalid expiry date format"
            
            # Check license status
            status = self.license_data.get("status", "trial")
            if status == "trial":
                return True, "Trial license active"
            elif status == "licensed":
                return True, "Full license active"
            elif status == "expired":
                return False, "License has expired"
            else:
                return False, "Invalid license status"
                
        except Exception as e:
            return False, f"License validation error: {e}"
    
    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Kích hoạt license với key
        Returns: (success, message)
        """
        try:
            # Validate license key format
            if not self._validate_license_key_format(license_key):
                return False, "Invalid license key format"
            
            # Check if license key is already used on this machine
            if self.license_data.get("license_key") == license_key:
                return True, "License already activated on this machine"
            
            # Simulate license server validation (in real implementation, call actual server)
            validation_result = self._validate_license_with_server(license_key)
            if not validation_result["valid"]:
                return False, validation_result["message"]
            
            # Update license data
            self.license_data.update({
                "status": "licensed",
                "license_key": license_key,
                "activation_date": datetime.datetime.now().isoformat(),
                "expiry_date": validation_result.get("expiry_date", ""),
                "features": validation_result.get("features", self.config["features"].copy()),
                "trial_used": True
            })
            
            self._save_license(self.license_data)
            return True, "License activated successfully"
            
        except Exception as e:
            return False, f"Activation error: {e}"
    
    def _validate_license_key_format(self, license_key: str) -> bool:
        """Validate format của license key"""
        # Format: TRUETAG-XXXX-XXXX-XXXX-XXXX-XXXX (example)
        parts = license_key.split('-')
        if len(parts) != 6:
            return False
        
        # First part should be "TRUETAG"
        if parts[0] != "TRUETAG":
            return False
        
        # Remaining parts should be 4 characters each
        return all(len(part) == 4 for part in parts[1:])
    
    def _validate_license_with_server(self, license_key: str) -> Dict:
        """Validate license với server (simulation)"""
        # Trong implementation thật, sẽ gọi API server
        # Ở đây chỉ là simulation
        return {
            "valid": True,
            "message": "License validated successfully",
            "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
            "features": {
                "basic_scripts": True,
                "csv_import": True,
                "advanced_scripts": True,
                "batch_processing": True,
                "api_access": True
            }
        }
    
    def get_license_info(self) -> Dict:
        """Lấy thông tin license hiện tại"""
        is_valid, message = self.is_license_valid()
        
        return {
            "status": self.license_data.get("status", "trial"),
            "is_valid": is_valid,
            "message": message,
            "license_key": self.license_data.get("license_key", ""),
            "activation_date": self.license_data.get("activation_date", ""),
            "expiry_date": self.license_data.get("expiry_date", ""),
            "machine_id": self.license_data.get("machine_id", ""),
            "features": self.license_data.get("features", {}),
            "trial_used": self.license_data.get("trial_used", False),
            "days_remaining": self._get_days_remaining()
        }
    
    def _get_days_remaining(self) -> int:
        """Tính số ngày còn lại"""
        try:
            expiry_date_str = self.license_data.get("expiry_date", "")
            if expiry_date_str:
                expiry_date = datetime.datetime.fromisoformat(expiry_date_str)
                now = datetime.datetime.now()
                if expiry_date > now:
                    return (expiry_date - now).days
                else:
                    grace_period_end = expiry_date + datetime.timedelta(days=self.config["grace_period_days"])
                    if now <= grace_period_end:
                        return -(grace_period_end - now).days  # Negative for grace period
                    else:
                        return 0
        except:
            pass
        return 0
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Kiểm tra feature có được kích hoạt không"""
        is_valid, _ = self.is_license_valid()
        if not is_valid:
            # Trong trial hoặc expired, chỉ cho phép basic features
            return feature_name in ["basic_scripts", "csv_import"]
        
        features = self.license_data.get("features", {})
        return features.get(feature_name, False)
    
    def reset_trial(self) -> bool:
        """Reset trial license (chỉ dùng cho testing)"""
        try:
            if os.path.exists(self.license_file):
                os.remove(self.license_file)
            self.license_data = self._load_license()
            return True
        except Exception as e:
            print(f"Error resetting trial: {e}")
            return False
    
    def get_trial_info(self) -> Dict:
        """Lấy thông tin trial"""
        return {
            "trial_days": self.config["trial_days"],
            "trial_used": self.license_data.get("trial_used", False),
            "days_remaining": self._get_days_remaining(),
            "grace_period_days": self.config["grace_period_days"]
        }

