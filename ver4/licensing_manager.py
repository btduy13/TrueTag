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
import requests
from urllib.parse import urljoin

class LicensingManager:
    """Quản lý licensing cho TRUETAG"""
    # Registry constants for persistent trial tracking
    REGISTRY_PATH = r"SOFTWARE\TrueTag"
    REG_TRIAL_START = "TrialStartDate"
    REG_MACHINE_FP = "MachineFingerprint"
    REG_TRIAL_USED = "TrialUsed"
    REG_APP_VERSION = "AppVersion"
    REG_CURRENT_VERSION = "CurrentInstalledVersion"

    def __init__(self, data_dir: str):
        self._session = requests.Session()
        self._session.trust_env = False  # Ignore system proxies
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
            "license_server": "http://127.0.0.1:5000",
            "enable_server_validation": True,
            "server_timeout": 2,
            "product_key": "TRUETAG-V4",
            "version": "4.1",
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

    def _get_machine_fingerprint(self) -> str:
        """Tạo fingerprint duy nhất dựa trên nhiều thông số phần cứng"""
        try:
            # 1. Machine GUID từ Registry
            guid = ""
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                winreg.CloseKey(key)
            except: guid = "unknown_guid"

            # 2. CPU ID
            cpu = self._get_wmic_value("cpu", "ProcessorId")

            # 3. Baseboard Serial
            mobo = self._get_wmic_value("baseboard", "SerialNumber")

            # 4. Volume Serial của ổ C
            volume = self._get_wmic_value("logicaldisk where DeviceID='C:'", "VolumeSerialNumber")

            # Kết hợp và hash
            combined = f"{guid}|{cpu}|{mobo}|{volume}"
            return hashlib.sha256(combined.encode()).hexdigest()
        except Exception as e:
            print(f"Error generating machine fingerprint: {e}")
            return hashlib.sha256(self._get_machine_id().encode()).hexdigest()

    def _save_trial_to_registry(self, activation_date: str) -> bool:
        """Lưu thông tin trial vào Windows Registry"""
        try:
            # Thử mở hoặc tạo key
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            except:
                # Nếu thất bại với HKLM (cần admin), thử với HKCU
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)

            winreg.SetValueEx(key, self.REG_TRIAL_START, 0, winreg.REG_SZ, activation_date)
            winreg.SetValueEx(key, self.REG_MACHINE_FP, 0, winreg.REG_SZ, self._get_machine_fingerprint())
            winreg.SetValueEx(key, self.REG_TRIAL_USED, 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, self.REG_APP_VERSION, 0, winreg.REG_SZ, self.config.get("version", "4.1"))
            winreg.SetValueEx(key, self.REG_CURRENT_VERSION, 0, winreg.REG_SZ, self.config.get("version", "4.1"))
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Warning: Could not save trial to registry: {e}")
            return False

    def _load_trial_from_registry(self) -> Optional[Dict]:
        """Đọc thông tin trial từ Registry"""
        try:
            # Thử cả HKCU và HKLM
            key = None
            for root in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
                try:
                    key = winreg.OpenKey(root, self.REGISTRY_PATH)
                    break
                except FileNotFoundError:
                    continue
            
            if not key:
                return None

            trial_data = {
                "activation_date": winreg.QueryValueEx(key, self.REG_TRIAL_START)[0],
                "machine_fp": winreg.QueryValueEx(key, self.REG_MACHINE_FP)[0],
                "trial_used": bool(winreg.QueryValueEx(key, self.REG_TRIAL_USED)[0]),
                "app_version": winreg.QueryValueEx(key, self.REG_APP_VERSION)[0],
                "installed_version": winreg.QueryValueEx(key, self.REG_CURRENT_VERSION)[0] if self._has_reg_value(key, self.REG_CURRENT_VERSION) else None
            }
            winreg.CloseKey(key)

            # Kiểm tra fingerprint
            if trial_data["machine_fp"] != self._get_machine_fingerprint():
                print("Registry fingerprint mismatch, ignoring")
                return None

            return trial_data
        except Exception as e:
            # Không in lồi ở đây vì thường xuyên là do Registry chưa có key
            return None
    
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
        """Khởi tạo license trial với kiểm tra persistent thông qua Registry và Server"""
        print("🔄 Initializing trial period...")

        # 1. Kiểm tra Registry trước để ngăn reset bằng cách cài lại
        registry_trial = self._load_trial_from_registry()
        if registry_trial and registry_trial.get("trial_used"):
            raise RuntimeError("Bạn đã sử dụng hết thời gian dùng thử trên máy này.")

        # 2. Kiểm tra trên Server (nếu có kết nối online)
        trial_used_on_server, server_msg = self._check_trial_used_on_server()
        if trial_used_on_server:
            raise RuntimeError(f"Trial đã được sử dụng: {server_msg}")

        # 3. Nếu chưa sử dụng, tiến hành khởi tạo
        activation_date = datetime.datetime.now().isoformat()
        expiry_date = (
            datetime.datetime.now() + 
            datetime.timedelta(days=self.config.get("trial_days", 30))
        ).isoformat()

        license_data["status"] = "trial"
        license_data["activation_date"] = activation_date
        license_data["expiry_date"] = expiry_date
        license_data["trial_used"] = True
        license_data["features"] = self.config.get("features", {}).copy()
        license_data["last_check"] = activation_date
        license_data["checksum"] = self._calculate_checksum(license_data)

        # 4. Lưu vào Registry để persistent
        self._save_trial_to_registry(activation_date)

        # 5. Báo cáo lên Server nếu có thể
        self._report_trial_usage_to_server(license_data)

        # 6. Lưu vào file license.json local
        self._save_license(license_data)
        return license_data

    def _check_trial_used_on_server(self) -> Tuple[bool, str]:
        """Kiểm tra với server xem máy này đã dùng trial chưa"""
        if not self.config.get("enable_server_validation", True):
            return False, "Offline mode enabled"

        try:
            server_url = self.config.get("license_server", "http://localhost:5000")
            timeout = self.config.get("server_timeout", 5)
            check_url = urljoin(server_url, "/api/check-trial-used")
            
            response = requests.post(
                check_url,
                json={
                    "machine_fingerprint": self._get_machine_fingerprint(),
                    "product_key": self.config.get("product_key", "TRUETAG-V4")
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("trial_used", False), data.get("message", "")
            return False, "Server unavailable"
        except:
            return False, "Connection failed"

    def _report_trial_usage_to_server(self, license_data: Dict) -> bool:
        """Báo cáo sử dụng trial lên server"""
        if not self.config.get("enable_server_validation", True):
            return False

        try:
            server_url = self.config.get("license_server", "http://127.0.0.1:5000")
            timeout = self.config.get("server_timeout", 2)
            report_url = urljoin(server_url, "/api/report-trial-usage")
            
            self._session.post(
                report_url,
                json={
                    "machine_fingerprint": self._get_machine_fingerprint(),
                    "product_key": self.config.get("product_key", "TRUETAG-V4"),
                    "machine_id": self._get_machine_id(),
                    "activation_date": license_data.get("activation_date")
                },
                timeout=timeout
            )
            return True
        except:
            return False
    
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
        """Kiểm tra license và phiên bản"""
        # 0. Kiểm tra phiên bản (Local Invalidation)
        current_ver = self.config.get("version", "4.1")
        registry_trial = self._load_trial_from_registry()
        if registry_trial and registry_trial.get("installed_version"):
            last_installed = registry_trial["installed_version"]
            if self._compare_versions(last_installed, current_ver) > 0:
                return False, f"Phiên bản này ({current_ver}) đã lỗi thời. Vui lòng sử dụng bản {last_installed}."

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
            
            # **NEW: Check if license is revoked on server**
            license_key = self.license_data.get("license_key", "")
            if license_key:
                is_revoked, revoke_message = self._check_license_revoked_status(license_key)
                if is_revoked:
                    # Update local status to revoked
                    self.license_data["status"] = "revoked"
                    self._save_license(self.license_data)
                    return False, f"License has been revoked: {revoke_message}"
            
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
            elif status == "revoked":
                return False, "License has been revoked"
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
        """Validate license với server thật"""
        # Check if server validation is enabled
        if not self.config.get("enable_server_validation", True):
            # Fallback to basic validation if server is disabled
            return {
                "valid": True,
                "message": "Server validation disabled",
                "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "features": self.config["features"].copy()
            }
        
        try:
            server_url = self.config.get("license_server", "http://127.0.0.1:5000")
            timeout = self.config.get("server_timeout", 2)
            machine_id = self._get_machine_id()
            
            # Call server API to validate license
            validate_url = urljoin(server_url, "/api/validate")
            
            response = self._session.post(
                validate_url,
                json={
                    "license_key": license_key,
                    "machine_id": machine_id,
                    "version": self.config.get("version", "4.1")
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    license_info = data.get("license_info", {})
                    return {
                        "valid": True,
                        "message": data.get("message", "License validated successfully"),
                        "expiry_date": license_info.get("expiry_date", ""),
                        "features": license_info.get("features", self.config["features"].copy())
                    }
                else:
                    return {
                        "valid": False,
                        "message": data.get("message", "License validation failed")
                    }
            else:
                data = response.json()
                return {
                    "valid": False,
                    "message": data.get("message", "License validation failed")
                }
                
        except Exception as e:
            print(f"Warning: License server connection issue: {e}")
            # Fallback to offline validation
            return {
                "valid": True,
                "message": "Server offline - offline validation",
                "expiry_date": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "features": self.config["features"].copy()
            }
    
    def _check_license_revoked_status(self, license_key: str) -> Tuple[bool, str]:
        """Kiểm tra license có bị revoke không"""
        if not self.config.get("enable_server_validation", True):
            return False, "Server validation disabled"
        
        try:
            server_url = self.config.get("license_server", "http://127.0.0.1:5000")
            timeout = self.config.get("server_timeout", 2)
            
            # Call server API to check revoke status
            revoke_url = urljoin(server_url, "/api/check-revoked")
            
            response = self._session.post(
                revoke_url,
                json={
                    "license_key": license_key,
                    "version": self.config.get("version", "4.1")
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                is_revoked = data.get("revoked", False)
                message = data.get("message", "")
                return is_revoked, message
            else:
                return False, "Cannot check revoke status"
                
        except Exception as e:
            # If server is unreachable, assume not revoked (offline mode)
            print(f"Warning: Error checking revoke status: {e}")
            return False, "Server unreachable - offline mode"
    
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

    def _has_reg_value(self, key, value_name):
        try:
            winreg.QueryValueEx(key, value_name)
            return True
        except:
            return False

    def _compare_versions(self, v1, v2):
        """Compare two version strings (e.g. '4.1' vs '4.0'). Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        try:
            p1 = [int(x) for x in v1.split('.')]
            p2 = [int(x) for x in v2.split('.')]
            for i in range(max(len(p1), len(p2))):
                n1 = p1[i] if i < len(p1) else 0
                n2 = p2[i] if i < len(p2) else 0
                if n1 > n2: return 1
                if n1 < n2: return -1
            return 0
        except:
            return 0
