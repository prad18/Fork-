import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime  
from dataclasses import dataclass

@dataclass
class ExtractedItem:
    name: str
    quantity: float
    unit: str
    price: float
    category: str
    confidence: float
    attributes: Dict[str, Any]

class ImprovedInvoiceParser:
    """
    Improved invoice parser specifically designed for table-format invoices
    like the Organic Harvest Distributors invoice
    """
    
    def __init__(self):
        # Enhanced vendor patterns
        self.vendor_patterns = [
            r'^([A-Z][A-Z\s&,.\'\-]+(?:DISTRIBUTORS|DISTRIBUTORS|COMPANY|FARM|MARKET|LLC|Inc|Co\.?|Corp|Ltd))',
            r'^([A-Z]{2,}[A-Z\s&,.\'\-]*(?:DISTRIBUTORS|COMPANY|FARM|MARKET))',
            r'(?:from|vendor|supplier)[:]\s*([^\n]+)',
        ]
        
        # Enhanced total patterns - look for final total, not subtotal
        self.total_patterns = [
            r'(?:TOTAL|Grand\s+Total|Amount\s+Due|Balance\s+Due)[:]\s*\$?([0-9,]+\.?[0-9]*)',
            r'TOTAL[:]\s*\$([0-9,]+\.?[0-9]*)',
            r'\$([0-9,]+\.?[0-9]*)\s*$',  # Last dollar amount on a line
        ]
        
        # Date patterns
        self.date_patterns = [
            r'([A-Za-z]{3,9}\s+[0-9]{1,2},?\s+[0-9]{2,4})',  # "June 28, 2025"
            r'([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
            r'(?:invoice\s+date|date)[:]\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})',
        ]
        
        # Ingredient categories
        self.ingredient_categories = {
            'protein': ['beef', 'chicken', 'pork', 'fish', 'tuna', 'salmon', 'ribeye', 'steak'],
            'vegetables': ['carrot', 'kale', 'arugula', 'potato', 'basil', 'onion', 'tomato'],
            'dairy': ['milk', 'cheese', 'butter', 'cream', 'eggs'],
            'grains': ['rice', 'bread', 'flour', 'pasta'],
            'beverages': ['water', 'coffee', 'tea', 'juice'],
            'other': []
        }
    
    def parse_invoice(self, ocr_text: str) -> Dict[str, Any]:
        """Main parsing function"""
        
        if not ocr_text:
            return self._empty_result()
        
        # Clean the text
        cleaned_text = self._clean_text(ocr_text)
        lines = cleaned_text.split('\n')
        
        # Extract basic information
        vendor_name = self._extract_vendor(lines)
        total_amount = self._extract_total(lines)
        invoice_date = self._extract_date(lines)
        
        # Extract table items
        items = self._extract_table_items(lines)
        
        # Categorize items
        categorized_items = self._categorize_items(items)
        
        return {
            "vendor_name": vendor_name,
            "total_amount": total_amount,
            "invoice_date": invoice_date,
            "items": [self._item_to_dict(item) for item in items],
            "categorized_items": categorized_items,
            "parsing_confidence": 0.9 if vendor_name and items else 0.5,
            "item_count": len(items)
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean OCR text while preserving table structure"""
        
        print(f"🧹 Original text length: {len(text)}")
        print(f"🧹 Original lines: {len(text.split('\n'))}")
        
        # DON'T remove pipes - we need them for table structure!
        # Only fix obvious OCR errors
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between joined words
        
        print(f"🧹 Cleaned text length: {len(text)}")
        print(f"🧹 Cleaned lines: {len(text.split('\n'))}")
        
        return text
    
    def _extract_vendor(self, lines: List[str]) -> Optional[str]:
        """Extract vendor name from first few lines"""
        
        # Look in first 5 lines for vendor
        for line in lines[:5]:
            line = line.strip()
            if len(line) < 5:
                continue
                
            # Check if line matches vendor patterns
            for pattern in self.vendor_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    vendor = match.group(1).strip()
                    # Clean up vendor name
                    vendor = re.sub(r'\s+', ' ', vendor)
                    return vendor
        
        return None
    
    def _extract_total(self, lines: List[str]) -> Optional[float]:
        """Extract total amount - look for TOTAL: not Subtotal:"""
        
        # Look from bottom up for total
        for line in reversed(lines):
            line = line.strip()
            
            # Skip subtotal lines, look for final total
            if 'subtotal' in line.lower():
                continue
                
            # Try multiple total patterns
            total_patterns_extended = [
                r'TOTAL[:]\s*\$?([0-9,]+\.?[0-9]*)',
                r'(?:Grand\s+)?Total[:]\s*\$?([0-9,]+\.?[0-9]*)',
                r'Amount\s+Due[:]\s*\$?([0-9,]+\.?[0-9]*)',
                r'Balance[:]\s*\$?([0-9,]+\.?[0-9]*)',
                r'TOTAL\s*[:]\s*\$([0-9,]+\.?[0-9]*)',  # TOTAL: $427.95
                r'TOTAL\s+\$([0-9,]+\.?[0-9]*)',  # TOTAL $427.95
                r'\$([0-9,]+\.?[0-9]*)\s*$',  # Last dollar amount on a line
            ]
            
            for pattern in total_patterns_extended:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    try:
                        amount_str = match.group(1).replace(',', '')
                        amount = float(amount_str)
                        print(f"✅ Found total: ${amount} in line: {line}")
                        return amount
                    except:
                        continue
        
        # Also try searching through all text as one string for TOTAL patterns
        all_text = ' '.join(lines)
        total_patterns_global = [
            r'TOTAL[:]\s*\$([0-9,]+\.?[0-9]*)',
            r'TOTAL\s*[:]\s*\$([0-9,]+\.?[0-9]*)',
        ]
        
        for pattern in total_patterns_global:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    print(f"✅ Found total (global search): ${amount}")
                    return amount
                except:
                    continue
        
        print("❌ No total amount found")
        return None
    
    def _extract_date(self, lines: List[str]) -> Optional[str]:
        """Extract invoice date"""
        
        for line in lines[:10]:  # Look in first 10 lines
            for pattern in self.date_patterns:
                match = re.search(pattern, line)
                if match:
                    date_str = match.group(1)
                    # Try to parse and reformat
                    try:
                        if '/' in date_str:
                            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
                        else:
                            date_obj = datetime.strptime(date_str, '%B %d, %Y')
                        return date_obj.strftime('%Y-%m-%d')
                    except:
                        return date_str
        
        return None
    
    def _extract_table_items(self, lines: List[str]) -> List[ExtractedItem]:
        """Extract items from table format"""
        items = []
        
        print(f"🔍 Analyzing {len(lines)} lines for table structure...")
        
        # First, check if we have one big line with all the data (common with OCR)
        if len(lines) == 1 and len(lines[0]) > 500:
            print("🔄 Detected single large OCR line, attempting to split by items...")
            # Split the line by item patterns
            big_line = lines[0]
            split_lines = self._split_ocr_line_by_items(big_line)
            if split_lines:
                lines = split_lines
                print(f"✅ Split into {len(lines)} item lines")
        
        # Find table start - look for header with Qty, Unit, Item Description, etc.
        table_start = -1
        for i, line in enumerate(lines):
            line_lower = line.lower()
            print(f"  Line {i}: {line[:60]}...")
            
            # Look for table headers with multiple variations
            if (('qty' in line_lower or 'quantity' in line_lower) and 
                ('unit' in line_lower) and 
                ('item' in line_lower or 'description' in line_lower)):
                table_start = i + 1
                print(f"✅ Found table header at line {i}: {line}")
                break
            
            # Alternative: look for specific known headers
            if 'qty unit item description' in line_lower.replace(' ', ''):
                table_start = i + 1
                print(f"✅ Found table header (alt) at line {i}: {line}")
                break
        
        # If no clear header found, look for lines that might be table rows
        if table_start == -1:
            print("⚠️ No clear table header found, searching for table rows...")
            
            # Look for lines with quantity + unit + description + price pattern
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) < 10:
                    continue
                    
                # Check if line has quantity + unit + price pattern
                if self._looks_like_table_row(line):
                    table_start = i
                    print(f"✅ Found potential table start at line {i}: {line}")
                    break
        
        if table_start == -1:
            print("❌ Could not find table structure")
            return items
        
        print(f"✅ Processing table starting at line {table_start}")
        
        # Process table rows until we hit totals
        for i in range(table_start, len(lines)):
            line = lines[i].strip()
            
            # Stop at totals section
            if any(word in line.lower() for word in ['subtotal', 'tax', 'delivery', 'total']):
                print(f"🛑 Stopping at totals line {i}: {line}")
                break
            
            # Skip empty lines or separators
            if not line or len(line) < 10 or re.match(r'^[-=_\s]+$', line):
                continue
            
            print(f"📝 Processing line {i}: {line}")
            
            # Parse table row
            item = self._parse_table_row(line)
            if item:
                items.append(item)
                print(f"✅ Parsed: {item.name} - {item.quantity} {item.unit} - ${item.price}")
            else:
                print(f"❌ Could not parse line: {line}")
        
        print(f"✅ Found {len(items)} items total")
        return items
    
    def _split_ocr_line_by_items(self, big_line: str) -> List[str]:
        """Split a big OCR line into individual item lines based on patterns"""
        
        print(f"🔍 Processing line of {len(big_line)} characters")
        print(f"🔍 Sample text: {big_line[:300]}...")
        
        # IMPROVED: Based on the OCR output, items are separated by specific patterns
        # The key insight is that each item starts with a quantity number followed by unit
        
        # First, let's try to find all item start positions
        # Pattern: number + space + unit (lb, box, case, bottle, gal, bb)
        item_start_pattern = r'(\d+\s+(?:lb|box|case|bottle|gal|bb|each))\s+'
        starts = list(re.finditer(item_start_pattern, big_line, re.IGNORECASE))
        
        print(f"🔍 Found {len(starts)} potential item starts")
        
        if len(starts) == 0:
            return []
        
        items = []
        
        for i, start_match in enumerate(starts):
            start_pos = start_match.start()
            
            # Find the end of this item (start of next item or end of string)
            if i + 1 < len(starts):
                end_pos = starts[i + 1].start()
            else:
                end_pos = len(big_line)
            
            # Extract the item text
            item_text = big_line[start_pos:end_pos].strip()
            
            # Clean up the item text
            item_text = re.sub(r'\s+', ' ', item_text)
            
            # Make sure it has a price
            if '$' in item_text and len(item_text) > 10:
                items.append(item_text)
                print(f"  Found item {len(items)}: {item_text[:80]}...")
        
        if len(items) >= 4:  # Good number of items found
            return items
        
        # Fallback: More aggressive pattern matching
        print("🔍 Using fallback pattern matching...")
        
        # Enhanced patterns to catch all items
        fallback_patterns = [
            # Pattern 1: qty unit + everything until next qty unit (most comprehensive)
            r'(\d+\s+(?:lb|box|case|bottle|gal|bb)\s+[^$]*?\$[0-9]+\.?[0-9]*[^0-9]*?)(?=\d+\s+(?:lb|box|case|bottle|gal|bb)|$)',
            # Pattern 2: Any text chunk that has unit + price
            r'((?:lb|box|case|bottle|gal|bb)\s+[^$]*?\$[0-9]+\.?[0-9]*)',
            # Pattern 3: Find prices and work backwards to find items
            r'([^$]*?\$[0-9]+\.?[0-9]*)',
        ]
        
        all_items = []
        for pattern_idx, pattern in enumerate(fallback_patterns):
            matches = re.findall(pattern, big_line, re.IGNORECASE | re.DOTALL)
            
            if matches:
                print(f"🔍 Fallback pattern {pattern_idx + 1} found {len(matches)} items")
                
                # Filter matches to only include those with units and reasonable length
                valid_matches = []
                for match in matches:
                    match = match.strip()
                    if (len(match) > 15 and  # Reasonable length
                        any(unit in match.lower() for unit in ['lb', 'box', 'case', 'bottle', 'gal', 'bb']) and
                        '$' in match):
                        valid_matches.append(match)
                
                if valid_matches:
                    all_items.extend(valid_matches)
                    if len(valid_matches) >= 6:  # Good number of items
                        break
        
        # Remove duplicates
        unique_items = []
        seen = set()
        for item in all_items:
            # Use first 40 characters for duplicate detection
            key = item[:40].strip().lower()
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        print(f"✅ Found {len(unique_items)} unique items")
        return unique_items
    
    def _looks_like_table_row(self, line: str) -> bool:
        """Check if a line looks like a table row with quantity, unit, and price"""
        
        # Look for pattern: number + unit + text + price
        # Example: "10 lb Heirloom Carrots (Organic) Local $2.10"
        pattern = r'^\s*\d+\s+[a-zA-Z]+\s+.*\$\d+\.?\d*'
        if re.match(pattern, line):
            return True
        
        # Also check for pipe-separated format from OCR
        # Example: "| am [erass-Fes beef ribeye | oval | 932.50 |"
        if '|' in line and '$' in line:
            return True
            
        # Check for lines with food items and prices
        food_indicators = ['beef', 'chicken', 'kale', 'basil', 'arugula', 'carrot', 'organic']
        if any(food in line.lower() for food in food_indicators) and '$' in line:
            return True
        
        return False
    
    def _parse_table_row(self, line: str) -> Optional[ExtractedItem]:
        """Parse individual table row - enhanced for OCR output"""
        
        print(f"  🔍 Parsing: {line}")
        
        # ENHANCED: Handle the specific OCR patterns we're seeing
        # Pattern examples from the invoice:
        # "10 lb Heirloom Carrots (Organic) Local $2.10"
        # "2 box Grass-Fed Beef Ribeye Oval $32.50"
        
        # Try multiple parsing patterns in order of specificity
        patterns = [
            # Pattern 1: qty unit description (details) origin $price
            r'^(\d+)\s+(lb|box|case|bottle|gal|bb)\s+([^($]*?)(?:\([^)]*\))?\s*([^$]*?)\s*\$([0-9]+\.?[0-9]*).*?$',
            # Pattern 2: qty unit description $price
            r'^(\d+)\s+(lb|box|case|bottle|gal|bb)\s+([^$]*?)\s*\$([0-9]+\.?[0-9]*).*?$',
            # Pattern 3: qty unit words... $price (catch-all)
            r'^(\d+)\s+(lb|box|case|bottle|gal|bb)\s+(.*?)\s*\$([0-9]+\.?[0-9]*).*?$',
        ]
        
        for pattern_idx, pattern in enumerate(patterns):
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                groups = match.groups()
                print(f"  ✅ Matched pattern {pattern_idx + 1}: {groups}")
                
                quantity = int(groups[0])
                unit = groups[1].lower()
                
                if pattern_idx == 0:  # Pattern 1: has origin info
                    description = groups[2].strip()
                    origin = groups[3].strip()
                    price = float(groups[4])
                    
                    # Combine description and origin
                    full_name = f"{description} {origin}".strip()
                    
                elif pattern_idx == 1:  # Pattern 2: simple description
                    description = groups[2].strip()
                    price = float(groups[3])
                    full_name = description
                    
                else:  # Pattern 3: catch-all
                    description = groups[2].strip()
                    price = float(groups[3])
                    full_name = description
                
                # Clean up the name
                full_name = re.sub(r'\s+', ' ', full_name).strip()
                
                if not full_name:
                    full_name = "Unknown Item"
                
                print(f"  ✅ Extracted: {quantity} {unit} {full_name} ${price}")
                
                return ExtractedItem(
                    name=full_name,
                    quantity=float(quantity),
                    unit=unit,
                    price=price,
                    category=self._categorize_ingredient(full_name),
                    confidence=0.95,
                    attributes={}
                )
        
        # Fallback: Try to extract any item with price
        price_match = re.search(r'\$([0-9]+\.?[0-9]*)', line)
        if price_match:
            price = float(price_match.group(1))
            
            # Extract quantity
            qty_match = re.search(r'^(\d+)', line.strip())
            quantity = float(qty_match.group(1)) if qty_match else 1.0
            
            # Extract unit
            unit_match = re.search(r'\d+\s*(lb|box|case|bottle|gal|bb)', line, re.IGNORECASE)
            unit = unit_match.group(1).lower() if unit_match else "each"
            
            # Extract name (text between unit and price)
            if unit_match:
                start_pos = unit_match.end()
                end_pos = price_match.start()
                name = line[start_pos:end_pos].strip()
            else:
                # Just use text before price
                name = line[:price_match.start()].strip()
                # Remove quantity from beginning
                name = re.sub(r'^\d+\s*', '', name).strip()
            
            if name and len(name) > 2:
                print(f"  ✅ Fallback extracted: {quantity} {unit} {name} ${price}")
                
                return ExtractedItem(
                    name=name,
                    quantity=quantity,
                    unit=unit,
                    price=price,
                    category=self._categorize_ingredient(name),
                    confidence=0.7,
                    attributes={}
                )
        
        print(f"  ❌ Could not parse line: {line}")
        return None
    
    def _categorize_ingredient(self, name: str) -> str:
        """Categorize ingredient based on description"""
        if not name:
            return 'other'
            
        name_lower = name.lower()
        
        for category, keywords in self.ingredient_categories.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return category
        
        return 'other'
    
    def _categorize_items(self, items: List[ExtractedItem]) -> Dict[str, List[Dict]]:
        """Group items by category"""
        categorized = {}
        
        for item in items:
            if item.category not in categorized:
                categorized[item.category] = []
            categorized[item.category].append(self._item_to_dict(item))
        
        return categorized
    
    def _item_to_dict(self, item: ExtractedItem) -> Dict[str, Any]:
        """Convert ExtractedItem to dictionary"""
        return {
            'name': item.name,
            'quantity': item.quantity,
            'unit': item.unit,
            'price': item.price,
            'category': item.category,
            'confidence': item.confidence,
            'attributes': item.attributes
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

# Test the parser
if __name__ == "__main__":
    # Test with sample invoice text
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
    
    parser = ImprovedInvoiceParser()
    result = parser.parse_invoice(sample_text)
    print(json.dumps(result, indent=2))
