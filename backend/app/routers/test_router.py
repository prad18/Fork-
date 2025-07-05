"""
Test endpoint without authentication for testing invoice processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import os
import shutil
import uuid
from datetime import datetime

from app.services.invoice_processing_service import InvoiceProcessingService
from app.core.config import settings

router = APIRouter()

# Initialize service
invoice_processor = InvoiceProcessingService()

@router.post("/test-upload")
async def test_upload_invoice(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Test upload and process an invoice file WITHOUT authentication"""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not allowed. Supported types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"test_{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Process invoice immediately
    try:
        print(f"🔄 Processing test invoice: {file.filename}")
        result = invoice_processor.process_invoice(file_path)
        
        # Clean up test file
        try:
            os.remove(file_path)
        except:
            pass
        
        return {
            "success": True,
            "filename": file.filename,
            "processing_result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        # Clean up test file on error
        try:
            os.remove(file_path)
        except:
            pass
        
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/test-health")
async def test_health() -> Dict[str, Any]:
    """Test health endpoint without authentication"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Test endpoint is working"
    }
