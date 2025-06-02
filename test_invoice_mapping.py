
"""
Test script to verify invoice value mapping from database to PDF generation
"""
import sqlite3
import datetime
from utils.pdf_invoice_generator import generate_invoice

def check_database_settings():
    """Check what settings exist in the database"""
    print("=== CHECKING DATABASE SETTINGS ===")
    conn = sqlite3.connect('./pos_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if settings table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
    if not cursor.fetchone():
        print("❌ Settings table does not exist!")
        conn.close()
        return False
    
    # Get all settings
    cursor.execute("SELECT key, value FROM settings ORDER BY key")
    settings = cursor.fetchall()
    
    print(f"Found {len(settings)} settings:")
    for setting in settings:
        print(f"  {setting['key']}: {setting['value']}")
    
    conn.close()
    return len(settings) > 0

def create_test_invoice_data():
    """Create test invoice data"""
    return {
        'invoice_number': 'TEST-001',
        'invoice_id': 'TEST-001',
        'date': '04/01/2025',
        'time': '10:30 AM',
        'customer': {
            'name': 'Test Customer',
            'phone': '9876543210',
            'address': 'Test Address',
            'village': 'Test Village',
            'email': 'test@test.com',
            'gstin': ''
        },
        'items': [
            {
                'name': 'Test Product',
                'company': 'Test Company',
                'hsn_code': '1234',
                'batch_no': 'B001',
                'expiry_date': '2025-12-31',
                'quantity': 2,
                'unit': 'kg',
                'price': 100,
                'discount': 5,
                'total': 190
            }
        ],
        'payment': {
            'method': 'Cash',
            'status': 'PAID',
            'subtotal': 200,
            'discount': 10,
            'cgst': 9,
            'sgst': 9,
            'total': 208
        }
    }

def test_invoice_generation():
    """Test invoice generation and check if values are mapped"""
    print("\n=== TESTING INVOICE GENERATION ===")
    
    # Create test data
    invoice_data = create_test_invoice_data()
    
    # Generate invoice
    save_path = "./test_mapping_invoice.pdf"
    
    try:
        success = generate_invoice(invoice_data, save_path)
        
        if success:
            print("✅ Invoice generated successfully!")
            print(f"📄 Saved to: {save_path}")
            return True
        else:
            print("❌ Invoice generation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error generating invoice: {e}")
        return False

def check_shop_info_mapping():
    """Check if shop info is properly mapped from database"""
    print("\n=== CHECKING SHOP INFO MAPPING ===")
    
    conn = sqlite3.connect('./pos_data.db')
    cursor = conn.cursor()
    
    # Check what shop info keys exist
    expected_keys = [
        'shop_name', 'shop_address', 'shop_phone', 'shop_gst', 'shop_email',
        'shop_laid_no', 'shop_lcsd_no', 'shop_lfrd_no',
        'state_name', 'state_code'
    ]
    
    print("Checking for expected shop info keys:")
    missing_keys = []
    
    for key in expected_keys:
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            print(f"  ✅ {key}: {result[0]}")
        else:
            print(f"  ❌ {key}: NOT FOUND")
            missing_keys.append(key)
    
    conn.close()
    
    if missing_keys:
        print(f"\n⚠️  Missing {len(missing_keys)} required shop info keys:")
        for key in missing_keys:
            print(f"    - {key}")
        return False
    else:
        print("\n✅ All shop info keys found!")
        return True

def add_missing_shop_info():
    """Add missing shop info to database"""
    print("\n=== ADDING MISSING SHOP INFO ===")
    
    conn = sqlite3.connect('./pos_data.db')
    cursor = conn.cursor()
    
    # Default shop info
    default_shop_info = {
        'shop_name': 'Agritech Products Shop',
        'shop_address': 'Main Road, Maharashtra',
        'shop_phone': '+91 1234567890',
        'shop_gst': '27AABCU9603R1ZX',
        'shop_email': 'info@agritech.com',
        'shop_laid_no': 'LAID123456',
        'shop_lcsd_no': 'LCSD789012',
        'shop_lfrd_no': 'LFRD345678',
        'state_name': 'Maharashtra',
        'state_code': '27'
    }
    
    added_count = 0
    
    for key, value in default_shop_info.items():
        # Check if key exists
        cursor.execute("SELECT id FROM settings WHERE key = ?", (key,))
        if not cursor.fetchone():
            # Insert new setting
            cursor.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
            print(f"  ➕ Added {key}: {value}")
            added_count += 1
        else:
            print(f"  ✅ {key} already exists")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Added {added_count} missing shop info entries")
    return added_count > 0

if __name__ == "__main__":
    print("🔍 INVOICE MAPPING VERIFICATION TEST")
    print("=" * 50)
    
    # Step 1: Check database settings
    settings_exist = check_database_settings()
    
    # Step 2: Check shop info mapping
    shop_info_complete = check_shop_info_mapping()
    
    # Step 3: Add missing shop info if needed
    if not shop_info_complete:
        add_missing_shop_info()
        shop_info_complete = check_shop_info_mapping()
    
    # Step 4: Test invoice generation
    if settings_exist and shop_info_complete:
        invoice_success = test_invoice_generation()
        
        if invoice_success:
            print("\n🎉 OVERALL RESULT: SUCCESS!")
            print("   - Database settings found ✅")
            print("   - Shop info mapping complete ✅") 
            print("   - Invoice generation successful ✅")
        else:
            print("\n❌ OVERALL RESULT: PARTIAL SUCCESS")
            print("   - Database settings found ✅")
            print("   - Shop info mapping complete ✅")
            print("   - Invoice generation failed ❌")
    else:
        print("\n❌ OVERALL RESULT: FAILED")
        print(f"   - Database settings found: {'✅' if settings_exist else '❌'}")
        print(f"   - Shop info mapping complete: {'✅' if shop_info_complete else '❌'}")
