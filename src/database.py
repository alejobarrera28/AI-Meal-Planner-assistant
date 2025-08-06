"""
Simple Meal Database - Educational RAG implementation
Loads MealRec+ dataset for demonstrating AI concepts
"""

import os
from typing import Dict, List, Any


class MealDatabase:
    """Simple database for educational AI meal planning demo"""

    def __init__(self, data_path: str = "MealRec+/MealRec+H"):
        self.data_path = data_path
        
        # Load core data silently
        self.courses = self._load_courses()
        self.meals = self._load_meals()
        self.health_scores = self._load_health_scores()

    def _load_courses(self) -> Dict[int, Dict]:
        """Load course data with categories"""
        courses = {}
        categories = {0: "appetizer", 1: "main", 2: "dessert"}
        
        # Load categories
        try:
            with open(os.path.join(self.data_path, "course_category.txt"), "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        course_id = int(parts[0])
                        category_id = int(parts[1])
                        courses[course_id] = {
                            "id": course_id,
                            "name": f"Course {course_id}",
                            "category": categories.get(category_id, "unknown")
                        }
        except Exception:
            pass  # Silently handle errors
        
        return courses

    def _load_meals(self) -> Dict[int, List[int]]:
        """Load meal compositions (which courses make up each meal)"""
        meals = {}
        try:
            with open(os.path.join(self.data_path, "meal_course.txt"), "r") as f:
                for line in f:
                    parts = line.strip().split("\t")
                    if len(parts) >= 2:
                        meal_id = int(parts[0])
                        course_id = int(parts[1])
                        if meal_id not in meals:
                            meals[meal_id] = []
                        meals[meal_id].append(course_id)
        except Exception:
            pass  # Silently handle errors
        
        return meals

    def _load_health_scores(self) -> Dict[int, Dict]:
        """Load FSA health scores (lower = healthier)"""
        scores = {}
        try:
            with open(os.path.join(self.data_path, "healthiness/course_fsa.txt"), "r") as f:
                for course_id, line in enumerate(f):
                    fsa_score = float(line.strip())
                    scores[course_id] = {"fsa": fsa_score}
        except Exception:
            pass  # Silently handle errors
        
        return scores

    def search_courses_by_category(self, category: str, limit: int = 10) -> List[Dict]:
        """Search for courses in a specific category"""
        results = []
        for course in self.courses.values():
            if course["category"].lower() == category.lower():
                # Add health score if available
                health_info = self.health_scores.get(course["id"], {})
                course_with_health = course.copy()
                course_with_health.update(health_info)
                results.append(course_with_health)
                
                if len(results) >= limit:
                    break
        
        return results

    def filter_healthy_courses(self, max_fsa_score: float = 5.0, limit: int = 10) -> List[Dict]:
        """Find courses with good health scores (lower FSA = healthier)"""
        results = []
        for course_id, course in self.courses.items():
            health = self.health_scores.get(course_id, {"fsa": 10.0})
            if health.get("fsa", 10.0) <= max_fsa_score:
                course_with_health = course.copy()
                course_with_health.update(health)
                results.append(course_with_health)
                
                if len(results) >= limit:
                    break
        
        # Sort by health score (lower = better)
        results.sort(key=lambda x: x.get("fsa", 10.0))
        return results

    def get_meal_composition(self, meal_id: int) -> Dict[str, Any]:
        """Get the courses that make up a specific meal"""
        if meal_id not in self.meals:
            return {"error": f"Meal {meal_id} not found"}
        
        course_ids = self.meals[meal_id]
        courses = []
        
        for course_id in course_ids:
            if course_id in self.courses:
                course = self.courses[course_id].copy()
                health = self.health_scores.get(course_id, {})
                course.update(health)
                courses.append(course)
        
        return {
            "meal_id": meal_id,
            "courses": courses,
            "total_courses": len(courses)
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_courses": len(self.courses),
            "total_meals": len(self.meals),
            "categories": list(set(c["category"] for c in self.courses.values())),
            "health_scores_available": len(self.health_scores) > 0
        }