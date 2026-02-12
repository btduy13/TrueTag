"""
Simple License Validation Server
Flask API để validate licenses từ xa
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
from license_generator import LicenseGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize license generator
data_dir = os.path.dirname(os.path.abspath(__file__))
generator = LicenseGenerator(data_dir)

# Minimum supported version
MIN_SUPPORTED_VERSION = "4.1"

def is_version_supported(client_version):
    """Kiểm tra phiên bản có đựoc hỗ trợ không"""
    if not client_version: return False
    try:
        p_client = [int(x) for x in client_version.split('.')]
        p_min = [int(x) for x in MIN_SUPPORTED_VERSION.split('.')]
        for i in range(max(len(p_client), len(p_min))):
            n_c = p_client[i] if i < len(p_client) else 0
            n_m = p_min[i] if i < len(p_min) else 0
            if n_c > n_m: return True
            if n_c < n_m: return False
        return True
    except:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'License server is running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/validate', methods=['POST'])
def validate_license():
    """
    Validate license key
    Request: {license_key: str, machine_id: str}
    Response: {valid: bool, message: str, license_data: dict}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'valid': False,
                'message': 'Invalid request format'
            }), 400

        client_version = data.get('version', '')
        if not is_version_supported(client_version):
            return jsonify({
                'valid': False,
                'message': f'Phiên bản này ({client_version or "vô danh"}) đã bị vô hiệu hóa. Vui lòng cập nhật lên {MIN_SUPPORTED_VERSION}.'
            }), 426
        
        license_key = data.get('license_key', '')
        machine_id = data.get('machine_id', '')
        
        if not license_key:
            return jsonify({
                'valid': False,
                'message': 'License key is required'
            }), 400
        
        # Validate license using generator
        is_valid, message, license_data = generator.validate_license(license_key, machine_id)
        
        # Return validation result
        response = {
            'valid': is_valid,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_valid:
            # Include license info if valid
            response['license_info'] = {
                'license_type': license_data.get('license_type', ''),
                'expiry_date': license_data.get('expiry_date', ''),
                'features': license_data.get('features', []),
                'status': license_data.get('status', '')
            }
        
        return jsonify(response), 200 if is_valid else 403
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/activate', methods=['POST'])
def activate_license():
    """
    Activate license on machine
    Request: {license_key: str, machine_id: str, customer_name: str}
    Response: {success: bool, message: str}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request format'
            }), 400
        
        license_key = data.get('license_key', '')
        machine_id = data.get('machine_id', '')
        customer_name = data.get('customer_name', '')
        
        if not license_key or not machine_id:
            return jsonify({
                'success': False,
                'message': 'License key and machine ID are required'
            }), 400
        
        # Activate license
        success, message = generator.activate_license(license_key, machine_id, customer_name)
        
        return jsonify({
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }), 200 if success else 403
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/license-info', methods=['POST'])
def get_license_info():
    """
    Get license information
    Request: {license_key: str}
    Response: {success: bool, license_info: dict}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request format'
            }), 400
        
        license_key = data.get('license_key', '')
        
        if not license_key:
            return jsonify({
                'success': False,
                'message': 'License key is required'
            }), 400
        
        # Get license info
        license_info = generator.get_license_info(license_key)
        
        if not license_info:
            return jsonify({
                'success': False,
                'message': 'License not found'
            }), 404
        
        # Remove sensitive info
        safe_info = {
            'license_key': license_info.get('license_key', ''),
            'license_type': license_info.get('license_type', ''),
            'status': license_info.get('status', ''),
            'expiry_date': license_info.get('expiry_date', ''),
            'features': license_info.get('features', []),
            'max_uses': license_info.get('max_uses', 0),
            'current_uses': license_info.get('current_uses', 0)
        }
        
        # Add revoke info if revoked
        if license_info.get('status') == 'revoked':
            revoke_info = license_info.get('revoke_info', {})
            safe_info['revoke_info'] = {
                'revoked_date': revoke_info.get('revoked_date', ''),
                'reason': revoke_info.get('reason', '')
            }
        
        return jsonify({
            'success': True,
            'license_info': safe_info,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/check-revoked', methods=['POST'])
def check_revoked():
    """
    Check if license is revoked
    Request: {license_key: str}
    Response: {revoked: bool, message: str}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'revoked': True,
                'message': 'Invalid request format'
            }), 400
            
        client_version = data.get('version', '')
        if not is_version_supported(client_version):
            return jsonify({
                'revoked': True,
                'message': f'Yêu cầu nâng cấp lên {MIN_SUPPORTED_VERSION}.'
            }), 426
        
        license_key = data.get('license_key', '')
        
        if not license_key:
            return jsonify({
                'revoked': True,
                'message': 'License key is required'
            }), 400
        
        # Get license info
        license_info = generator.get_license_info(license_key)
        
        if not license_info:
            return jsonify({
                'revoked': True,
                'message': 'License not found'
            }), 404
        
        is_revoked = license_info.get('status') == 'revoked'
        
        response = {
            'revoked': is_revoked,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_revoked:
            revoke_info = license_info.get('revoke_info', {})
            response['message'] = f"License revoked: {revoke_info.get('reason', 'No reason provided')}"
            response['revoked_date'] = revoke_info.get('revoked_date', '')
        else:
            response['message'] = 'License is active'
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'revoked': True,
            'message': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# Trial tracking database file
TRIAL_DB_FILE = os.path.join(data_dir, 'trial_db.json')

def load_trial_db():
    """Load trial tracking database"""
    if os.path.exists(TRIAL_DB_FILE):
        try:
            with open(TRIAL_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_trial_db(db_data):
    """Save trial tracking database"""
    try:
        with open(TRIAL_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=4, ensure_ascii=False)
        return True
    except:
        return False

@app.route('/api/check-trial-used', methods=['POST'])
def check_trial_used():
    """
    Kiểm tra xem machine fingerprint này đã dùng trial chưa
    Request: {machine_fingerprint: str, product_key: str}
    """
    try:
        data = request.get_json()
        machine_fp = data.get('machine_fingerprint', '')
        product_key = data.get('product_key', 'TRUETAG-V4')

        if not machine_fp:
            return jsonify({'trial_used': False, 'message': 'Missing machine fingerprint'}), 400

        db = load_trial_db()
        if machine_fp in db:
            trial_info = db[machine_fp]
            # Check if it's the same product key (optional)
            return jsonify({
                'trial_used': True,
                'message': f"Dùng thử đã được kích hoạt trên máy này vào lúc {trial_info.get('activation_date', 'N/A')}",
                'activation_date': trial_info.get('activation_date')
            }), 200
        
        return jsonify({'trial_used': False, 'message': 'Máy này chưa dùng thử'}), 200
    except Exception as e:
        return jsonify({'trial_used': False, 'message': str(e)}), 500

@app.route('/api/report-trial-usage', methods=['POST'])
def report_trial_usage():
    """
    Báo cáo việc bắt đầu sử dụng trial
    Request: {machine_fingerprint: str, product_key: str, machine_id: str, activation_date: str}
    """
    try:
        data = request.get_json()
        machine_fp = data.get('machine_fingerprint')
        
        if not machine_fp:
            return jsonify({'success': False, 'message': 'Missing fingerprint'}), 400

        db = load_trial_db()
        if machine_fp not in db:
            db[machine_fp] = {
                'product_key': data.get('product_key'),
                'machine_id': data.get('machine_id'),
                'activation_date': data.get('activation_date', datetime.now().isoformat()),
                'ip_address': request.remote_addr,
                'reporter_timestamp': datetime.now().isoformat()
            }
            save_trial_db(db)
            return jsonify({'success': True, 'message': 'Trial usage reported'}), 200
        
        return jsonify({'success': True, 'message': 'Trial already recorded'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get license statistics (admin only)"""
    try:
        stats = generator.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("TRUETAG License Server")
    print("=" * 60)
    print(f"Starting server...")
    print(f"Data directory: {data_dir}")
    print(f"License database: {generator.license_db_file}")
    print()
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /api/validate - Validate license")
    print("  POST /api/activate - Activate license")
    print("  POST /api/license-info - Get license info")
    print("  POST /api/check-revoked - Check if revoked")
    print("  GET  /api/statistics - Get statistics")
    print()
    print("Server running on http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
