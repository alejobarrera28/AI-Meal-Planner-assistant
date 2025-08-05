"""
User history and preference tools
"""

from typing import Dict, Any
from .base import BaseTool, ToolUtils


class GetUserHistoryTool(BaseTool):
    """Get user's meal history and preferences"""
    
    def execute(self, user_id: int) -> Dict[str, Any]:
        # Get user's course interactions
        user_courses = [course_idx for uid, course_idx in self.meal_db.user_course_interactions if uid == user_id]
        
        # Get user's meal interactions
        user_meals = []
        for split in ["train", "test", "tune"]:
            user_meals.extend([meal_idx for uid, meal_idx in self.meal_db.user_meal_interactions.get(split, []) if uid == user_id])
        
        if not user_courses and not user_meals:
            return {"error": f"No history found for user {user_id}"}
        
        # Analyze preferences
        category_counts = {0: 0, 1: 0, 2: 0}  # appetizer, main, dessert
        health_scores = []
        
        for course_idx in user_courses:
            if course_idx in self.meal_db.recipes_db:
                recipe = self.meal_db.recipes_db[course_idx]
                category_counts[recipe.category] += 1
                health_scores.append(recipe.fsa_health_score)
        
        # Calculate preferences
        total_courses = sum(category_counts.values())
        category_preferences = {}
        if total_courses > 0:
            category_preferences = {
                "appetizer": round(category_counts[0] / total_courses * 100, 1),
                "main": round(category_counts[1] / total_courses * 100, 1), 
                "dessert": round(category_counts[2] / total_courses * 100, 1)
            }
        
        avg_health_score = sum(health_scores) / len(health_scores) if health_scores else 0
        
        return {
            "user_id": user_id,
            "total_courses": len(user_courses),
            "total_meals": len(user_meals),
            "category_preferences": category_preferences,
            "average_health_score": round(avg_health_score, 2),
            "health_preference": ToolUtils.get_health_rating(avg_health_score),
            "most_preferred_category": max(category_preferences.keys(), key=category_preferences.get) if category_preferences else None
        }