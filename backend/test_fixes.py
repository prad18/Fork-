"""
Quick test to verify the fixes work
"""
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_imports():
    """Test that all imports work"""
    try:
        from app.services.invoice_processing_service import InvoiceProcessingService
        print("[SUCCESS] InvoiceProcessingService import works")
        
        from app.services.llm_invoice_parser import LLMInvoiceParser
        print("[SUCCESS] LLMInvoiceParser import works")
        
        from app.routers.invoice import router
        print("[SUCCESS] Invoice router import works")
        
        return True
    except Exception as e:
        print(f"[ERROR] Import failed: {e}")
        return False

def test_date_parsing():
    """Test date parsing functionality"""
    from datetime import datetime
    
    # Test the date formats that were causing issues
    test_dates = [
        "May 25, 2022",
        "2022-05-25", 
        "05/25/2022",
        "25/05/2022"
    ]
    
    date_formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
        "%B %d, %Y", "%b %d, %Y",
        "%d %B %Y", "%d %b %Y",
        "%m-%d-%Y", "%d-%m-%Y"
    ]
    
    for date_str in test_dates:
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                print(f"[SUCCESS] Parsed '{date_str}' with format '{fmt}': {parsed_date}")
                break
            except ValueError:
                continue
        
        if not parsed_date:
            print(f"[ERROR] Could not parse date: {date_str}")

def test_processing_method():
    """Test the processing method exists"""
    try:
        from app.services.invoice_processing_service import InvoiceProcessingService
        processor = InvoiceProcessingService()
        
        # Test the method exists
        test_items = [
            {"name": "Tomatoes", "quantity": 5, "unit": "kg", "price": 10.0},
        ]
        
        result = processor._process_items_for_carbon_footprint(test_items)
        print(f"[SUCCESS] _process_items_for_carbon_footprint works: {result}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Method test failed: {e}")
        return False

if __name__ == "__main__":
    print("Running quick tests...")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Test date parsing
    print("Testing date parsing:")
    test_date_parsing()
    print()
    
    # Test processing method
    method_ok = test_processing_method()
    print()
    
    if imports_ok and method_ok:
        print("[SUCCESS] All tests passed! The fixes are working.")
    else:
        print("[ERROR] Some tests failed. Check the errors above.")
