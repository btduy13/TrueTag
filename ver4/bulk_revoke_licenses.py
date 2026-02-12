"""
Bulk License Revocation Script
Thu hồi hàng loạt tất cả licenses đã phát hành
"""

import os
import json
from datetime import datetime
from license_generator import LicenseGenerator

def bulk_revoke_all_licenses():
    """Thu hồi tất cả licenses active trong database"""
    
    print("=" * 60)
    print("BULK LICENSE REVOCATION TOOL")
    print("=" * 60)
    print()
    
    # Initialize license generator
    data_dir = os.path.dirname(os.path.abspath(__file__))
    generator = LicenseGenerator(data_dir)
    
    # Get all active licenses
    print("📋 Loading active licenses...")
    active_licenses = generator.list_licenses(status="active")
    
    if not active_licenses:
        print("✓ No active licenses found to revoke.")
        return
    
    print(f"Found {len(active_licenses)} active license(s):")
    print()
    
    # Display licenses
    for i, lic in enumerate(active_licenses, 1):
        customer_name = lic.get('customer_info', {}).get('name', 'N/A')
        print(f"{i}. {lic['license_key']}")
        print(f"   Type: {lic['license_type']}")
        print(f"   Customer: {customer_name}")
        print(f"   Created: {lic['created_date'][:10]}")
        print()
    
    # Confirmation
    print("⚠️  WARNING: This will revoke ALL active licenses!")
    print("⚠️  Users will need new license keys to continue using the software.")
    print()
    
    confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Revocation cancelled.")
        return
    
    # Get revocation details
    print()
    admin_name = input("Enter your admin name: ").strip()
    reason = input("Enter reason for revocation: ").strip()
    
    if not admin_name or not reason:
        print("❌ Admin name and reason are required!")
        return
    
    # Perform bulk revocation
    print()
    print("🔄 Revoking licenses...")
    print()
    
    license_keys = [lic['license_key'] for lic in active_licenses]
    results = generator.revoke_license_bulk(license_keys, reason, admin_name)
    
    # Display results
    success_count = 0
    failed_count = 0
    
    for license_key, message in results.items():
        if "successfully" in message.lower():
            success_count += 1
            print(f"✓ {license_key}: {message}")
        else:
            failed_count += 1
            print(f"✗ {license_key}: {message}")
    
    print()
    print("=" * 60)
    print(f"✓ Successfully revoked: {success_count}")
    print(f"✗ Failed: {failed_count}")
    print("=" * 60)
    
    # Create revocation report
    report_file = f"revocation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("LICENSE REVOCATION REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Admin: {admin_name}\n")
        f.write(f"Reason: {reason}\n")
        f.write(f"Total revoked: {success_count}\n")
        f.write(f"Failed: {failed_count}\n\n")
        f.write("REVOKED LICENSES:\n")
        f.write("-" * 60 + "\n")
        for lic in active_licenses:
            customer_name = lic.get('customer_info', {}).get('name', 'N/A')
            f.write(f"License Key: {lic['license_key']}\n")
            f.write(f"Type: {lic['license_type']}\n")
            f.write(f"Customer: {customer_name}\n")
            f.write(f"Email: {lic.get('customer_info', {}).get('email', 'N/A')}\n")
            f.write(f"Created: {lic['created_date'][:10]}\n")
            f.write("-" * 60 + "\n")
    
    print(f"\n📄 Revocation report saved to: {report_file}")
    print("\n✅ Bulk revocation completed!")
    print("\nNext steps:")
    print("1. Review the revocation report")
    print("2. Create new license keys for customers")
    print("3. Contact customers with new licenses and installer")

if __name__ == "__main__":
    try:
        bulk_revoke_all_licenses()
    except Exception as e:
        print(f"\n❌ Error during bulk revocation: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
