#!/usr/bin/env python3
"""
Test the actual LLMInvoiceParser class with hybrid parsing
"""

import sys
import os

# Add the services directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'services'))

from llm_invoice_parser import LLMInvoiceParser
import json

def test_hybrid_parser():
    print("🔧 Testing LLMInvoiceParser with Hybrid Approach")
    print("=" * 60)
    
    # Sample OCR text
    sample_ocr_text = """
ORGANIC HARVEST DISTRIBUTORS
123 Green Valley Lane, Sonoma, CA 95476
Phone: (707) 555-0199 | Email: orders@organicharvest.com

BILLED TO:                          INVOICE #: INV-2025-03742
The Earth Table Bistro             June 28, 2025
642 Mission Street
San Francisco, CA 94105

Qty  Unit   Item Description           Total
10   lb     Heirloom Carrots (Organic) $21.00
8    lb     Grass-fed Beef Ribeye      $100.00
6    lb     Organic Kale               $42.00
12   lb     Fresh Basil (Organic)      $25.20
2    case   Organic Free-Range Eggs    $20.00
4    lb     Ahi Tuna Steaks (Frozen)   $52.00
1    box    Fair Trade Organic Coffee  $25.00
5    gal    Organic Whole Milk         $21.25
6    lb     Wild Arugula (Organic)     $36.00
3    bottle Sparkling Mineral Water    $18.00
4    lb     Organic Yukon Gold Potatoes $19.20

                                    Subtotal:   $378.85
                                    Tax (9%):    $34.10
                                    Delivery Fee: $15.00
                                    TOTAL:      $427.95
"""
    
    # Initialize parser (will use llama2:latest by default)
    parser = LLMInvoiceParser()
    
    print(f"🤖 Using model: {parser.model}")
    print(f"🌐 Ollama URL: {parser.ollama_url}")
    
    # Test the full hybrid parsing
    print("\n📋 Running hybrid parse (regex + LLM)...")
    result = parser.parse_invoice(sample_ocr_text)
    
    print(f"\n📊 RESULTS:")
    print("-" * 40)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"🔧 Method: {result.get('parsing_method', 'unknown')}")
    print(f"🏢 Vendor: {result.get('vendor_name', 'N/A')}")
    print(f"💰 Total: ${result.get('total_amount', 'N/A')}")
    print(f"📅 Date: {result.get('invoice_date', 'N/A')}")
    print(f"📦 Items: {result.get('item_count', 0)}")
    print(f"🎯 Confidence: {result.get('parsing_confidence', 0)}")
    
    if result.get('items'):
        print(f"\n🛒 Sample Items:")
        for i, item in enumerate(result['items'][:3]):
            print(f"   {i+1}. {item['name']} - {item['quantity']} {item['unit']} @ ${item['price']}")
        
        if len(result['items']) > 3:
            print(f"   ... and {len(result['items']) - 3} more items")
    
    # Show regex result if available
    if result.get('regex_result'):
        print(f"\n🔍 Regex Fallback Result:")
        regex_result = result['regex_result']
        print(f"   Vendor: {regex_result.get('vendor_name', 'N/A')}")
        print(f"   Total: ${regex_result.get('total_amount', 'N/A')}")
        print(f"   Date: {regex_result.get('invoice_date', 'N/A')}")
    
    # Show any errors
    if result.get('llm_error'):
        print(f"\n❌ LLM Error: {result['llm_error']}")
    
    print(f"\n📄 Full JSON Result:")
    print(json.dumps(result, indent=2))
    
    # Determine success
    if result.get('parsing_method') == 'llm+regex' and result.get('item_count', 0) > 0:
        print(f"\n🎉 EXCELLENT! Hybrid parsing with LLM worked perfectly!")
        return True
    elif result.get('parsing_method') in ['regex-fallback', 'regex-only'] and result.get('vendor_name'):
        print(f"\n⚠️ LLM failed, but regex fallback worked. Basic parsing successful.")
        return True
    else:
        print(f"\n❌ Parsing failed completely.")
        return False

if __name__ == "__main__":
    success = test_hybrid_parser()
    
    if success:
        print(f"\n✅ Your LLMInvoiceParser is ready for integration!")
        print(f"💡 Start your FastAPI backend and test with real invoice uploads.")
    else:
        print(f"\n🔧 Fix the issues above before integrating with FastAPI.")
