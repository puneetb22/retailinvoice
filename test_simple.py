#!/usr/bin/env python3

"""Simple test for decimal handling"""

from decimal import Decimal, InvalidOperation

# Test basic decimal operations
def test_decimal_math():
    try:
        a = Decimal('100.50')
        b = Decimal('50.25')
        
        # Test addition
        sum_result = a + b
        print(f"Addition: {a} + {b} = {sum_result}")
        
        # Test subtraction
        diff_result = a - b
        print(f"Subtraction: {a} - {b} = {diff_result}")
        
        # Test multiplication
        mult_result = a * Decimal('0.05')  # 5% tax
        print(f"Multiplication (5% tax): {a} * 0.05 = {mult_result}")
        
        # Test division
        div_result = a / Decimal('2')
        print(f"Division: {a} / 2 = {div_result}")
        
        print("✓ All basic decimal math operations succeeded")
        return True
    except Exception as e:
        print(f"✗ Error in decimal math: {e}")
        return False

# Test string conversion
def test_string_conversion():
    try:
        # Test valid conversions
        valid_values = [
            '100.50',    # String
            '100',       # Integer string
            100.50,      # Float
            100          # Integer
        ]
        
        for val in valid_values:
            decimal_val = Decimal(str(val))
            print(f"Converted {val} ({type(val).__name__}) to Decimal: {decimal_val}")
        
        # Test invalid conversions
        invalid_values = ['abc', '']
        for val in invalid_values:
            try:
                decimal_val = Decimal(str(val))
                print(f"✗ Should have failed: {val}")
            except (ValueError, InvalidOperation) as e:
                print(f"✓ Correctly caught error for '{val}': {type(e).__name__}")
        
        print("✓ All string conversion tests passed")
        return True
    except Exception as e:
        print(f"✗ Error in string conversion: {e}")
        return False

if __name__ == "__main__":
    print("\n--- SIMPLE DECIMAL TESTS ---\n")
    
    print("Test 1: Basic Decimal Math")
    print("-" * 40)
    test_decimal_math()
    print("-" * 40)
    
    print("\nTest 2: String Conversion")
    print("-" * 40)
    test_string_conversion()
    print("-" * 40)
    
    print("\nTests completed")
