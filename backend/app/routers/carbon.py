from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models import CarbonFootprint, User, Invoice
from app.dependencies import get_current_user
from app.services.carbon_service import CarbonService

router = APIRouter()

class CarbonFootprintResponse(BaseModel):
    id: int
    period_start: datetime
    period_end: datetime
    scope1_emissions: float
    scope2_emissions: float
    scope3_emissions: float
    total_emissions: float
    
    class Config:
        from_attributes = True

# Initialize carbon calculator service
carbon_service = CarbonService()

@router.get("/footprint")
async def get_carbon_footprint(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get carbon footprint for the specified period"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    # Check if we have a calculated footprint for this period
    existing_footprint = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == current_user.id,
        CarbonFootprint.period_start >= start_date,
        CarbonFootprint.period_end <= end_date
    ).first()
    
    if existing_footprint:
        return existing_footprint
    
    # Calculate new footprint
    footprint_data = await carbon_service.calculate_footprint(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    
    # Save to database
    carbon_footprint = CarbonFootprint(
        user_id=current_user.id,
        period_start=start_date,
        period_end=end_date,
        scope1_emissions=footprint_data["scope1_emissions"],
        scope2_emissions=footprint_data["scope2_emissions"],
        scope3_emissions=footprint_data["scope3_emissions"],
        total_emissions=footprint_data["total_emissions"]
    )
    
    db.add(carbon_footprint)
    db.commit()
    db.refresh(carbon_footprint)
    
    return carbon_footprint

@router.get("/history")
async def get_carbon_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical carbon footprint data"""
    
    footprints = db.query(CarbonFootprint).filter(
        CarbonFootprint.user_id == current_user.id
    ).order_by(CarbonFootprint.period_start.desc()).all()
    
    return footprints

@router.get("/breakdown")
async def get_emissions_breakdown(
    period_days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed breakdown of emissions by category"""
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=period_days)
    
    breakdown = await carbon_service.get_emissions_breakdown(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )
    
    return breakdown

@router.get("/invoice/{invoice_id}")
async def get_invoice_carbon_footprint(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get carbon footprint analysis for a specific invoice"""
    
    # Get the invoice
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == current_user.id
    ).first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    # Return stored carbon footprint if available
    if invoice.carbon_footprint:
        return {
            "invoice_id": invoice.id,
            "filename": invoice.filename,
            "vendor_name": invoice.vendor_name,
            "total_amount": invoice.total_amount,
            "carbon_analysis": invoice.carbon_footprint
        }
    
    # Calculate carbon footprint if not already calculated
    if invoice.parsed_data and "items" in invoice.parsed_data:
        carbon_data = await carbon_service.calculate_footprint(invoice.parsed_data["items"])
        
        # Store the result
        invoice.carbon_footprint = carbon_data
        db.commit()
        
        return {
            "invoice_id": invoice.id,
            "filename": invoice.filename,
            "vendor_name": invoice.vendor_name,
            "total_amount": invoice.total_amount,
            "carbon_analysis": carbon_data
        }
    
    raise HTTPException(
        status_code=400, 
        detail="Invoice has not been processed or contains no items"
    )

@router.get("/dashboard")
async def get_carbon_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get carbon footprint dashboard data"""
    
    # Get all completed invoices with carbon data
    invoices = db.query(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.processing_status == "completed",
        Invoice.parsed_data.isnot(None)
    ).all()
    
    if not invoices:
        return {
            "total_emissions": 0,
            "total_invoices": 0,
            "sustainability_score": 0,
            "emissions_by_category": {},
            "recent_invoices": [],
            "recommendations": []
        }

    # Aggregate carbon data
    total_emissions = 0
    emissions_by_category = {}
    all_recommendations = []
    recent_invoices = []
    
    for invoice in invoices[-10:]:  # Last 10 invoices
        if invoice.parsed_data and invoice.parsed_data.get("items"):
            # Calculate carbon footprint for this invoice
            items = invoice.parsed_data.get("items", [])
            carbon_analysis = await carbon_service.calculate_footprint(items)
            
            invoice_emissions = carbon_analysis.get("total_footprint", 0)
            total_emissions += invoice_emissions
            
            # Aggregate by category
            for category, emissions in carbon_analysis.get("emissions_breakdown", {}).items():
                emissions_by_category[category] = emissions_by_category.get(category, 0) + emissions
            
            # Recent invoice data
            recent_invoices.append({
                "id": invoice.id,
                "filename": invoice.filename,
                "vendor_name": invoice.vendor_name or "Unknown Vendor",
                "total_emissions": round(invoice_emissions, 2),
                "sustainability_score": carbon_analysis.get("sustainability_score", 0),
                "upload_date": invoice.upload_date.isoformat() if invoice.upload_date else None
            })
    
    # Calculate average sustainability score
    avg_sustainability_score = 50  # Default score if no data
    if recent_invoices:
        scores = [inv["sustainability_score"] for inv in recent_invoices if inv["sustainability_score"] > 0]
        avg_sustainability_score = sum(scores) / len(scores) if scores else 50

    return {
        "total_emissions": round(total_emissions, 2),
        "total_invoices": len(invoices),
        "sustainability_score": round(avg_sustainability_score),
        "emissions_by_category": emissions_by_category,
        "recent_invoices": recent_invoices,
        "recommendations": []  # Could add general recommendations here
    }
