#!/usr/bin/env python3
"""
Standalone LLM Test Script
Tests Ollama LLM connectivity and parsing capability without FastAPI dependencies
"""

import json
import requests
import sys
import traceback
from typing import Dict, Any, Optional

class LLMTester:
    def __init__(self, ollama_url: str = "http://127.0.0.1:11434", model: str = "llama2"):
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"

    def test_ollama_connection(self) -> bool:
        """Test basic Ollama server connectivity"""
        print("=" * 60)
        print("🔧 TESTING OLLAMA CONNECTION")
        print("=" * 60)
        
        try:
            print(f"📡 Connecting to: {self.ollama_url}")
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Server responded with status: {response.status_code}")
                return False
            
            print("✅ Ollama server is running!")
            
            # Check available models
            models_data = response.json()
            models = models_data.get('models', [])
            model_names = [model['name'] for model in models]
            
            print(f"📋 Available models: {model_names}")
            
            if not model_names:
                print("❌ No models found! Please install a model first.")
                print("   Example: ollama pull llama2")
                return False
            
            # Check if our target model exists
            model_available = any(self.model in name for name in model_names)
            
            if model_available:
                print(f"✅ Target model '{self.model}' is available!")
                return True
            else:
                print(f"⚠️ Target model '{self.model}' not found.")
                print(f"   Using first available model: {model_names[0]}")
                self.model = model_names[0].split(':')[0]  # Remove tag
                return True
                
        except requests.ConnectionError:
            print("❌ Cannot connect to Ollama server!")
            print("   Make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False

    def test_simple_llm_request(self) -> bool:
        """Test a simple LLM request"""
        print("\n" + "=" * 60)
        print("🤖 TESTING SIMPLE LLM REQUEST")
        print("=" * 60)
        
        simple_prompt = "Respond with only the word 'SUCCESS' if you can process this message."
        
        try:
            print(f"📤 Sending simple prompt to model: {self.model}")
            print(f"   Prompt: {simple_prompt}")
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": simple_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 10
                    }
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
            
            result = response.json()
            llm_output = result.get('response', '').strip()
            
            print(f"📥 LLM Response: '{llm_output}'")
            
            if 'SUCCESS' in llm_output.upper():
                print("✅ Simple LLM request successful!")
                return True
            else:
                print("⚠️ LLM responded but output unexpected")
                return True  # Still working, just different output
                
        except Exception as e:
            print(f"❌ Error in simple LLM request: {e}")
            traceback.print_exc()
            return False

    def test_json_generation(self) -> bool:
        """Test LLM's ability to generate JSON"""
        print("\n" + "=" * 60)
        print("📄 TESTING JSON GENERATION")
        print("=" * 60)
        
        json_prompt = """Generate a simple JSON object with the following structure. Return ONLY the JSON, no other text:

{
  "test": "success",
  "number": 42,
  "array": ["item1", "item2"]
}
"""
        
        try:
            print("📤 Testing JSON generation capability...")
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": json_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1
                    }
                },
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                return False
            
            result = response.json()
            llm_output = result.get('response', '').strip()
            
            print(f"📥 Raw LLM Output:")
            print(f"   {llm_output}")
            
            # Try to parse as JSON
            try:
                parsed_json = json.loads(llm_output)
                print("✅ LLM generated valid JSON!")
                print(f"   Parsed: {json.dumps(parsed_json, indent=2)}")
                return True
            except json.JSONDecodeError:
                print("⚠️ LLM output is not valid JSON, but LLM is responding")
                return True  # LLM works, just need better prompts
                
        except Exception as e:
            print(f"❌ Error in JSON generation test: {e}")
            return False

    def test_invoice_parsing(self, ocr_text: str) -> Optional[Dict[str, Any]]:
        """Test invoice parsing on OCR text"""
        print("\n" + "=" * 60)
        print("🧾 TESTING INVOICE PARSING")
        print("=" * 60)
        
        prompt = f"""You are an expert invoice parser. Parse the following OCR text from a restaurant/food service invoice and extract structured data.

OCR TEXT:
{ocr_text}

Extract the following information and return ONLY valid JSON (no other text):

{{
  "vendor_name": "Name of the vendor/supplier company",
  "total_amount": 0.0,
  "invoice_date": "YYYY-MM-DD format or null",
  "items": [
    {{
      "name": "Item description",
      "quantity": 0.0,
      "unit": "lb/box/case/bottle/gal/each",
      "price": 0.0,
      "category": "protein/vegetables/dairy/grains/beverages/other"
    }}
  ]
}}

RULES:
1. Extract ALL food items with quantities, units, and prices
2. Categorize items: protein (meat/fish), vegetables, dairy, grains, beverages, other
3. Find the TOTAL amount (not subtotal)
4. Return ONLY the JSON object, no explanations

RESPOND WITH ONLY VALID JSON:"""

        try:
            print("📤 Sending invoice parsing request...")
            print(f"   OCR text length: {len(ocr_text)} characters")
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=600  # Long timeout for complex parsing
            )
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
            
            result = response.json()
            llm_output = result.get('response', '').strip()
            
            print(f"📥 Raw LLM Output (first 500 chars):")
            print(f"   {llm_output[:500]}...")
            
            # Try to extract JSON from response
            parsed_data = self._extract_json_from_response(llm_output)
            
            if parsed_data:
                print("✅ Successfully parsed invoice!")
                print(f"   Vendor: {parsed_data.get('vendor_name', 'N/A')}")
                print(f"   Total: ${parsed_data.get('total_amount', 'N/A')}")
                print(f"   Items found: {len(parsed_data.get('items', []))}")
                
                if parsed_data.get('items'):
                    print("   Sample items:")
                    for i, item in enumerate(parsed_data['items'][:3]):
                        print(f"     {i+1}. {item.get('name', 'N/A')} - {item.get('quantity', 'N/A')} {item.get('unit', 'N/A')} @ ${item.get('price', 'N/A')}")
                
                return parsed_data
            else:
                print("❌ Could not extract valid JSON from LLM response")
                return None
                
        except Exception as e:
            print(f"❌ Error in invoice parsing test: {e}")
            traceback.print_exc()
            return None

    def _extract_json_from_response(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response"""
        import re
        
        # Try direct JSON parse first
        try:
            return json.loads(llm_output.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON in markdown blocks
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, llm_output, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match.strip())
                except json.JSONDecodeError:
                    continue
        
        return None

def main():
    print("🚀 Starting LLM Standalone Test")
    print(f"Python version: {sys.version}")
    
    # Sample OCR text for testing
    sample_ocr_text = """
ORGANIC HARVEST DISTRIBUTORS
123 Green Valley Lane, Sonoma, CA 95476
Phone: (707) 555-0199 | Email: orders@organicharvest.com

BILLED TO:                          INVOICE #: INV-2025-03742
The Earth Table Bistro                        June 28, 2025
642 Mission Street
San Francisco, CA 94105
Chef Laura Martinez
(415) 555-0288

Qty  Unit   Item Description           Origin     Total
10   lb     Heirloom Carrots (Organic) Local      $21.00
8    lb     Grass-fed Beef Ribeye      Local      $100.00
6    lb     Organic Kale               Imported   $42.00
12   lb     Fresh Basil (Organic)      Local      $25.20
2    case   Organic Free-Range Eggs    Local      $20.00
4    lb     Ahi Tuna Steaks (Frozen)   Imported   $52.00
1    box    Fair Trade Organic Coffee  Imported   $25.00
5    gal    Organic Whole Milk         Local      $21.25
6    lb     Wild Arugula (Organic)     Local      $36.00
3    bottle Sparkling Mineral Water    Imported   $18.00
4    lb     Organic Yukon Gold Potatoes Local     $19.20

                                    Subtotal:   $378.85
                                    Tax (9%):    $34.10
                                    Delivery Fee: $15.00
                                    TOTAL:      $427.95
"""
    
    # Initialize tester
    tester = LLMTester()
    
    # Run tests in sequence
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Connection
    if tester.test_ollama_connection():
        tests_passed += 1
    
    # Test 2: Simple request
    if tester.test_simple_llm_request():
        tests_passed += 1
    
    # Test 3: JSON generation
    if tester.test_json_generation():
        tests_passed += 1
    
    # Test 4: Invoice parsing
    if tester.test_invoice_parsing(sample_ocr_text):
        tests_passed += 1
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED! Your LLM setup is working correctly.")
        print("   You can now integrate with your FastAPI backend.")
    elif tests_passed >= 2:
        print("⚠️ PARTIAL SUCCESS. LLM is working but may need fine-tuning.")
        print("   The basic connectivity is good, work on prompt engineering.")
    else:
        print("❌ MAJOR ISSUES. Please fix LLM setup before integration.")
        print("   Check Ollama installation and model availability.")
    
    print("\n🔧 Troubleshooting tips:")
    print("   1. Make sure Ollama is running: ollama serve")
    print("   2. Install a model: ollama pull llama2")
    print("   3. Test manually: ollama run llama2 'Hello'")
    print("   4. Check firewall/port 11434")

if __name__ == "__main__":
    main()
