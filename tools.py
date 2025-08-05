"""
Comprehensive Tool Suite for LLM Function Calling
Provides structured functions for meal planning and recipe analysis
"""

from typing import Dict, List, Any, Optional
from rag_database import MealRecRAGDatabase



class MealPlanningTools:
    """Comprehensive tool suite for LLM function calling"""

    def __init__(self, rag_db: MealRecRAGDatabase):
        self.rag_db = rag_db

    def filter_courses(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter courses based on category, health scores, or other criteria"""
        
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
                "course_id": self._get_real_course_id(course_idx),
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

    def generate_meal_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete meal plan (appetizer, main, dessert) based on dietary goals"""
        
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
                    "course_id": self._get_real_course_id(course_idx),
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

    def calculate_health_score(self, item_id: int, score_type: str, item_type: str = "course") -> Dict[str, Any]:
        """Calculate health score for a course or meal"""
        
        if item_type == "course":
            if item_id not in self.rag_db.recipes_db:
                return {"error": f"Course {item_id} not found"}
                
            recipe = self.rag_db.recipes_db[item_id]
            
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
                "health_rating": self._get_health_rating(score),
                "course_name": recipe.course_name,
                "category": ["appetizer", "main", "dessert"][recipe.category]
            }
            
        elif item_type == "meal":
            if item_id not in self.rag_db.meal_course_mapping:
                return {"error": f"Meal {item_id} not found"}
                
            course_indices = self.rag_db.meal_course_mapping[item_id]
            scores = []
            
            for course_idx in course_indices:
                if course_idx in self.rag_db.recipes_db:
                    recipe = self.rag_db.recipes_db[course_idx]
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
                "health_rating": self._get_health_rating(avg_score),
                "course_count": len(scores),
                "individual_scores": scores
            }

    def get_user_history(self, user_id: int) -> Dict[str, Any]:
        """Get user's meal history and preferences"""
        
        # Get user's course interactions
        user_courses = [course_idx for uid, course_idx in self.rag_db.user_course_interactions if uid == user_id]
        
        # Get user's meal interactions
        user_meals = []
        for split in ["train", "test", "tune"]:
            user_meals.extend([meal_idx for uid, meal_idx in self.rag_db.user_meal_interactions.get(split, []) if uid == user_id])
        
        if not user_courses and not user_meals:
            return {"error": f"No history found for user {user_id}"}
        
        # Analyze preferences
        category_counts = {0: 0, 1: 0, 2: 0}  # appetizer, main, dessert
        health_scores = []
        
        for course_idx in user_courses:
            if course_idx in self.rag_db.recipes_db:
                recipe = self.rag_db.recipes_db[course_idx]
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
            "health_preference": self._get_health_rating(avg_health_score),
            "most_preferred_category": max(category_preferences.keys(), key=category_preferences.get) if category_preferences else None
        }

    def swap_for_healthier(self, course_id: int, improvement_threshold: float = 1.0) -> Dict[str, Any]:
        """Find a healthier alternative to a given course in the same category"""
        
        # Convert real course ID to course index if needed
        course_idx = course_id
        if course_id in self.rag_db.course_to_index:
            course_idx = self.rag_db.course_to_index[course_id]
        
        if course_idx not in self.rag_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
            
        original_recipe = self.rag_db.recipes_db[course_idx]
        original_score = original_recipe.fsa_health_score
        target_category = original_recipe.category
        
        # Find alternatives in same category
        alternatives = []
        for other_id, recipe in self.rag_db.recipes_db.items():
            if (recipe.category == target_category and 
                other_id != course_idx and
                recipe.fsa_health_score < (original_score - improvement_threshold)):
                
                improvement = original_score - recipe.fsa_health_score
                alternatives.append((other_id, recipe, improvement))
        
        if not alternatives:
            return {
                "original_course": {
                    "course_id": self._get_real_course_id(course_id),
                    "course_name": original_recipe.course_name,
                    "fsa_score": original_score
                },
                "message": f"No healthier alternatives found with improvement >= {improvement_threshold}",
                "alternatives_checked": sum(1 for _, recipe in self.rag_db.recipes_db.items() if recipe.category == target_category) - 1
            }
        
        # Sort by improvement (best first)
        alternatives.sort(key=lambda x: x[2], reverse=True)
        best_id, best_recipe, improvement = alternatives[0]
        
        return {
            "original_course": {
                "course_id": self._get_real_course_id(course_idx),
                "course_name": original_recipe.course_name,
                "fsa_score": original_score,
                "who_score": original_recipe.who_health_score
            },
            "healthier_alternative": {
                "course_id": self._get_real_course_id(best_id),
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

    def summarize_recipe(self, course_id: int) -> Dict[str, Any]:
        """Generate a natural language summary of a course/recipe"""
        
        # Convert real course ID to course index if needed
        course_idx = course_id
        if course_id in self.rag_db.course_to_index:
            course_idx = self.rag_db.course_to_index[course_id]
        
        if course_idx not in self.rag_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
            
        recipe = self.rag_db.recipes_db[course_idx]
        category_name = ["appetizer", "main course", "dessert"][recipe.category]
        
        # Health rating
        health_rating = self._get_health_rating(recipe.fsa_health_score)
        
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
            "course_id": self._get_real_course_id(course_idx),
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

    def search_courses_by_category(self, category: str, limit: int = 10) -> Dict[str, Any]:
        """Search for courses in a specific category"""
        
        category_map = {"appetizer": 0, "main": 1, "dessert": 2}
        category_idx = category_map.get(category)
        
        if category_idx is None:
            return {"error": f"Invalid category: {category}. Use appetizer, main, or dessert"}
        
        courses = []
        for course_idx, recipe in self.rag_db.recipes_db.items():
            if recipe.category == category_idx:
                courses.append({
                    "course_id": self._get_real_course_id(course_idx),
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

    def find_healthy_courses(self, max_fsa_score: float, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """Find the healthiest courses with optional category filter"""
        
        category_filter = None
        if category:
            category_map = {"appetizer": 0, "main": 1, "dessert": 2}
            category_filter = category_map.get(category)
        
        healthy_courses = []
        for course_idx, recipe in self.rag_db.recipes_db.items():
            if recipe.fsa_health_score <= max_fsa_score:
                if category_filter is None or recipe.category == category_filter:
                    healthy_courses.append({
                        "course_id": self._get_real_course_id(course_idx),
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

    def get_meal_composition(self, meal_id: int) -> Dict[str, Any]:
        """Get all courses that make up a specific meal"""
        
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
                    "course_id": self._get_real_course_id(course_idx),
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
            "health_rating": self._get_health_rating(avg_fsa)
        }

    def recommend_similar_meals(self, course_id: int, limit: int = 5) -> Dict[str, Any]:
        """Find meals containing similar courses to a given course"""
        
        # Convert real course ID to course index if needed
        course_idx = course_id
        if course_id in self.rag_db.course_to_index:
            course_idx = self.rag_db.course_to_index[course_id]
        
        if course_idx not in self.rag_db.recipes_db:
            return {"error": f"Course {course_id} not found"}
        
        reference_recipe = self.rag_db.recipes_db[course_idx]
        reference_category = reference_recipe.category
        
        # Find meals containing the reference course
        meals_with_course = reference_recipe.meal_affiliations
        
        # Find similar meals (same category courses)
        similar_meals = []
        for meal_id, course_indices in self.rag_db.meal_course_mapping.items():
            if meal_id in meals_with_course:
                continue  # Skip meals that already contain this course
                
            # Check if meal has courses in same category
            has_similar_category = any(
                self.rag_db.recipes_db.get(idx, {}).category == reference_category 
                for idx in course_indices
                if idx in self.rag_db.recipes_db
            )
            
            if has_similar_category:
                # Calculate meal health score
                meal_scores = [
                    self.rag_db.recipes_db[idx].fsa_health_score 
                    for idx in course_indices 
                    if idx in self.rag_db.recipes_db
                ]
                avg_score = sum(meal_scores) / len(meal_scores) if meal_scores else 10
                
                similar_meals.append({
                    "meal_id": meal_id,
                    "course_count": len(course_indices),
                    "average_health_score": round(avg_score, 2),
                    "courses": [
                        {
                            "course_id": self._get_real_course_id(idx),
                            "course_name": self.rag_db.recipes_db[idx].course_name,
                            "category": ["appetizer", "main", "dessert"][self.rag_db.recipes_db[idx].category]
                        }
                        for idx in course_indices
                        if idx in self.rag_db.recipes_db
                    ]
                })
        
        # Sort by health score (healthiest first)
        similar_meals.sort(key=lambda x: x["average_health_score"])
        
        return {
            "reference_course": {
                "course_id": self._get_real_course_id(course_idx),
                "course_name": reference_recipe.course_name,
                "category": ["appetizer", "main", "dessert"][reference_category]
            },
            "similar_meals": similar_meals[:limit],
            "total_found": len(similar_meals),
            "meals_with_reference_course": len(meals_with_course)
        }

    def _get_real_course_id(self, course_idx: int) -> int:
        """Get real course ID from course index"""
        for real_id, idx in self.rag_db.course_to_index.items():
            if idx == course_idx:
                return real_id
        return course_idx  # Fallback to course index

    def _get_health_rating(self, score: float) -> str:
        """Convert health score to rating"""
        if score <= 4:
            return "excellent"
        elif score <= 6:
            return "very good"
        elif score <= 8:
            return "good"
        elif score <= 10:
            return "fair"
        else:
            return "poor"