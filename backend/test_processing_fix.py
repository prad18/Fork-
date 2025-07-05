"""
Test the invoice processing service with the missing method fix
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.invoice_processing_service import InvoiceProcessingService

def test_invoice_processing():
    """Test the invoice processing service"""
    processor = InvoiceProcessingService()
    
    # Test the new method
    test_items = [
        {"name": "Tomatoes", "quantity": 5, "unit": "kg", "price": 10.0},
        {"name": "Chicken", "quantity": 2, "unit": "kg", "price": 15.0}
    ]
    
    print("Testing _process_items_for_carbon_footprint method...")
    result = processor._process_items_for_carbon_footprint(test_items)
    print(f"Result: {result}")
    
    # Test with an actual image file
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = os.listdir(uploads_dir)
        if files:
            test_file = os.path.join(uploads_dir, files[0])
            print(f"\nTesting with actual file: {test_file}")
            
            try:
                result = processor.process_invoice(test_file)
                print(f"Success: {result.get('success', False)}")
                print(f"Items found: {len(result.get('parsed_data', {}).get('items', []))}")
            except Exception as e:
                print(f"Error: {e}")
    
    print("\nInvoice processing service test completed!")

if __name__ == "__main__":
    test_invoice_processing()
