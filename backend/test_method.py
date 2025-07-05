import sys
import os
sys.path.append('.')
from app.services.invoice_processing_service import InvoiceProcessingService

processor = InvoiceProcessingService()
items = [{'name': 'test', 'quantity': 1, 'unit': 'kg', 'price': 5.0}]
result = processor._process_items_for_carbon_footprint(items)
print('Method exists and works:', result)
