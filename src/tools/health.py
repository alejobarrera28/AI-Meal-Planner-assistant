"""
Health scoring and optimization tools
"""

from typing import Dict, Any
from .base import BaseTool, ToolUtils


class CalculateHealthScoreTool(BaseTool):
    """Calculate health score for a course or meal"""
    
    def execute(self, item_id: int, score_type: str, item_type: str = "course") -> Dict[str, Any]:
        if item_type == "course":
            if item_id not in self.meal_db.recipes_db:
                return {"error": f"Course {item_id} not found"}
                
            recipe = self.meal_db.recipes_db[item_id]
            
            if score_type == "fsa":
                score = recipe.fsa_health_score
            elif score_type == "who": 
                score = recipe.who_health_score
            elif score_type == "combined":
                score = (recipe.fsa_health_score + recipe.who_health_score) / 2
            else:
                return {"error": f"Unknown score type: {score_type}"}
                
            return {
                "item_id": item_id,
                "item_type": "course",
                "score_type": score_type,
                "score": score,
                "health_rating": ToolUtils.get_health_rating(score),
                "course_name": recipe.course_name,
                "category": ["appetizer", "main", "dessert"][recipe.category]
            }
            
        elif item_type == "meal":
            if item_id not in self.meal_db.meal_course_mapping:
                return {"error": f"Meal {item_id} not found"}
                
            course_indices = self.meal_db.meal_course_mapping[item_id]
            scores = []
            
            for course_idx in course_indices:
                if course_idx in self.meal_db.recipes_db:
                    recipe = self.meal_db.recipes_db[course_idx]
                    if score_type == "fsa":
                        scores.append(recipe.fsa_health_score)
                    elif score_type == "who":
                        scores.append(recipe.who_health_score)
                    elif score_type == "combined":
                        scores.append((recipe.fsa_health_score + recipe.who_health_score) / 2)
            
            if not scores:
                return {"error": f"No valid courses found for meal {item_id}"}
                
            avg_score = sum(scores) / len(scores)
            
            return {
                "item_id": item_id,
                "item_type": "meal", 
                "score_type": score_type,
                "score": round(avg_score, 2),
                "health_rating": ToolUtils.get_health_rating(avg_score),
                "course_count": len(scores),
                "individual_scores": scores
            }


class SwapForHealthierTool(BaseTool):
    """Find a healthier alternative to a given course in the same category"""
    
    def execute(self, course_id: int, improvement_threshold: float = 1.0) -> Dict[str, Any]:
        # Convert real course ID to course index if needed
        course_idx = ToolUtils.convert_course_id_to_index(self.meal_db, course_id)
        
        if course_idx not in self.meal_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
            
        original_recipe = self.meal_db.recipes_db[course_idx]
        original_score = original_recipe.fsa_health_score
        target_category = original_recipe.category
        
        # Find alternatives in same category
        alternatives = []
        for other_id, recipe in self.meal_db.recipes_db.items():
            if (recipe.category == target_category and 
                other_id != course_idx and
                recipe.fsa_health_score < (original_score - improvement_threshold)):
                
                improvement = original_score - recipe.fsa_health_score
                alternatives.append((other_id, recipe, improvement))
        
        if not alternatives:
            return {
                "original_course": {
                    "course_id": ToolUtils.get_real_course_id(self.meal_db, course_idx),
                    "course_name": original_recipe.course_name,
                    "fsa_score": original_score
                },
                "message": f"No healthier alternatives found with improvement >= {improvement_threshold}",
                "alternatives_checked": sum(1 for _, recipe in self.meal_db.recipes_db.items() if recipe.category == target_category) - 1
            }
        
        # Sort by improvement (best first)
        alternatives.sort(key=lambda x: x[2], reverse=True)
        best_id, best_recipe, improvement = alternatives[0]
        
        return {
            "original_course": {
                "course_id": ToolUtils.get_real_course_id(self.meal_db, course_idx),
                "course_name": original_recipe.course_name,
                "fsa_score": original_score,
                "who_score": original_recipe.who_health_score
            },
            "healthier_alternative": {
                "course_id": ToolUtils.get_real_course_id(self.meal_db, best_id),
                "course_name": best_recipe.course_name,
                "fsa_score": best_recipe.fsa_health_score,
                "who_score": best_recipe.who_health_score
            },
            "improvement": {
                "fsa_improvement": round(improvement, 2),
                "who_improvement": round(original_recipe.who_health_score - best_recipe.who_health_score, 2)
            },
            "category": ["appetizer", "main", "dessert"][target_category],
            "total_alternatives": len(alternatives)
        }