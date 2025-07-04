import json
import requests
from typing import Dict, Optional, Any
import re

class LLMInvoiceParser:
    """
    LLM-based invoice parser using local Ollama for robust text parsing.
    This parser uses a local LLM to understand and extract structured data
    from OCR text, providing much better accuracy than regex patterns.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama2"):
        """
        Initialize the LLM parser
        
        Args:
            ollama_url: URL of the local Ollama server
            model: Model name to use (e.g., 'llama2', 'llama3.2', 'mistral', 'phi3')
        """
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
        
    def parse_invoice(self, ocr_text: str) -> Dict[str, Any]:
        """
        Parse invoice using LLM for robust extraction
        
        Args:
            ocr_text: Raw OCR text from the invoice
            
        Returns:
            Dictionary with structured invoice data
        """
        if not ocr_text or len(ocr_text.strip()) < 10:
            return self._empty_result()
        
        try:
            # Check if Ollama is available
            if not self._check_ollama_available():
                print("⚠️ Ollama not available, falling back to basic extraction")
                return self._fallback_parse(ocr_text)
            
            # Use LLM to parse the invoice
            parsed_data = self._llm_parse(ocr_text)
            
            if parsed_data:
                return parsed_data
            else:
                print("⚠️ LLM parsing failed, falling back to basic extraction")
                return self._fallback_parse(ocr_text)
                
        except Exception as e:
            print(f"❌ Error in LLM parsing: {e}")
            return self._fallback_parse(ocr_text)
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama server is running and model is available"""
        try:
            # Check if server is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            # Check for exact match or partial match
            model_available = any(self.model in name for name in model_names)
            
            if not model_available:
                print(f"⚠️ Model '{self.model}' not found. Available models: {model_names}")
                # Try to use the first available model
                if model_names:
                    self.model = model_names[0].split(':')[0]  # Remove tag if present
                    print(f"🔄 Using available model: {self.model}")
                    return True
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    def _llm_parse(self, ocr_text: str) -> Optional[Dict[str, Any]]:
        """Use LLM to parse the invoice text"""
        
        # Create a detailed prompt for the LLM
        prompt = self._create_parsing_prompt(ocr_text)
        
        try:
            # Make request to Ollama
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Low temperature for consistent output
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=60  # Give LLM time to process
            )
            
            if response.status_code != 200:
                print(f"❌ Ollama API error: {response.status_code}")
                return None
            
            # Parse the response
            result = response.json()
            llm_output = result.get('response', '').strip()
            
            if not llm_output:
                print("❌ Empty response from LLM")
                return None
            
            # Extract JSON from LLM response
            parsed_data = self._extract_json_from_response(llm_output)
            
            if parsed_data:
                # Validate and clean the parsed data
                return self._validate_and_clean_data(parsed_data)
            else:
                print("❌ Could not extract valid JSON from LLM response")
                return None
                
        except Exception as e:
            print(f"❌ Error in LLM request: {e}")
            return None
    
    def _create_parsing_prompt(self, ocr_text: str) -> str:
        """Create a detailed prompt for the LLM to parse invoice data"""
        
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
      "category": "protein/vegetables/dairy/grains/beverages/other",
      "confidence": 0.95
    }}
  ],
  "parsing_confidence": 0.95,
  "item_count": 0
}}

RULES:
1. Extract ALL food items with quantities, units, and prices
2. Categorize items: protein (meat/fish), vegetables, dairy, grains, beverages, other
3. Find the TOTAL amount (not subtotal)
4. Clean and normalize item names
5. Convert quantities to numbers
6. Return ONLY the JSON object, no explanations
7. If unsure about a value, use reasonable defaults
8. For dates, try to parse into YYYY-MM-DD format

RESPOND WITH ONLY VALID JSON:"""

        return prompt
    
    def _extract_json_from_response(self, llm_output: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from LLM response, handling various formats"""
        
        # Try to find JSON in the response
        json_patterns = [
            r'\{.*\}',  # Look for { ... }
            r'```json\s*(\{.*\})\s*```',  # Look for ```json { ... } ```
            r'```\s*(\{.*\})\s*```',  # Look for ``` { ... } ```
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, llm_output, re.DOTALL)
            for match in matches:
                try:
                    # Clean the JSON string
                    json_str = match.strip()
                    parsed = json.loads(json_str)
                    return parsed
                except json.JSONDecodeError:
                    continue
        
        # If no JSON found, try parsing the entire response
        try:
            return json.loads(llm_output.strip())
        except json.JSONDecodeError:
            print("❌ Could not parse JSON from LLM response")
            print(f"LLM Output: {llm_output[:500]}...")
            return None
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed data from LLM"""
        
        # Ensure required fields exist
        cleaned_data = {
            "vendor_name": data.get("vendor_name"),
            "total_amount": None,
            "invoice_date": data.get("invoice_date"),
            "items": [],
            "categorized_items": {},
            "parsing_confidence": data.get("parsing_confidence", 0.8),
            "item_count": 0
        }
        
        # Validate total amount
        try:
            total = data.get("total_amount")
            if total is not None:
                cleaned_data["total_amount"] = float(total)
        except (ValueError, TypeError):
            pass
        
        # Validate and clean items
        items = data.get("items", [])
        valid_items = []
        
        for item in items:
            if not isinstance(item, dict):
                continue
                
            try:
                cleaned_item = {
                    "name": str(item.get("name", "Unknown Item")).strip(),
                    "quantity": float(item.get("quantity", 1.0)),
                    "unit": str(item.get("unit", "each")).lower().strip(),
                    "price": float(item.get("price", 0.0)),
                    "category": str(item.get("category", "other")).lower().strip(),
                    "confidence": float(item.get("confidence", 0.8)),
                    "attributes": {}
                }
                
                # Validate that we have minimum required data
                if cleaned_item["name"] and cleaned_item["price"] > 0:
                    valid_items.append(cleaned_item)
                    
            except (ValueError, TypeError):
                continue
        
        cleaned_data["items"] = valid_items
        cleaned_data["item_count"] = len(valid_items)
        
        # Create categorized items
        categorized = {}
        for item in valid_items:
            category = item["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item)
        
        cleaned_data["categorized_items"] = categorized
        
        return cleaned_data
    
    def _fallback_parse(self, ocr_text: str) -> Dict[str, Any]:
        """Simple fallback parsing when LLM is not available"""
        
        lines = ocr_text.split('\n')
        
        # Basic vendor extraction
        vendor_name = None
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 5 and any(word in line.upper() for word in ['DISTRIBUTORS', 'COMPANY', 'FARM', 'MARKET']):
                vendor_name = line
                break
        
        # Basic total extraction
        total_amount = None
        for line in reversed(lines):
            if 'total' in line.lower() and '$' in line:
                match = re.search(r'\$([0-9,]+\.?[0-9]*)', line)
                if match:
                    try:
                        total_amount = float(match.group(1).replace(',', ''))
                        break
                    except:
                        pass
        
        # Basic date extraction
        invoice_date = None
        date_pattern = r'([A-Za-z]{3,9}\s+[0-9]{1,2},?\s+[0-9]{2,4})'
        for line in lines[:10]:
            match = re.search(date_pattern, line)
            if match:
                invoice_date = match.group(1)
                break
        
        return {
            "vendor_name": vendor_name,
            "total_amount": total_amount,
            "invoice_date": invoice_date,
            "items": [],
            "categorized_items": {},
            "parsing_confidence": 0.3,
            "item_count": 0
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "vendor_name": None,
            "total_amount": None,
            "invoice_date": None,
            "items": [],
            "categorized_items": {},
            "parsing_confidence": 0.0,
            "item_count": 0
        }

# Usage example and testing
if __name__ == "__main__":
    # Test the parser with sample data
    sample_text = """
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
    10   lb     Heirloom Carrots (Organic) Local      $2.10
    8    lb     Grass-fed Beef Ribeye      Local      $12.50
    6    lb     Organic Kale               Imported   $7.00
    12   lb     Fresh Basil (Organic)      Local      $2.10
    2    case   Organic Free-Range Eggs    Local      $10.00
    4    lb     Ahi Tuna Steaks (Frozen)   Imported   $13.00
    1    box    Fair Trade Organic Coffee  Imported   $25.00
    5    gal    Organic Whole Milk         Local      $21.25
    6    lb     Wild Arugula (Organic)     Local      $21.00
    3    bottle Sparkling Mineral Water    Imported   $18.00
    4    lb     Organic Yukon Gold Potatoes Local     $9.60
    
                                        Subtotal:   $378.85
                                        Tax (9):     34.10
                                        Delivery Fee: $15.0
                                        TOTAL:      $427.95
    """
    
    parser = LLMInvoiceParser()
    result = parser.parse_invoice(sample_text)
    print(json.dumps(result, indent=2))
