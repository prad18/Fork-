#!/usr/bin/env python3
"""
Invoice Parsing Test with Available Models
"""

import requests
import json
import time

def test_invoice_parsing():
    # Sample OCR text
    ocr_text = """
ORGANIC HARVEST DISTRIBUTORS
123 Green Valley Lane, Sonoma, CA 95476

BILLED TO:                          INVOICE #: INV-2025-03742
The Earth Table Bistro             June 28, 2025

Qty  Unit   Item Description           Total
10   lb     Heirloom Carrots (Organic) $21.00
8    lb     Grass-fed Beef Ribeye      $100.00
6    lb     Organic Kale               $42.00
2    case   Organic Free-Range Eggs    $20.00
4    lb     Ahi Tuna Steaks (Frozen)   $52.00

                                    TOTAL: $427.95
"""

    # Simple parsing prompt
    prompt = f"""Parse this invoice and return ONLY a JSON object:

{ocr_text}

Return this format:
{{
  "vendor_name": "company name",
  "total_amount": 427.95,
  "items": [
    {{"name": "item", "quantity": 10, "unit": "lb", "price": 21.00}}
  ]
}}"""

    models_to_test = ['qwen2.5:latest', 'llama2:latest', 'deepseek-r1:1.5b']
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=120
            )
            
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                llm_output = result.get('response', '').strip()
                
                print(f"⏱️ Response time: {elapsed:.1f}s")
                print(f"📤 LLM Output (first 300 chars):")
                print(f"{llm_output[:300]}...")
                
                # Try to parse JSON
                try:
                    # Look for JSON in the response
                    import re
                    json_match = re.search(r'\{.*\}', llm_output, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        print(f"✅ JSON parsed successfully!")
                        print(f"   Vendor: {parsed.get('vendor_name', 'N/A')}")
                        print(f"   Total: ${parsed.get('total_amount', 'N/A')}")
                        print(f"   Items: {len(parsed.get('items', []))}")
                        
                        if parsed.get('items'):
                            print(f"   First item: {parsed['items'][0]}")
                            
                        return model, parsed  # Return successful result
                    else:
                        print("⚠️ No JSON found in response")
                except Exception as e:
                    print(f"❌ JSON parsing error: {e}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.Timeout:
            print(f"⏰ Timeout after 120s")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None, None

if __name__ == "__main__":
    print("🧾 Testing Invoice Parsing with Available Models")
    print("=" * 60)
    
    best_model, result = test_invoice_parsing()
    
    if best_model:
        print(f"\n🎉 SUCCESS! Best model: {best_model}")
        print("✅ This model can parse invoices correctly.")
        print(f"📋 Full result: {json.dumps(result, indent=2)}")
        print(f"\n💡 Update your LLMInvoiceParser to use: {best_model}")
    else:
        print("\n❌ No models successfully parsed the invoice.")
        print("🔧 Try adjusting the prompt or model parameters.")
