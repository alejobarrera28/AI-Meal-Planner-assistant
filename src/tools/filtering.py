"""
Course filtering and search tools
"""

from typing import Dict, List, Any, Optional
from .base import BaseTool, ToolUtils


class FilterCoursesTool(BaseTool):
    """Filter courses based on category, health scores, or other criteria"""
    
    def execute(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        # Parse criteria
        category = criteria.get("category")
        max_fsa_score = criteria.get("max_fsa_score")
        max_who_score = criteria.get("max_who_score")
        limit = criteria.get("limit", 10)
        
        # Convert category name to index
        category_map = {"appetizer": 0, "main": 1, "dessert": 2}
        category_filter = category_map.get(category) if category else None
        
        matching_courses = []
        
        for course_idx, recipe in self.rag_db.recipes_db.items():
            # Apply filters
            if category_filter is not None and recipe.category != category_filter:
                continue
            if max_fsa_score is not None and recipe.fsa_health_score > max_fsa_score:
                continue  
            if max_who_score is not None and recipe.who_health_score > max_who_score:
                continue
                
            matching_courses.append({
                "course_id": ToolUtils.get_real_course_id(self.rag_db, course_idx),
                "course_name": recipe.course_name,
                "category": ["appetizer", "main", "dessert"][recipe.category],
                "fsa_score": recipe.fsa_health_score,
                "who_score": recipe.who_health_score,
                "meal_count": len(recipe.meal_affiliations)
            })
        
        # Sort by health score (lower is better)
        matching_courses.sort(key=lambda x: x["fsa_score"] + x["who_score"])
        
        return {
            "courses": matching_courses[:limit],
            "total_found": len(matching_courses),
            "criteria_applied": criteria
        }


class SearchCoursesByCategoryTool(BaseTool):
    """Search for courses in a specific category"""
    
    def execute(self, category: str, limit: int = 10) -> Dict[str, Any]:
        category_map = {"appetizer": 0, "main": 1, "dessert": 2}
        category_idx = category_map.get(category)
        
        if category_idx is None:
            return {"error": f"Invalid category: {category}. Use appetizer, main, or dessert"}
        
        courses = []
        for course_idx, recipe in self.rag_db.recipes_db.items():
            if recipe.category == category_idx:
                courses.append({
                    "course_id": ToolUtils.get_real_course_id(self.rag_db, course_idx),
                    "course_name": recipe.course_name,
                    "fsa_score": recipe.fsa_health_score,
                    "who_score": recipe.who_health_score,
                    "meal_count": len(recipe.meal_affiliations)
                })
        
        # Sort by health score (healthiest first)
        courses.sort(key=lambda x: x["fsa_score"] + x["who_score"])
        
        return {
            "category": category,
            "courses": courses[:limit],
            "total_available": len(courses),
            "showing": min(limit, len(courses))
        }


class FindHealthyCoursesTool(BaseTool):
    """Find the healthiest courses with optional category filter"""
    
    def execute(self, max_fsa_score: float, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        category_filter = None
        if category:
            category_map = {"appetizer": 0, "main": 1, "dessert": 2}
            category_filter = category_map.get(category)
        
        healthy_courses = []
        for course_idx, recipe in self.rag_db.recipes_db.items():
            if recipe.fsa_health_score <= max_fsa_score:
                if category_filter is None or recipe.category == category_filter:
                    healthy_courses.append({
                        "course_id": ToolUtils.get_real_course_id(self.rag_db, course_idx),
                        "course_name": recipe.course_name,
                        "category": ["appetizer", "main", "dessert"][recipe.category],
                        "fsa_score": recipe.fsa_health_score,
                        "who_score": recipe.who_health_score,
                        "combined_score": recipe.fsa_health_score + recipe.who_health_score
                    })
        
        # Sort by combined health score (healthiest first)
        healthy_courses.sort(key=lambda x: x["combined_score"])
        
        return {
            "criteria": {
                "max_fsa_score": max_fsa_score,
                "category": category
            },
            "courses": healthy_courses[:limit],
            "total_found": len(healthy_courses),
            "showing": min(limit, len(healthy_courses))
        }