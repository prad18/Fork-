from typing import Dict, Any, List, Optional
import json
import re
from dataclasses import dataclass
from enum import Enum

class RecommendationType(Enum):
    SUBSTITUTION = "substitution"
    SOURCING = "sourcing"
    SEASONAL = "seasonal"
    COST_OPTIMIZATION = "cost_optimization"
    CARBON_REDUCTION = "carbon_reduction"

@dataclass
class Recommendation:
    type: RecommendationType
    title: str
    description: str
    current_item: Optional[str]
    suggested_alternative: str
    impact_score: int  # 1-10 scale
    potential_savings: Dict[str, float]  # carbon, cost, etc.
    implementation_difficulty: str  # easy, medium, hard
    seasonal_factor: Optional[str]
    local_availability: bool

class AIRecommendationEngine:
    """
    Phase 2: Advanced AI-powered recommendation system
    Provides intelligent sustainability recommendations based on multiple factors
    """
    
    def __init__(self):
        self.ingredient_database = self._load_ingredient_database()
        self.seasonal_calendar = self._load_seasonal_calendar()
        self.substitution_matrix = self._load_substitution_matrix()
        
    def generate_comprehensive_recommendations(
        self, 
        invoice_items: List[Dict],
        restaurant_location: str = "general",
        current_season: str = "all",
        budget_constraint: Optional[float] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive AI-powered recommendations"""
        
        recommendations = []
        
        # 1. Carbon Reduction Recommendations
        carbon_recs = self._generate_carbon_reduction_recommendations(invoice_items)
        recommendations.extend(carbon_recs)
        
        # 2. Seasonal Optimization Recommendations
        seasonal_recs = self._generate_seasonal_recommendations(invoice_items, current_season)
        recommendations.extend(seasonal_recs)
        
        # 3. Local Sourcing Recommendations
        local_recs = self._generate_local_sourcing_recommendations(invoice_items, restaurant_location)
        recommendations.extend(local_recs)
        
        # 4. Cost Optimization Recommendations
        cost_recs = self._generate_cost_optimization_recommendations(invoice_items, budget_constraint)
        recommendations.extend(cost_recs)
        
        # 5. Nutritional Equivalency Recommendations
        nutrition_recs = self._generate_nutrition_recommendations(invoice_items)
        recommendations.extend(nutrition_recs)
        
        # Sort by impact score
        recommendations.sort(key=lambda x: x.impact_score, reverse=True)
        
        return {
            "recommendations": [self._recommendation_to_dict(rec) for rec in recommendations[:10]],
            "summary": self._generate_recommendation_summary(recommendations),
            "implementation_roadmap": self._generate_implementation_roadmap(recommendations),
            "projected_impact": self._calculate_projected_impact(recommendations)
        }
    
    def _generate_carbon_reduction_recommendations(self, items: List[Dict]) -> List[Recommendation]:
        """Generate recommendations focused on carbon footprint reduction"""
        recommendations = []
        
        for item in items:
            item_name = item.get("name", "").lower()
            carbon_intensity = self._get_carbon_intensity(item_name)
            
            if carbon_intensity > 20:  # High carbon items
                alternatives = self._find_carbon_alternatives(item_name)
                
                for alt in alternatives:
                    potential_reduction = (carbon_intensity - alt["carbon_intensity"]) * float(item.get("quantity", 1))
                    
                    if potential_reduction > 0:
                        recommendations.append(Recommendation(
                            type=RecommendationType.CARBON_REDUCTION,
                            title=f"Reduce carbon footprint: Replace {item.get('name', 'item')}",
                            description=f"Switch from {item.get('name')} to {alt['name']} to reduce emissions by {potential_reduction:.1f} kg CO₂e",
                            current_item=item.get("name"),
                            suggested_alternative=alt["name"],
                            impact_score=min(10, int(potential_reduction / 5)),
                            potential_savings={
                                "carbon_kg": potential_reduction,
                                "carbon_percent": (potential_reduction / (carbon_intensity * float(item.get("quantity", 1)))) * 100
                            },
                            implementation_difficulty=alt.get("difficulty", "medium"),
                            seasonal_factor=None,
                            local_availability=alt.get("local_available", False)
                        ))
        
        return recommendations
    
    def _generate_seasonal_recommendations(self, items: List[Dict], current_season: str) -> List[Recommendation]:
        """Generate recommendations for seasonal optimization"""
        recommendations = []
        
        for item in items:
            item_name = item.get("name", "").lower()
            seasonal_info = self._get_seasonal_info(item_name, current_season)
            
            if not seasonal_info["in_season"]:
                seasonal_alternatives = seasonal_info.get("alternatives", [])
                
                for alt in seasonal_alternatives:
                    carbon_reduction = self._calculate_seasonal_carbon_benefit(item_name, alt)
                    cost_reduction = self._calculate_seasonal_cost_benefit(item_name, alt)
                    
                    recommendations.append(Recommendation(
                        type=RecommendationType.SEASONAL,
                        title=f"Seasonal optimization: {alt}",
                        description=f"Switch to seasonal {alt} instead of out-of-season {item.get('name')}",
                        current_item=item.get("name"),
                        suggested_alternative=alt,
                        impact_score=7,
                        potential_savings={
                            "carbon_kg": carbon_reduction,
                            "cost_percent": cost_reduction
                        },
                        implementation_difficulty="easy",
                        seasonal_factor=current_season,
                        local_availability=True
                    ))
        
        return recommendations
    
    def _generate_local_sourcing_recommendations(self, items: List[Dict], location: str) -> List[Recommendation]:
        """Generate recommendations for local sourcing"""
        recommendations = []
        
        for item in items:
            item_name = item.get("name", "").lower()
            
            if not self._is_likely_local(item_name):
                local_alternatives = self._find_local_alternatives(item_name, location)
                
                for alt in local_alternatives:
                    transportation_reduction = self._calculate_transportation_savings(item_name, alt)
                    
                    recommendations.append(Recommendation(
                        type=RecommendationType.SOURCING,
                        title=f"Source locally: {alt['name']}",
                        description=f"Source {alt['name']} from local suppliers to reduce transportation emissions and support local economy",
                        current_item=item.get("name"),
                        suggested_alternative=alt["name"],
                        impact_score=6,
                        potential_savings={
                            "carbon_kg": transportation_reduction,
                            "local_economy_support": True
                        },
                        implementation_difficulty="medium",
                        seasonal_factor=None,
                        local_availability=True
                    ))
        
        return recommendations
    
    def _generate_cost_optimization_recommendations(self, items: List[Dict], budget: Optional[float]) -> List[Recommendation]:
        """Generate cost-conscious sustainability recommendations"""
        recommendations = []
        
        if not budget:
            return recommendations
        
        for item in items:
            item_name = item.get("name", "").lower()
            item_cost = float(item.get("price", 0))
            
            cost_effective_alternatives = self._find_cost_effective_sustainable_alternatives(item_name, item_cost)
            
            for alt in cost_effective_alternatives:
                cost_savings = item_cost - alt["estimated_cost"]
                carbon_impact = alt["carbon_benefit"]
                
                if cost_savings > 0 and carbon_impact > 0:
                    recommendations.append(Recommendation(
                        type=RecommendationType.COST_OPTIMIZATION,
                        title=f"Cost-effective green choice: {alt['name']}",
                        description=f"Save money while reducing environmental impact",
                        current_item=item.get("name"),
                        suggested_alternative=alt["name"],
                        impact_score=8,
                        potential_savings={
                            "cost_dollar": cost_savings,
                            "carbon_kg": carbon_impact
                        },
                        implementation_difficulty="easy",
                        seasonal_factor=None,
                        local_availability=alt.get("local_available", False)
                    ))
        
        return recommendations
    
    def _generate_nutrition_recommendations(self, items: List[Dict]) -> List[Recommendation]:
        """Generate nutritionally equivalent sustainable alternatives"""
        recommendations = []
        
        # This would integrate with nutrition databases in a full implementation
        nutrition_mapping = {
            "beef": [
                {"name": "lentils", "protein_equivalent": 0.8, "carbon_reduction": 0.9},
                {"name": "mushrooms", "umami_equivalent": 0.9, "carbon_reduction": 0.85},
                {"name": "jackfruit", "texture_equivalent": 0.7, "carbon_reduction": 0.95}
            ],
            "dairy milk": [
                {"name": "oat milk", "nutritional_score": 0.85, "carbon_reduction": 0.7},
                {"name": "pea milk", "protein_equivalent": 0.9, "carbon_reduction": 0.75}
            ]
        }
        
        for item in items:
            item_name = item.get("name", "").lower()
            
            for key, alternatives in nutrition_mapping.items():
                if key in item_name:
                    for alt in alternatives:
                        recommendations.append(Recommendation(
                            type=RecommendationType.SUBSTITUTION,
                            title=f"Nutritional alternative: {alt['name']}",
                            description=f"Maintain nutritional value while reducing environmental impact",
                            current_item=item.get("name"),
                            suggested_alternative=alt["name"],
                            impact_score=7,
                            potential_savings={
                                "carbon_reduction_percent": alt.get("carbon_reduction", 0) * 100,
                                "nutritional_equivalency": alt.get("nutritional_score", alt.get("protein_equivalent", 0.8))
                            },
                            implementation_difficulty="medium",
                            seasonal_factor=None,
                            local_availability=False
                        ))
        
        return recommendations
    
    # Helper methods for data loading and calculations
    def _load_ingredient_database(self) -> Dict:
        """Load comprehensive ingredient database with carbon, nutrition, seasonal data"""
        # In production, this would load from a real database
        return {
            "beef": {"carbon": 60.0, "seasonal": [], "local_regions": []},
            "chicken": {"carbon": 6.9, "seasonal": ["all"], "local_regions": ["most"]},
            "lentils": {"carbon": 0.9, "seasonal": ["fall"], "local_regions": ["many"]},
            # ... more ingredients
        }
    
    def _load_seasonal_calendar(self) -> Dict:
        """Load seasonal availability calendar"""
        return {
            "spring": ["asparagus", "peas", "lettuce", "spinach"],
            "summer": ["tomatoes", "corn", "peppers", "zucchini"],
            "fall": ["squash", "apples", "root vegetables"],
            "winter": ["citrus", "stored grains", "preserved items"]
        }
    
    def _load_substitution_matrix(self) -> Dict:
        """Load ingredient substitution matrix"""
        return {
            "beef": [
                {"name": "chicken", "carbon_factor": 0.12, "cost_factor": 0.7},
                {"name": "lentils", "carbon_factor": 0.015, "cost_factor": 0.3},
                {"name": "mushrooms", "carbon_factor": 0.05, "cost_factor": 0.8}
            ]
        }
    
    def _recommendation_to_dict(self, rec: Recommendation) -> Dict:
        """Convert recommendation object to dictionary"""
        return {
            "type": rec.type.value,
            "title": rec.title,
            "description": rec.description,
            "current_item": rec.current_item,
            "suggested_alternative": rec.suggested_alternative,
            "impact_score": rec.impact_score,
            "potential_savings": rec.potential_savings,
            "implementation_difficulty": rec.implementation_difficulty,
            "seasonal_factor": rec.seasonal_factor,
            "local_availability": rec.local_availability
        }
    
    def _generate_recommendation_summary(self, recommendations: List[Recommendation]) -> Dict:
        """Generate summary of recommendations"""
        return {
            "total_recommendations": len(recommendations),
            "high_impact": len([r for r in recommendations if r.impact_score >= 8]),
            "easy_implementation": len([r for r in recommendations if r.implementation_difficulty == "easy"]),
            "seasonal_optimizations": len([r for r in recommendations if r.type == RecommendationType.SEASONAL])
        }
    
    def _generate_implementation_roadmap(self, recommendations: List[Recommendation]) -> List[Dict]:
        """Generate phased implementation roadmap"""
        phases = {
            "immediate": [r for r in recommendations if r.implementation_difficulty == "easy"],
            "short_term": [r for r in recommendations if r.implementation_difficulty == "medium"],
            "long_term": [r for r in recommendations if r.implementation_difficulty == "hard"]
        }
        
        return [
            {
                "phase": phase,
                "timeline": {"immediate": "1-2 weeks", "short_term": "1-3 months", "long_term": "3-12 months"}[phase],
                "recommendations": len(recs),
                "estimated_impact": sum(r.impact_score for r in recs)
            }
            for phase, recs in phases.items() if recs
        ]
    
    def _calculate_projected_impact(self, recommendations: List[Recommendation]) -> Dict:
        """Calculate total projected impact if all recommendations implemented"""
        total_carbon_savings = sum(
            rec.potential_savings.get("carbon_kg", 0) 
            for rec in recommendations
        )
        
        return {
            "total_carbon_reduction_kg": total_carbon_savings,
            "sustainability_score_improvement": min(25, len(recommendations) * 2),
            "estimated_cost_impact": "neutral_to_positive"
        }
    
    # Placeholder methods for complex calculations
    def _get_carbon_intensity(self, item_name: str) -> float:
        # Simplified - in production would use comprehensive database
        high_carbon = ["beef", "lamb", "cheese"]
        if any(item in item_name for item in high_carbon):
            return 40.0
        return 5.0
    
    def _find_carbon_alternatives(self, item_name: str) -> List[Dict]:
        # Simplified alternatives mapping
        alternatives = {
            "beef": [{"name": "chicken", "carbon_intensity": 6.9, "difficulty": "easy"}],
            "lamb": [{"name": "pork", "carbon_intensity": 12.1, "difficulty": "easy"}]
        }
        return alternatives.get(item_name, [])
    
    def _get_seasonal_info(self, item_name: str, season: str) -> Dict:
        # Simplified seasonal info
        return {"in_season": True, "alternatives": []}
    
    def _calculate_seasonal_carbon_benefit(self, current: str, alternative: str) -> float:
        return 2.5  # Simplified
    
    def _calculate_seasonal_cost_benefit(self, current: str, alternative: str) -> float:
        return 15.0  # 15% cost reduction
    
    def _is_likely_local(self, item_name: str) -> bool:
        return "local" in item_name
    
    def _find_local_alternatives(self, item_name: str, location: str) -> List[Dict]:
        return [{"name": f"local {item_name}"}]
    
    def _calculate_transportation_savings(self, current: str, alternative: Dict) -> float:
        return 1.2  # kg CO2e reduction
    
    def _find_cost_effective_sustainable_alternatives(self, item_name: str, current_cost: float) -> List[Dict]:
        return [{"name": "alternative", "estimated_cost": current_cost * 0.9, "carbon_benefit": 2.0}]
