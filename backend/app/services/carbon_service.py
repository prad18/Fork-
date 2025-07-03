from typing import Dict, Any, List
import re

class CarbonService:
    def __init__(self):
        # Enhanced carbon intensity database (kg CO2e per kg)
        self.carbon_intensities = {
            # Proteins
            "beef": 60.0, "ground beef": 60.0, "steak": 60.0,
            "lamb": 39.2, "mutton": 39.2,
            "pork": 12.1, "bacon": 12.1, "ham": 12.1,
            "chicken": 6.9, "turkey": 10.9,
            "fish": 6.1, "salmon": 11.9, "tuna": 6.1, "cod": 2.9,
            "shrimp": 11.8, "lobster": 22.0,
            
            # Dairy
            "cheese": 13.5, "butter": 23.8, "cream": 8.0,
            "milk": 3.2, "yogurt": 2.2,
            "eggs": 4.2,
            
            # Grains & Starches
            "rice": 4.0, "wheat": 1.4, "flour": 1.4,
            "pasta": 1.4, "bread": 1.3,
            "potato": 0.3, "sweet potato": 0.3,
            
            # Vegetables (Local vs Imported)
            "tomato": 2.3, "local tomato": 0.7,
            "onion": 0.3, "local onion": 0.1,
            "lettuce": 3.5, "local lettuce": 0.8,
            "spinach": 2.0, "local spinach": 0.5,
            "carrot": 0.4, "local carrot": 0.1,
            "bell pepper": 3.0, "local bell pepper": 0.7,
            
            # Fruits
            "apple": 0.4, "local apple": 0.1,
            "banana": 0.7, "orange": 0.4,
            "lemon": 0.6, "lime": 0.6,
            
            # Oils & Condiments
            "olive oil": 5.4, "vegetable oil": 3.2,
            "vinegar": 0.9, "salt": 0.1,
            "sugar": 1.8,
            
            # Herbs & Spices
            "basil": 2.1, "oregano": 2.0, "thyme": 2.0,
            "black pepper": 7.0, "garlic": 0.4,
            
            # Default categories
            "organic": 0.8,  # 20% reduction for organic
            "local": 0.3,    # 70% reduction for local
            "imported": 2.5,  # Higher footprint for imported
            "default": 2.0
        }

    async def calculate_footprint(self, items: List[Dict]) -> Dict[str, Any]:
        """Calculate carbon footprint for a list of invoice items"""
        
        total_emissions = 0.0
        item_emissions = []
        emissions_by_category = {}
        
        for item in items:
            emission_data = await self._calculate_item_emissions(item)
            total_emissions += emission_data["total_co2"]
            item_emissions.append(emission_data)
            
            # Group by category
            category = emission_data["category"]
            if category not in emissions_by_category:
                emissions_by_category[category] = 0.0
            emissions_by_category[category] += emission_data["total_co2"]
        
        # Calculate sustainability metrics
        sustainability_score = self._calculate_sustainability_score(item_emissions)
        
        return {
            "total_emissions_kg": round(total_emissions, 2),
            "emissions_by_item": item_emissions,
            "emissions_by_category": emissions_by_category,
            "sustainability_score": sustainability_score,
            "recommendations": self._generate_recommendations(item_emissions),
            "summary": {
                "total_items": len(items),
                "high_impact_items": len([i for i in item_emissions if i["impact_level"] == "high"]),
                "average_per_item": round(total_emissions / len(items) if items else 0, 2)
            }
        }
    
    async def _calculate_item_emissions(self, item: Dict) -> Dict[str, Any]:
        """Calculate emissions for a single item"""
        
        name = item.get("name", "").lower()
        quantity = self._extract_quantity(item.get("quantity", "1"))
        price = item.get("price", 0)
        
        # Find matching carbon intensity
        carbon_intensity = self._find_carbon_intensity(name)
        
        # Calculate total CO2
        total_co2 = quantity * carbon_intensity
        
        # Determine impact level
        impact_level = self._get_impact_level(carbon_intensity)
        
        # Categorize item
        category = self._categorize_item(name)
        
        return {
            "name": item.get("name", "Unknown"),
            "quantity": quantity,
            "carbon_intensity": carbon_intensity,
            "total_co2": round(total_co2, 2),
            "impact_level": impact_level,
            "category": category,
            "price": price,
            "co2_per_dollar": round(total_co2 / price if price > 0 else 0, 2),
            "is_local": "local" in name,
            "is_organic": "organic" in name
        }
    
    def _extract_quantity(self, quantity_str: str) -> float:
        """Extract numeric quantity from string like '5 lbs', '2.5 kg', etc."""
        try:
            # Extract first number from string
            numbers = re.findall(r'\d+\.?\d*', str(quantity_str))
            if numbers:
                return float(numbers[0])
            return 1.0
        except:
            return 1.0
    
    def _find_carbon_intensity(self, item_name: str) -> float:
        """Find carbon intensity for an item"""
        item_name = item_name.lower().strip()
        
        # Direct match
        if item_name in self.carbon_intensities:
            return self.carbon_intensities[item_name]
        
        # Partial match
        for key, value in self.carbon_intensities.items():
            if key in item_name or item_name in key:
                modifier = 1.0
                # Apply modifiers
                if "local" in item_name:
                    modifier *= 0.3
                elif "organic" in item_name:
                    modifier *= 0.8
                elif "imported" in item_name:
                    modifier *= 1.5
                return value * modifier
        
        # Category-based fallback
        if any(protein in item_name for protein in ["beef", "meat", "steak"]):
            return self.carbon_intensities["beef"]
        elif any(poultry in item_name for poultry in ["chicken", "poultry"]):
            return self.carbon_intensities["chicken"]
        elif any(dairy in item_name for dairy in ["milk", "cream", "dairy"]):
            return self.carbon_intensities["milk"]
        elif any(veg in item_name for veg in ["vegetable", "lettuce", "green"]):
            return 1.0
        
        return self.carbon_intensities["default"]
    
    def _get_impact_level(self, carbon_intensity: float) -> str:
        """Determine impact level based on carbon intensity"""
        if carbon_intensity > 20:
            return "high"
        elif carbon_intensity > 5:
            return "medium"
        else:
            return "low"
    
    def _categorize_item(self, item_name: str) -> str:
        """Categorize item for analysis"""
        item_name = item_name.lower()
        
        if any(protein in item_name for protein in ["beef", "pork", "chicken", "fish", "meat"]):
            return "protein"
        elif any(dairy in item_name for dairy in ["milk", "cheese", "butter", "cream"]):
            return "dairy"
        elif any(veg in item_name for veg in ["tomato", "lettuce", "onion", "carrot", "vegetable"]):
            return "vegetables"
        elif any(grain in item_name for grain in ["rice", "wheat", "bread", "pasta"]):
            return "grains"
        elif any(fruit in item_name for fruit in ["apple", "orange", "banana", "fruit"]):
            return "fruits"
        else:
            return "other"
    
    def _calculate_sustainability_score(self, item_emissions: List[Dict]) -> int:
        """Calculate sustainability score (0-100)"""
        if not item_emissions:
            return 50
        
        total_score = 0
        for item in item_emissions:
            # Base score from carbon intensity
            if item["impact_level"] == "low":
                score = 80
            elif item["impact_level"] == "medium":
                score = 50
            else:
                score = 20
            
            # Bonus for local/organic
            if item["is_local"]:
                score += 15
            if item["is_organic"]:
                score += 10
            
            total_score += min(score, 100)
        
        return min(int(total_score / len(item_emissions)), 100)
    
    def _generate_recommendations(self, item_emissions: List[Dict]) -> List[Dict]:
        """Generate sustainability recommendations"""
        recommendations = []
        
        # Find high-impact items
        high_impact = [item for item in item_emissions if item["impact_level"] == "high"]
        
        for item in high_impact[:3]:  # Top 3 high-impact items
            recommendations.append({
                "type": "substitution",
                "current_item": item["name"],
                "recommendation": self._get_substitution_suggestion(item),
                "potential_reduction": f"{item['total_co2'] * 0.6:.1f} kg CO2e",
                "priority": "high"
            })
        
        # General recommendations
        if any(not item["is_local"] for item in item_emissions):
            recommendations.append({
                "type": "sourcing",
                "recommendation": "Consider sourcing more ingredients locally to reduce transportation emissions",
                "potential_reduction": "20-50% reduction in transportation emissions",
                "priority": "medium"
            })
        
        return recommendations
    
    def _get_substitution_suggestion(self, item: Dict) -> str:
        """Get substitution suggestion for high-impact item"""
        category = item["category"]
        
        if category == "protein":
            if "beef" in item["name"].lower():
                return "Consider chicken, turkey, or plant-based alternatives"
            elif "lamb" in item["name"].lower():
                return "Consider chicken, pork, or plant-based alternatives"
        elif category == "dairy":
            return "Consider plant-based alternatives or reduced quantities"
        elif category == "vegetables":
            return "Consider local or seasonal alternatives"
        
        return "Consider local, organic, or seasonal alternatives"
