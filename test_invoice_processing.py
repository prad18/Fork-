"""
Test script for the integrated invoice processing pipeline
Run this to test OCR + LLM processing without going through the full web interface
"""

import sys
import os
import json

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.services.invoice_processing_service import InvoiceProcessingService
    print("✅ Successfully imported InvoiceProcessingService")
except ImportError as e:
    print(f"❌ Failed to import services: {e}")
    print("Make sure you're running this from the Fork+ root directory")
    sys.exit(1)

def main():
    print("=" * 60)
    print("           Fork+ Invoice Processing Test")
    print("=" * 60)
    
    # Initialize the processor
    try:
        processor = InvoiceProcessingService()
        print("✅ Invoice processor initialized")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return
    
    # Check service status
    print("\n🔍 Checking service status...")
    status = processor.get_service_status()
    
    print(f"OCR Service: {'✅' if status['ocr_service']['available'] else '❌'}")
    if status['ocr_service']['available']:
        print(f"  Engine: {status['ocr_service'].get('engine', 'Unknown')}")
    
    print(f"LLM Service: {'✅' if status['llm_service']['available'] else '❌'}")
    if status['llm_service']['available']:
        print(f"  Engine: {status['llm_service'].get('engine', 'Unknown')}")
        print(f"  Model: {status['llm_service'].get('model', 'Unknown')}")
    else:
        print("  ⚠️ LLM service not available. Run setup-llm.bat first!")
    
    print(f"Ready for Processing: {'✅' if status['combined_service']['ready_for_processing'] else '❌'}")
    
    if not status['combined_service']['ready_for_processing']:
        print("\n❌ System not ready for processing. Please check the services above.")
        return
    
    # Test with sample invoice text
    print("\n🧪 Testing with sample invoice text...")
    
    sample_text = """
ORGANIC HARVEST DISTRIBUTORS
123 Green Valley Lane, Sonoma, CA 95476
Phone: (707) 555-0199

INVOICE #: INV-2025-03742
Date: June 28, 2025

BILLED TO:
The Earth Table Bistro
642 Mission Street
San Francisco, CA 94105

Qty  Unit   Item Description           Price    Total
10   lb     Heirloom Carrots (Organic)  $2.10   $21.00
8    lb     Grass-fed Beef Ribeye       $12.50  $100.00
6    lb     Organic Kale                $7.00   $42.00
12   lb     Fresh Basil (Organic)       $2.10   $25.20
2    case   Organic Free-Range Eggs     $10.00  $20.00
4    lb     Ahi Tuna Steaks             $13.00  $52.00

                                    Subtotal:   $260.20
                                    Tax (9%):    $23.42
                                    TOTAL:      $283.62
"""
    
    print("Processing sample invoice...")
    result = processor.process_invoice_from_text(sample_text)
    
    if result.get('success', False):
        print("✅ Processing successful!")
        print(f"📊 Results:")
        print(f"  Vendor: {result.get('vendor_name', 'Unknown')}")
        print(f"  Total: ${result.get('total_amount', 0)}")
        print(f"  Date: {result.get('invoice_date', 'Unknown')}")
        print(f"  Items: {result.get('item_count', 0)}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Method: {result.get('processing_method', 'Unknown')}")
        
        print(f"\n📝 First 3 items:")
        items = result.get('items', [])
        for i, item in enumerate(items[:3]):
            print(f"  {i+1}. {item.get('name', 'Unknown')} - "
                  f"{item.get('quantity', 0)} {item.get('unit', '')} @ "
                  f"${item.get('price', 0)}")
        
        if len(items) > 3:
            print(f"  ... and {len(items) - 3} more items")
        
        # Show categories if available
        categories = result.get('categorized_items', {})
        if categories:
            print(f"\n📂 Categories:")
            for category, count in categories.items():
                print(f"  {category}: {count} items")
        
        print(f"\n⏱️ Processing time:")
        proc_time = result.get('processing_time', {})
        print(f"  OCR: {proc_time.get('ocr_time', 0):.2f}s")
        print(f"  LLM: {proc_time.get('llm_time', 0):.2f}s")
        
    else:
        print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        if 'llm_result' in result:
            print(f"LLM Error: {result['llm_result'].get('error', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("Test completed!")
    
    # Offer to test with a real file
    if result.get('success', False):
        print("\n💡 To test with a real invoice image/PDF:")
        print("   python test_invoice_processing.py path/to/your/invoice.jpg")
        print("\n💡 To test via the web API:")
        print("   1. Start the backend: python backend/main.py")
        print("   2. Check status: GET http://localhost:8000/api/invoices/service/status")
        print("   3. Test parsing: POST http://localhost:8000/api/invoices/test/parse-text")

if __name__ == "__main__":
    # Check if a file path was provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            print(f"🖼️ Testing with file: {file_path}")
            
            try:
                processor = InvoiceProcessingService()
                result = processor.process_invoice(file_path)
                
                if result.get('success', False):
                    print("✅ File processing successful!")
                    print(f"  Vendor: {result.get('vendor_name', 'Unknown')}")
                    print(f"  Total: ${result.get('total_amount', 0)}")
                    print(f"  Items: {result.get('item_count', 0)}")
                    print(f"  Confidence: {result.get('confidence', 0):.2f}")
                else:
                    print(f"❌ File processing failed: {result.get('error', 'Unknown')}")
                    
            except Exception as e:
                print(f"❌ Error processing file: {e}")
        else:
            print(f"❌ File not found: {file_path}")
    else:
        main()
