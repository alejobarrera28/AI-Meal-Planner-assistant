"""
Recipe analysis and recommendation tools
"""

from typing import Dict, Any
from .base import BaseTool, ToolUtils


class SummarizeRecipeTool(BaseTool):
    """Generate a natural language summary of a course/recipe"""
    
    def execute(self, course_id: int) -> Dict[str, Any]:
        # Convert real course ID to course index if needed
        course_idx = ToolUtils.convert_course_id_to_index(self.meal_db, course_id)
        
        if course_idx not in self.meal_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
            
        recipe = self.meal_db.recipes_db[course_idx]
        category_name = ["appetizer", "main course", "dessert"][recipe.category]
        
        # Health rating
        health_rating = ToolUtils.get_health_rating(recipe.fsa_health_score)
        
        # Meal usage
        meal_count = len(recipe.meal_affiliations)
        popularity = "very popular" if meal_count > 10 else "popular" if meal_count > 5 else "moderate"
        
        # Generate summary
        summary = f"{recipe.course_name} is a {health_rating} {category_name} "
        summary += f"with an FSA health score of {recipe.fsa_health_score} and WHO score of {recipe.who_health_score}. "
        summary += f"This {popularity} recipe appears in {meal_count} different meal combinations in our dataset."
        
        if recipe.fsa_health_score <= 5:
            summary += " This is an excellent choice for health-conscious diners."
        elif recipe.fsa_health_score <= 7:
            summary += " This offers a good balance of taste and nutrition."
        else:
            summary += " Consider this as an occasional treat rather than a regular choice."
            
        return {
            "course_id": ToolUtils.get_real_course_id(self.meal_db, course_idx),
            "course_name": recipe.course_name,
            "summary": summary,
            "category": category_name,
            "health_rating": health_rating,
            "meal_appearances": meal_count,
            "scores": {
                "fsa": recipe.fsa_health_score,
                "who": recipe.who_health_score
            }
        }


class RecommendSimilarMealsTool(BaseTool):
    """Find meals containing similar courses to a given course"""
    
    def execute(self, course_id: int, limit: int = 5) -> Dict[str, Any]:
        # Convert real course ID to course index if needed
        course_idx = ToolUtils.convert_course_id_to_index(self.meal_db, course_id)
        
        if course_idx not in self.meal_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
        
        reference_recipe = self.meal_db.recipes_db[course_idx]
        reference_category = reference_recipe.category
        
        # Find meals containing the reference course
        meals_with_course = reference_recipe.meal_affiliations
        
        # Find similar meals (same category courses)
        similar_meals = []
        for meal_id, course_indices in self.meal_db.meal_course_mapping.items():
            if meal_id in meals_with_course:
                continue  # Skip meals that already contain this course
                
            # Check if meal has courses in same category
            has_similar_category = any(
                self.meal_db.recipes_db.get(idx, {}).category == reference_category 
                for idx in course_indices
                if idx in self.meal_db.recipes_db
            )
            
            if has_similar_category:
                # Calculate meal health score
                meal_scores = [
                    self.meal_db.recipes_db[idx].fsa_health_score 
                    for idx in course_indices 
                    if idx in self.meal_db.recipes_db
                ]
                avg_score = sum(meal_scores) / len(meal_scores) if meal_scores else 10
                
                similar_meals.append({
                    "meal_id": meal_id,
                    "course_count": len(course_indices),
                    "average_health_score": round(avg_score, 2),
                    "courses": [
                        {
                            "course_id": ToolUtils.get_real_course_id(self.meal_db, idx),
                            "course_name": self.meal_db.recipes_db[idx].course_name,
                            "category": ["appetizer", "main", "dessert"][self.meal_db.recipes_db[idx].category]
                        }
                        for idx in course_indices
                        if idx in self.meal_db.recipes_db
                    ]
                })
        
        # Sort by health score (healthiest first)
        similar_meals.sort(key=lambda x: x["average_health_score"])
        
        return {
            "reference_course": {
                "course_id": ToolUtils.get_real_course_id(self.meal_db, course_idx),
                "course_name": reference_recipe.course_name,
                "category": ["appetizer", "main", "dessert"][reference_category]
            },
            "similar_meals": similar_meals[:limit],
            "total_found": len(similar_meals),
            "meals_with_reference_course": len(meals_with_course)
        }