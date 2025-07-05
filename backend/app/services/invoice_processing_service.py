"""
Complete Invoice Processing Service
Combines PaddleOCR for text extraction with LLM for robust parsing
"""

import logging
from typing import Dict, Any, List
from .ocr_service import OCRService
from .llm_invoice_parser import LLMInvoiceParser

logger = logging.getLogger(__name__)

class InvoiceProcessingService:
    """
    Complete invoice processing pipeline:
    1. Use PaddleOCR to extract text from images/PDFs
    2. Use LLM parser for robust, accurate parsing
    """
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.llm_parser = LLMInvoiceParser()
        
    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        """
        Complete invoice processing pipeline
        
        Args:
            file_path: Path to invoice image or PDF
            
        Returns:
            Dict containing parsed invoice data
        """
        try:
            logger.info(f"[INFO] Processing invoice: {file_path}")
            
            # Step 1: Extract text using OCR
            logger.info("[INFO] Step 1: Extracting text with PaddleOCR...")
            extracted_text = self.ocr_service.extract_text(file_path)
            
            # Debug: Log the extracted text
            logger.info(f"[INFO] OCR extracted {len(extracted_text) if extracted_text else 0} characters")
            if extracted_text:
                logger.info(f"[INFO] OCR Text Preview (first 500 chars): {extracted_text[:500]}")
            else:
                logger.warning("[WARNING] OCR returned empty text")
            
            if not extracted_text or not extracted_text.strip():
                logger.error("[ERROR] No text extracted from image")
                return {
                    'success': False,
                    'error': 'No text extracted from image',
                    'ocr_result': {'text': extracted_text, 'success': False}
                }
            
            # Step 2: Parse with LLM
            logger.info("[INFO] Step 2: Parsing with LLM...")
            parsed_data = self.llm_parser.parse_invoice(extracted_text)
            
            if not parsed_data:
                logger.error("[ERROR] LLM parsing returned empty result")
                return {
                    'success': False,
                    'error': 'Failed to parse invoice data',
                    'ocr_result': {'text': extracted_text, 'success': True}
                }
            
            logger.info(f"[SUCCESS] Successfully parsed invoice with method: {parsed_data.get('parsing_method', 'unknown')}")
            
            # Step 3: Process items for carbon footprint
            logger.info("[STEP 3] Processing items for carbon footprint...")
            processed_items = self._process_items_for_carbon_footprint(parsed_data.get('items', []))
            
            # Combine results
            result = {
                'success': True,
                'ocr_result': {
                    'text': extracted_text,
                    'success': True
                },
                'parsed_data': parsed_data,
                'processed_items': processed_items,
                'parsing_method': parsed_data.get('parsing_method', 'unknown')
            }
            
            logger.info("[SUCCESS] Invoice processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing invoice: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'ocr_result': {'text': '', 'success': False}
            }
            logger.info("Step 2: Parsing with LLM...")
            parsed_result = self.llm_parser.parse_invoice(extracted_text)
            # Debug: print parsed_result for diagnosis
            logger.debug(f"LLM/Parser result: {parsed_result}")
            if not parsed_result.get('success', False):
                return {
                    'success': False,
                    'error': 'Invoice parsing failed',
                    'ocr_result': {'text': extracted_text, 'success': True, 'confidence': 0.8},
                    'llm_result': parsed_result
                }
            
            # Step 3: Combine results
            final_result = {
                'success': True,
                'processing_method': 'PaddleOCR + LLM',
                'vendor_name': parsed_result.get('vendor_name'),
                'total_amount': parsed_result.get('total_amount'),
                'invoice_date': parsed_result.get('invoice_date'),
                'items': parsed_result.get('items', []),
                'categorized_items': parsed_result.get('categorized_items', {}),
                'item_count': len(parsed_result.get('items', [])),
                'confidence': parsed_result.get('confidence', 0.0),
                'ocr_confidence': 0.8,  # Default confidence for PaddleOCR
                'extracted_text': extracted_text,
                'processing_time': {
                    'ocr_time': 0,  # Not tracking OCR time separately
                    'llm_time': parsed_result.get('processing_time', 0)
                }
            }
            
            logger.info(f"Successfully processed invoice: {final_result['item_count']} items found")
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing invoice: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def process_invoice_from_text(self, text: str) -> Dict[str, Any]:
        """
        Process invoice from already extracted text (skip OCR)
        
        Args:
            text: Extracted text from invoice
            
        Returns:
            Dict containing parsed invoice data
        """
        try:
            logger.info("Processing invoice from text with LLM...")
            
            parsed_result = self.llm_parser.parse_invoice(text)
            # Debug: print parsed_result for diagnosis
            logger.debug(f"LLM/Parser result: {parsed_result}")
            if not parsed_result.get('success', False):
                return {
                    'success': False,
                    'error': 'Invoice parsing failed',
                    'llm_result': parsed_result
                }
            
            final_result = {
                'success': True,
                'processing_method': 'LLM only',
                'vendor_name': parsed_result.get('vendor_name'),
                'total_amount': parsed_result.get('total_amount'),
                'invoice_date': parsed_result.get('invoice_date'),
                'items': parsed_result.get('items', []),
                'categorized_items': parsed_result.get('categorized_items', {}),
                'item_count': len(parsed_result.get('items', [])),
                'confidence': parsed_result.get('confidence', 0.0),
                'extracted_text': text,
                'processing_time': {
                    'ocr_time': 0,
                    'llm_time': parsed_result.get('processing_time', 0)
                }
            }
            
            logger.info(f"Successfully processed text: {final_result['item_count']} items found")
            return final_result
            
        except Exception as e:
            logger.error(f"Error processing text: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}'
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get status of all services
        
        Returns:
            Dict containing service status information
        """
        try:
            # Test OCR service
            ocr_status = self.ocr_service.get_service_info()
            
            # Test LLM service
            llm_status = self.llm_parser.get_service_status()
            
            return {
                'ocr_service': {
                    'available': True,
                    'engine': 'PaddleOCR',
                    'info': ocr_status
                },
                'llm_service': {
                    'available': llm_status.get('available', False),
                    'engine': 'Ollama',
                    'model': llm_status.get('model'),
                    'status': llm_status.get('status')
                },
                'combined_service': {
                    'available': llm_status.get('available', False),
                    'ready_for_processing': llm_status.get('available', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            return {
                'ocr_service': {'available': False, 'error': str(e)},
                'llm_service': {'available': False, 'error': str(e)},
                'combined_service': {'available': False, 'error': str(e)}
            }
    
    def _process_items_for_carbon_footprint(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process parsed invoice items for carbon footprint calculation"""
        processed_items = []
        
        for item in items:
            processed_item = {
                'name': item.get('name', ''),
                'quantity': item.get('quantity', 1),
                'unit': item.get('unit', 'item'),
                'price': item.get('price', 0.0),
                'category': item.get('category', 'unknown'),
                'carbon_footprint': 0.0  # Will be calculated by carbon service
            }
            processed_items.append(processed_item)
        
        return processed_items

# Test code for standalone execution
if __name__ == "__main__":
    # Test the complete service
    
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
    
    # Initialize service
    processor = InvoiceProcessingService()
    
    # Test service status
    print("=== Service Status ===")
    status = processor.get_service_status()
    print(f"OCR Available: {status['ocr_service']['available']}")
    print(f"LLM Available: {status['llm_service']['available']}")
    print(f"Ready for Processing: {status['combined_service']['ready_for_processing']}")
    print()
    
    # Test text processing
    print("=== Testing Text Processing ===")
    result = processor.process_invoice_from_text(sample_ocr_text)
    
    if result['success']:
        print(f"[SUCCESS] Processing successful!")
        print(f"Vendor: {result['vendor_name']}")
        print(f"Total: ${result['total_amount']}")
        print(f"Date: {result['invoice_date']}")
        print(f"Items found: {result['item_count']}")
        print(f"Confidence: {result['confidence']:.2f}")
        
        print("\nItems:")
        for item in result['items'][:3]:  # Show first 3 items
            print(f"  - {item['name']}: {item['quantity']} {item['unit']} @ ${item['price']}")
        
        if result['item_count'] > 3:
            print(f"  ... and {result['item_count'] - 3} more items")
            
    else:
        print(f"[ERROR] Processing failed: {result['error']}")
    
    # If you want to test with an actual image file:
    # result = processor.process_invoice("path/to/your/invoice.jpg")
