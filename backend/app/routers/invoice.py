from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import shutil
import uuid

from app.database import get_db
from app.models import Invoice, User
from app.dependencies import get_current_user
from app.services.invoice_processing_service import InvoiceProcessingService
from app.services.ai_recommendation_service import AIRecommendationEngine
from app.services.carbon_service import CarbonService
from app.core.config import settings

router = APIRouter()

class InvoiceResponse(BaseModel):
    id: int
    filename: str
    upload_date: datetime
    processing_status: str
    parsed_data: Optional[Dict[str, Any]]
    total_amount: Optional[float]
    vendor_name: Optional[str]
    invoice_date: Optional[datetime]
    
    class Config:
        from_attributes = True

class InvoiceAnalysisResponse(BaseModel):
    invoice: InvoiceResponse
    extracted_items: List[Dict[str, Any]]
    carbon_analysis: Dict[str, Any]
    ai_recommendations: Dict[str, Any]
    sustainability_score: float

# Initialize services
invoice_processor = InvoiceProcessingService()
ai_engine = AIRecommendationEngine()
carbon_service = CarbonService()

@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process an invoice file"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 Starting invoice upload for user {current_user.id}")
    logger.info(f"🔍 File: {file.filename}, Content-Type: {file.content_type}")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        logger.error(f"[ERROR] Invalid file type: {file_extension}")
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not allowed. Supported types: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_FOLDER, unique_filename)
    
    logger.info(f"🔍 Saving file to: {file_path}")
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"✅ File saved successfully")
    except Exception as e:
        logger.error(f"[ERROR] Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create invoice record
    invoice = Invoice(
        filename=file.filename,
        file_path=file_path,
        user_id=current_user.id,
        upload_date=datetime.utcnow(),
        processing_status="pending"
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    logger.info(f"✅ Invoice record created with ID: {invoice.id}")
    
    # Process invoice in background
    background_tasks.add_task(process_invoice_background, invoice.id, file_path)
    logger.info(f"🔍 Background processing task added for invoice {invoice.id}")
    
    return invoice

async def process_invoice_background(invoice_id: int, file_path: str):
    """Background task to process invoice using integrated OCR + LLM pipeline"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"🔍 Starting background processing for invoice {invoice_id}")
        logger.info(f"🔍 File path: {file_path}")
        
        # Create new database session for background task
        from app.database import SessionLocal
        db = SessionLocal()
        
        try:
            # Get invoice record
            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                logger.error(f"[ERROR] Invoice {invoice_id} not found in database")
                return
            
            logger.info(f"� Processing invoice {invoice_id}: {invoice.filename}")
            logger.info(f"🔍 Starting OCR + LLM pipeline...")
            
            # Process using integrated service (OCR + LLM)
            result = invoice_processor.process_invoice(file_path)
            
            logger.info(f"🔍 Processing result: {result}")
            
            if not result.get('success', False):
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"[ERROR] Processing failed for invoice {invoice_id}: {error_msg}")
                
                # Update invoice with failed status
                invoice.processing_status = "failed"
                invoice.error_message = error_msg
                db.commit()
                return
            
            logger.info(f"✅ Processing successful for invoice {invoice_id}")
            
            # Extract data from result
            parsed_data = result.get('parsed_data', {})
            items = parsed_data.get('items', [])
            
            logger.info(f"🔍 Found {len(items)} items in invoice")
            logger.info(f"🔍 Vendor: {parsed_data.get('vendor_name', 'Unknown')}")
            logger.info(f"🔍 Total: ${parsed_data.get('total_amount', 0)}")
            logger.info(f"🔍 Parsing method: {parsed_data.get('parsing_method', 'Unknown')}")
            
            # Update invoice with processed data
            invoice.ocr_text = result.get('ocr_result', {}).get('text', '')
            invoice.parsed_data = parsed_data
            invoice.total_amount = parsed_data.get('total_amount')
            invoice.vendor_name = parsed_data.get('vendor_name')
            invoice.processing_status = "completed"
            
            # Parse invoice date if available
            if parsed_data.get('invoice_date'):
                try:
                    # Try ISO format first
                    invoice.invoice_date = datetime.fromisoformat(parsed_data['invoice_date'])
                    logger.info(f"✅ Invoice date parsed: {invoice.invoice_date}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not parse invoice date: {parsed_data.get('invoice_date')}")
                    # Try alternative date formats
                    date_formats = [
                        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
                        "%B %d, %Y", "%b %d, %Y",
                        "%d %B %Y", "%d %b %Y",
                        "%m-%d-%Y", "%d-%m-%Y"
                    ]
                    
                    for fmt in date_formats:
                        try:
                            invoice.invoice_date = datetime.strptime(parsed_data['invoice_date'], fmt)
                            logger.info(f"✅ Invoice date parsed with format {fmt}: {invoice.invoice_date}")
                            break
                        except ValueError:
                            continue
            
            db.commit()
            logger.info(f"✅ Invoice {invoice_id} processing completed and saved to database")
            
        except Exception as e:
            logger.error(f"[ERROR] Error in background processing: {str(e)}")
            # Update invoice with failed status
            if 'invoice' in locals():
                invoice.processing_status = "failed"
                invoice.error_message = str(e)
                db.commit()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"[ERROR] Critical error in background processing: {str(e)}")
        # Fallback logging if database operations fail
        print(f"[ERROR] Critical error processing invoice {invoice_id}: {str(e)}")

@router.get("/", response_model=List[InvoiceResponse])
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of invoices for current user"""
    
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific invoice"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    return invoice

@router.get("/{invoice_id}/analysis", response_model=InvoiceAnalysisResponse)
async def get_invoice_analysis(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive analysis of an invoice"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.processing_status != "completed" or not invoice.parsed_data:
        raise HTTPException(status_code=400, detail="Invoice not yet processed")
    
    # Get extracted items
    extracted_items = invoice.parsed_data.get("items", [])
    
    # Generate carbon analysis
    carbon_analysis = carbon_service.calculate_ingredient_footprint(extracted_items)
    
    # Generate AI recommendations
    ai_recommendations = ai_engine.generate_comprehensive_recommendations(
        extracted_items,
        restaurant_location="general",  # Could be user preference
        current_season=_get_current_season()
    )
    
    # Calculate sustainability score
    sustainability_score = _calculate_sustainability_score(
        carbon_analysis, 
        ai_recommendations, 
        extracted_items
    )
    
    return InvoiceAnalysisResponse(
        invoice=invoice,
        extracted_items=extracted_items,
        carbon_analysis=carbon_analysis,
        ai_recommendations=ai_recommendations,
        sustainability_score=sustainability_score
    )

@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an invoice"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Delete file
    try:
        if os.path.exists(invoice.file_path):
            os.remove(invoice.file_path)
    except Exception as e:
        # Log but don't fail if file deletion fails
        pass
    
    # Delete database record
    db.delete(invoice)
    db.commit()
    
    return {"message": "Invoice deleted successfully"}

@router.post("/{invoice_id}/reprocess")
async def reprocess_invoice(
    invoice_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprocess an invoice with latest algorithms"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Reset processing status
    invoice.processing_status = "pending"
    invoice.parsed_data = None
    db.commit()
    
    # Process in background
    background_tasks.add_task(process_invoice_background, invoice.id, invoice.file_path, db)
    
    return {"message": "Invoice reprocessing started"}

def _get_current_season() -> str:
    """Get current season based on date"""
    month = datetime.now().month
    if month in [12, 1, 2]:
        return "winter"
    elif month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    else:
        return "fall"

def _calculate_sustainability_score(
    carbon_analysis: Dict[str, Any], 
    ai_recommendations: Dict[str, Any], 
    items: List[Dict[str, Any]]
) -> float:
    """Calculate overall sustainability score (0-100)"""
    
    score = 50.0  # Base score
    
    # Factor in carbon intensity
    total_carbon = carbon_analysis.get("total_footprint", 0)
    item_count = len(items)
    
    if item_count > 0:
        avg_carbon_per_item = total_carbon / item_count
        
        # Lower carbon per item = higher score
        if avg_carbon_per_item < 5:
            score += 20
        elif avg_carbon_per_item < 10:
            score += 10
        elif avg_carbon_per_item > 20:
            score -= 20
        elif avg_carbon_per_item > 15:
            score -= 10
    
    # Factor in recommendation potential
    high_impact_recs = len([
        rec for rec in ai_recommendations.get("recommendations", [])
        if rec.get("impact_score", 0) >= 7
    ])
    
    if high_impact_recs == 0:
        score += 15  # Already sustainable
    elif high_impact_recs > 5:
        score -= 15  # Many improvement opportunities
    
    # Factor in seasonal alignment
    seasonal_score = carbon_analysis.get("sustainability_factors", {}).get("seasonal_score", 0.5)
    score += (seasonal_score - 0.5) * 20
    
    return max(0, min(100, score))

@router.get("/service/status")
async def get_service_status():
    """Get status of invoice processing services"""
    return invoice_processor.get_service_status()

@router.post("/test/parse-text")
async def test_parse_text(text_data: Dict[str, str]):
    """
    Test endpoint to parse invoice text directly with LLM
    Useful for testing and debugging the parser
    """
    text = text_data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text field is required")
    
    result = invoice_processor.process_invoice_from_text(text)
    return result

@router.post("/{invoice_id}/reprocess-with-llm")
async def reprocess_invoice_with_llm(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprocess an existing invoice using LLM parser if OCR text is available"""
    
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if not invoice.ocr_text:
        raise HTTPException(
            status_code=400, 
            detail="No OCR text available. Please reprocess the file completely."
        )
    
    try:
        # Reprocess with LLM using existing OCR text
        result = invoice_processor.process_invoice_from_text(invoice.ocr_text)
        
        if not result.get('success', False):
            raise HTTPException(
                status_code=500, 
                detail=f"LLM processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Update invoice with new parsed data
        invoice.parsed_data = {
            'items': result.get('items', []),
            'categorized_items': result.get('categorized_items', {}),
            'processing_method': result.get('processing_method', 'LLM only'),
            'confidence': result.get('confidence', 0.0),
            'processing_time': result.get('processing_time', {}),
            'item_count': result.get('item_count', 0),
            'reprocessed_with_llm': True,
            'reprocessed_at': datetime.utcnow().isoformat()
        }
        
        invoice.total_amount = result.get('total_amount')
        invoice.vendor_name = result.get('vendor_name')
        
        # Parse invoice date if available
        if result.get('invoice_date'):
            try:
                invoice.invoice_date = datetime.fromisoformat(result['invoice_date'])
            except Exception:
                # Try alternative date formats
                date_formats = [
                    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", 
                    "%B %d, %Y", "%b %d, %Y",
                    "%d %B %Y", "%d %b %Y",
                    "%m-%d-%Y", "%d-%m-%Y"
                ]
                for date_format in date_formats:
                    try:
                        invoice.invoice_date = datetime.strptime(
                            result['invoice_date'], date_format
                        )
                        break
                    except:
                        continue
        
        invoice.processing_status = "completed"
        db.commit()
        
        return {
            "success": True,
            "message": "Invoice reprocessed with LLM successfully",
            "item_count": result.get('item_count', 0),
            "vendor_name": result.get('vendor_name'),
            "total_amount": result.get('total_amount'),
            "confidence": result.get('confidence', 0.0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Reprocessing failed: {str(e)}"
        )
