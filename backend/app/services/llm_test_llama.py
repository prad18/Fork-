import json
from llm_invoice_parser import LLMInvoiceParser

if __name__ == "__main__":
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
    result = parser._llm_parse_with_prompt(sample_ocr_text, parser._create_parsing_prompt(sample_ocr_text))
    print(json.dumps(result, indent=2))
