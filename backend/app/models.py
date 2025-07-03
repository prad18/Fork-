from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    restaurant_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    invoices = relationship("Invoice", back_populates="user")
    menus = relationship("Menu", back_populates="user")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    ocr_text = Column(Text)
    parsed_data = Column(JSON)  # Structured ingredient data
    carbon_footprint = Column(JSON)  # Carbon analysis results
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    total_amount = Column(Float)
    vendor_name = Column(String)
    invoice_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="invoices")
    ingredients = relationship("InvoiceIngredient", back_populates="invoice")

class Menu(Base):
    __tablename__ = "menus"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    menu_items = Column(JSON)  # List of menu items with ingredients
    
    # Relationships
    user = relationship("User", back_populates="menus")

class InvoiceIngredient(Base):
    __tablename__ = "invoice_ingredients"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    name = Column(String, nullable=False)
    quantity = Column(Float)
    unit = Column(String)
    price = Column(Float)
    carbon_footprint = Column(Float)  # kg CO2e
    ingredient_category = Column(String)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="ingredients")

class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    scope1_emissions = Column(Float, default=0.0)  # Direct emissions
    scope2_emissions = Column(Float, default=0.0)  # Energy emissions
    scope3_emissions = Column(Float, default=0.0)  # Supply chain emissions
    total_emissions = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class IngredientDatabase(Base):
    __tablename__ = "ingredient_database"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    carbon_intensity = Column(Float, nullable=False)  # kg CO2e per kg
    category = Column(String)
    is_local = Column(Boolean, default=False)
    is_organic = Column(Boolean, default=False)
    seasonal_months = Column(JSON)  # List of months when in season
    alternative_ingredients = Column(JSON)  # List of sustainable alternatives
