"""
Meal planning and composition tools
"""

from typing import Dict, List, Any
from .base import BaseTool, ToolUtils


class GenerateMealPlanTool(BaseTool):
    """Generate a complete meal plan (appetizer, main, dessert) based on dietary goals"""
    
    def execute(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        health_focus = goal.get("health_focus", "balanced")
        max_avg_health_score = goal.get("max_avg_health_score")
        include_categories = goal.get("include_categories", ["appetizer", "main", "dessert"])
        
        # Set health score thresholds based on focus
        health_thresholds = {
            "weight_loss": 5.0,
            "heart_healthy": 6.0, 
            "balanced": 8.0,
            "low_sodium": 7.0
        }
        
        max_score = max_avg_health_score or health_thresholds.get(health_focus, 8.0)
        
        meal_plan = {}
        
        for category in include_categories:
            category_idx = {"appetizer": 0, "main": 1, "dessert": 2}.get(category)
            if category_idx is None:
                continue
                
            # Find best course in category
            best_courses = []
            for course_idx, recipe in self.rag_db.recipes_db.items():
                if recipe.category == category_idx and recipe.fsa_health_score <= max_score:
                    best_courses.append((course_idx, recipe))
            
            if best_courses:
                # Sort by health score and pick best
                best_courses.sort(key=lambda x: x[1].fsa_health_score + x[1].who_health_score)
                course_idx, recipe = best_courses[0]
                
                meal_plan[category] = {
                    "course_id": ToolUtils.get_real_course_id(self.rag_db, course_idx),
                    "course_name": recipe.course_name,
                    "fsa_score": recipe.fsa_health_score,
                    "who_score": recipe.who_health_score,
                    "category": category
                }
        
        # Calculate overall health score
        if meal_plan:
            avg_fsa = sum(course["fsa_score"] for course in meal_plan.values()) / len(meal_plan)
            avg_who = sum(course["who_score"] for course in meal_plan.values()) / len(meal_plan)
        else:
            avg_fsa = avg_who = 0
            
        return {
            "meal_plan": meal_plan,
            "goal": goal,
            "average_fsa_score": round(avg_fsa, 2),
            "average_who_score": round(avg_who, 2),
            "health_focus": health_focus,
            "courses_included": len(meal_plan)
        }


class GetMealCompositionTool(BaseTool):
    """Get all courses that make up a specific meal"""
    
    def execute(self, meal_id: int) -> Dict[str, Any]:
        if meal_id not in self.rag_db.meal_course_mapping:
            return {"error": f"Meal {meal_id} not found"}
        
        course_indices = self.rag_db.meal_course_mapping[meal_id]
        courses = []
        total_fsa = 0
        total_who = 0
        
        for course_idx in course_indices:
            if course_idx in self.rag_db.recipes_db:
                recipe = self.rag_db.recipes_db[course_idx]
                courses.append({
                    "course_id": ToolUtils.get_real_course_id(self.rag_db, course_idx),
                    "course_name": recipe.course_name,
                    "category": ["appetizer", "main", "dessert"][recipe.category],
                    "fsa_score": recipe.fsa_health_score,
                    "who_score": recipe.who_health_score
                })
                total_fsa += recipe.fsa_health_score
                total_who += recipe.who_health_score
        
        avg_fsa = total_fsa / len(courses) if courses else 0
        avg_who = total_who / len(courses) if courses else 0
        
        return {
            "meal_id": meal_id,
            "courses": courses,
            "course_count": len(courses),
            "average_scores": {
                "fsa": round(avg_fsa, 2),
                "who": round(avg_who, 2),
                "combined": round((avg_fsa + avg_who) / 2, 2)
            },
            "health_rating": ToolUtils.get_health_rating(avg_fsa)
        }