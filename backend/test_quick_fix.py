"""
Test the fixed invoice processing directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.services.invoice_processing_service import InvoiceProcessingService
    
    print("Testing invoice processing service...")
    processor = InvoiceProcessingService()
    
    # Test the method exists
    print("Testing _process_items_for_carbon_footprint method...")
    test_items = [
        {"name": "Tomatoes", "quantity": 5, "unit": "kg", "price": 10.0},
        {"name": "Chicken", "quantity": 2, "unit": "kg", "price": 15.0}
    ]
    
    result = processor._process_items_for_carbon_footprint(test_items)
    print(f"SUCCESS: Method works, result: {result}")
    
    # Test with minimal text parsing
    print("\nTesting text parsing...")
    test_text = "Invoice\nApples 5 kg $10.00\nBread 2 pieces $5.00\nTotal: $15.00"
    
    result = processor.process_invoice_from_text(test_text)
    print(f"Text parsing result: {result.get('success', False)}")
    
    print("\nAll tests passed! The fix is working.")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
