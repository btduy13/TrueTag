"""
License Server for TRUETAG v4.0
Mô phỏng server validation cho license
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, Tuple
from license_generator import LicenseGenerator

class LicenseServer:
    """Server mô phỏng để validate license"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.generator = LicenseGenerator(data_dir)
        self.server_config_file = os.path.join(data_dir, 'server_config.json')
        
        # Load server configuration
        self.config = self._load_server_config()
    
    def _load_server_config(self) -> Dict:
        """Load cấu hình server"""
        default_config = {
            "server_name": "TRUETAG License Server",
            "version": "1.0",
            "api_endpoints": {
                "validate": "/api/v1/validate",
                "activate": "/api/v1/activate",
                "info": "/api/v1/info"
            },
            "security": {
                "api_key": "TRUETAG-API-KEY-2025",
                "rate_limit": {
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000
                },
                "encryption": {
                    "enabled": True,
                    "algorithm": "AES-256"
                }
            },
            "logging": {
                "enabled": True,
                "log_file": "license_server.log"
            }
        }
        
        try:
            if os.path.exists(self.server_config_file):
                with open(self.server_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
            else:
                # Save default config
                with open(self.server_config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error loading server config: {e}")
        
        return default_config
    
    def validate_license_request(self, license_key: str, machine_id: str = None, 
                               api_key: str = None) -> Dict:
        """
        Validate license request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate license
            is_valid, message, license_data = self.generator.validate_license(license_key, machine_id)
            
            if is_valid:
                return {
                    "success": True,
                    "valid": True,
                    "license_key": license_key,
                    "license_type": license_data["license_type"],
                    "features": license_data["features"],
                    "expiry_date": license_data["expiry_date"],
                    "days_remaining": self._calculate_days_remaining(license_data["expiry_date"]),
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "server_version": self.config["version"]
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": message,
                    "error_code": "LICENSE_INVALID",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def activate_license_request(self, license_key: str, machine_id: str, 
                                customer_name: str = "", api_key: str = None) -> Dict:
        """
        Activate license request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Activate license
            success, message = self.generator.activate_license(license_key, machine_id, customer_name)
            
            if success:
                # Get updated license info
                license_info = self.generator.get_license_info(license_key)
                
                return {
                    "success": True,
                    "activated": True,
                    "license_key": license_key,
                    "machine_id": machine_id,
                    "activation_date": datetime.now().isoformat(),
                    "features": license_info["features"],
                    "expiry_date": license_info["expiry_date"],
                    "days_remaining": self._calculate_days_remaining(license_info["expiry_date"]),
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "server_version": self.config["version"]
                }
            else:
                return {
                    "success": False,
                    "activated": False,
                    "error": message,
                    "error_code": "ACTIVATION_FAILED",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_license_info_request(self, license_key: str, api_key: str = None) -> Dict:
        """
        Get license info request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get license info
            license_info = self.generator.get_license_info(license_key)
            
            if license_info:
                return {
                    "success": True,
                    "license_key": license_key,
                    "license_type": license_info["license_type"],
                    "status": license_info["status"],
                    "created_date": license_info["created_date"],
                    "expiry_date": license_info["expiry_date"],
                    "duration_days": license_info["duration_days"],
                    "features": license_info["features"],
                    "current_uses": license_info["current_uses"],
                    "max_uses": license_info["max_uses"],
                    "customer_info": license_info.get("customer_info", {}),
                    "notes": license_info.get("notes", ""),
                    "days_remaining": self._calculate_days_remaining(license_info["expiry_date"]),
                    "timestamp": datetime.now().isoformat(),
                    "server_version": self.config["version"]
                }
            else:
                return {
                    "success": False,
                    "error": "License not found",
                    "error_code": "LICENSE_NOT_FOUND",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def revoke_license_request(self, license_key: str, reason: str = "", admin_name: str = "", api_key: str = None) -> Dict:
        """
        Revoke license request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Revoke license
            success, message = self.generator.revoke_license(license_key, reason, admin_name)
            
            if success:
                # Get updated license info
                license_info = self.generator.get_license_info(license_key)
                
                return {
                    "success": True,
                    "revoked": True,
                    "license_key": license_key,
                    "reason": reason,
                    "admin_name": admin_name,
                    "revoked_date": datetime.now().isoformat(),
                    "status": license_info["status"] if license_info else "revoked",
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "server_version": self.config["version"]
                }
            else:
                return {
                    "success": False,
                    "revoked": False,
                    "error": message,
                    "error_code": "REVOKE_FAILED",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def unrevoke_license_request(self, license_key: str, admin_name: str = "", reason: str = "", api_key: str = None) -> Dict:
        """
        Unrevoke license request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Unrevoke license
            success, message = self.generator.unrevoke_license(license_key, admin_name, reason)
            
            if success:
                # Get updated license info
                license_info = self.generator.get_license_info(license_key)
                
                return {
                    "success": True,
                    "unrevoked": True,
                    "license_key": license_key,
                    "admin_name": admin_name,
                    "reason": reason,
                    "unrevoked_date": datetime.now().isoformat(),
                    "status": license_info["status"] if license_info else "active",
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                    "server_version": self.config["version"]
                }
            else:
                return {
                    "success": False,
                    "unrevoked": False,
                    "error": message,
                    "error_code": "UNREVOKE_FAILED",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def get_revoked_licenses_request(self, api_key: str = None) -> Dict:
        """
        Get revoked licenses request từ client
        Returns: Server response dictionary
        """
        try:
            # Validate API key
            if api_key and api_key != self.config["security"]["api_key"]:
                return {
                    "success": False,
                    "error": "Invalid API key",
                    "error_code": "INVALID_API_KEY",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get revoked licenses
            revoked_licenses = self.generator.get_revoked_licenses()
            
            return {
                "success": True,
                "revoked_licenses": revoked_licenses,
                "total_revoked": len(revoked_licenses),
                "timestamp": datetime.now().isoformat(),
                "server_version": self.config["version"]
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Server error: {e}",
                "error_code": "SERVER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_days_remaining(self, expiry_date_str: str) -> int:
        """Tính số ngày còn lại"""
        try:
            expiry_date = datetime.fromisoformat(expiry_date_str)
            now = datetime.now()
            if expiry_date > now:
                return (expiry_date - now).days
            else:
                return 0
        except:
            return 0
    
    def get_server_status(self) -> Dict:
        """Lấy trạng thái server"""
        stats = self.generator.get_statistics()
        
        return {
            "server_name": self.config["server_name"],
            "version": self.config["version"],
            "status": "online",
            "uptime": "unknown",  # Could be calculated if needed
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def simulate_client_request(self, request_type: str, **kwargs) -> Dict:
        """
        Mô phỏng request từ client
        """
        if request_type == "validate":
            return self.validate_license_request(
                kwargs.get("license_key"),
                kwargs.get("machine_id"),
                kwargs.get("api_key")
            )
        elif request_type == "activate":
            return self.activate_license_request(
                kwargs.get("license_key"),
                kwargs.get("machine_id"),
                kwargs.get("customer_name", ""),
                kwargs.get("api_key")
            )
        elif request_type == "info":
            return self.get_license_info_request(
                kwargs.get("license_key"),
                kwargs.get("api_key")
            )
        else:
            return {
                "success": False,
                "error": f"Unknown request type: {request_type}",
                "error_code": "UNKNOWN_REQUEST",
                "timestamp": datetime.now().isoformat()
            }
    
    def update_licensing_manager(self, licensing_manager):
        """
        Cập nhật licensing_manager để sử dụng server validation
        """
        # Override validation methods để sử dụng server
        original_validate = licensing_manager._validate_license_with_server
        
        def server_validate(license_key):
            # Simulate server request
            response = self.validate_license_request(license_key)
            
            if response["success"] and response["valid"]:
                return {
                    "valid": True,
                    "message": response["message"],
                    "expiry_date": response["expiry_date"],
                    "features": response["features"]
                }
            else:
                return {
                    "valid": False,
                    "message": response.get("error", "Validation failed")
                }
        
        # Replace the validation method
        licensing_manager._validate_license_with_server = server_validate
        
        return True
