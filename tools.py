"""
Tool Calls Interface - Structured functions for AI agent to use
Demonstrates function calling patterns for AI agents
"""

from typing import Dict, List, Any
from rag_database import MealRecRAGDatabase


class MealPlanningTools:
    """Tool Calls Interface - Structured functions for AI agent to use"""

    def __init__(self, rag_db: MealRecRAGDatabase):
        self.rag_db = rag_db

    def search_healthy_recipes(
        self, category: str = "any", health_preference: str = "balanced"
    ) -> Dict[str, Any]:
        """Tool: Search for healthy recipes"""

        # Parse category
        category_map = {"appetizer": 0, "main": 1, "dessert": 2}
        category_filter = (
            category_map.get(category.lower()) if category != "any" else None
        )

        # Parse health preference to score thresholds
        health_thresholds = {"very_healthy": 6.0, "healthy": 8.0, "balanced": 10.0}
        max_fsa = health_thresholds.get(health_preference, 10.0)

        # Retrieve using RAG
        result = self.rag_db.retrieve_recipes(
            category=category_filter, max_fsa_score=max_fsa, limit=5
        )

        return {
            "tool": "search_healthy_recipes",
            "recipes_found": len(result.recipes),
            "total_available": result.total_found,
            "recipes": [
                {
                    "name": recipe.course_name,
                    "category": ["appetizer", "main", "dessert"][recipe.category],
                    "fsa_score": recipe.fsa_health_score,
                    "who_score": recipe.who_health_score,
                }
                for recipe in result.recipes
            ],
            "reasoning": result.reasoning,
        }

    def analyze_meal_compositions(self, sample_size: int = 5) -> Dict[str, Any]:
        """Tool: Analyze meal compositions from dataset"""

        sample_meals = list(self.rag_db.meal_course_mapping.keys())[:sample_size]
        analyses = []

        for meal_id in sample_meals:
            course_indices = self.rag_db.meal_course_mapping[meal_id]
            courses_info = []

            for course_idx in course_indices:
                if course_idx in self.rag_db.recipes_db:
                    recipe = self.rag_db.recipes_db[course_idx]
                    courses_info.append(
                        {
                            "name": recipe.course_name,
                            "category": ["appetizer", "main", "dessert"][
                                recipe.category
                            ],
                            "health_score": (
                                recipe.fsa_health_score + recipe.who_health_score
                            )
                            / 2,
                        }
                    )

            analyses.append(
                {
                    "meal_id": meal_id,
                    "course_count": len(courses_info),
                    "courses": courses_info,
                    "avg_health_score": (
                        sum(c["health_score"] for c in courses_info) / len(courses_info)
                        if courses_info
                        else 0
                    ),
                }
            )

        return {
            "tool": "analyze_meal_compositions",
            "sample_size": len(analyses),
            "analyses": analyses,
        }
