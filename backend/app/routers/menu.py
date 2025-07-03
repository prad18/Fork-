from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any

from app.database import get_db
from app.models import Menu, User
from app.dependencies import get_current_user

router = APIRouter()

class MenuCreate(BaseModel):
    name: str
    description: str = ""
    menu_items: List[Dict[str, Any]]

class MenuResponse(BaseModel):
    id: int
    name: str
    description: str
    menu_items: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=MenuResponse)
async def create_menu(
    menu_data: MenuCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new menu"""
    menu = Menu(
        user_id=current_user.id,
        name=menu_data.name,
        description=menu_data.description,
        menu_items=menu_data.menu_items
    )
    
    db.add(menu)
    db.commit()
    db.refresh(menu)
    
    return menu

@router.get("/", response_model=List[MenuResponse])
async def get_menus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all menus for the current user"""
    menus = db.query(Menu).filter(Menu.user_id == current_user.id).all()
    return menus

@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific menu"""
    menu = db.query(Menu).filter(
        Menu.id == menu_id,
        Menu.user_id == current_user.id
    ).first()
    
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    
    return menu
