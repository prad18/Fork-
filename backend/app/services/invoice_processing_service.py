"""
Complete Invoice Processing Service
Combines PaddleOCR for text extraction with LLM for robust parsing
"""

import logging
from typing import Dict, Any
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
            logger.info(f"Processing invoice: {file_path}")
            
            # Step 1: Extract text using OCR
            logger.info("Step 1: Extracting text with PaddleOCR...")
            ocr_result = self.ocr_service.extract_text(file_path)
            
            if not ocr_result.get('success', False):
                return {
                    'success': False,
                    'error': 'OCR extraction failed',
                    'ocr_result': ocr_result
                }
            
            extracted_text = ocr_result.get('text', '')
            if not extracted_text:
                return {
                    'success': False,
                    'error': 'No text extracted from image',
                    'ocr_result': ocr_result
                }
            
            logger.info(f"OCR extracted {len(extracted_text)} characters")
            
            # Step 2: Parse with LLM
            logger.info("Step 2: Parsing with LLM...")
            parsed_result = self.llm_parser.parse_invoice(extracted_text)
            
            if not parsed_result.get('success', False):
                return {
                    'success': False,
                    'error': 'LLM parsing failed',
                    'ocr_result': ocr_result,
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
                'ocr_confidence': ocr_result.get('confidence', 0.0),
                'extracted_text': extracted_text,
                'processing_time': {
                    'ocr_time': ocr_result.get('processing_time', 0),
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
            
            if not parsed_result.get('success', False):
                return {
                    'success': False,
                    'error': 'LLM parsing failed',
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

# Example usage and testing
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
        print(f"✅ Processing successful!")
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
        print(f"❌ Processing failed: {result['error']}")
    
    # If you want to test with an actual image file:
    # result = processor.process_invoice("path/to/your/invoice.jpg")
