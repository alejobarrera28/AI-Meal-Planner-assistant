"""
Data models for the AI Meal Planning Agent
Simple dataclasses representing the core data structures
"""

from dataclasses import dataclass
from typing import List

@dataclass
class MealRecipe:
    """Recipe from MealRec+ dataset"""
    course_index: int
    course_name: str
    category: int  # 0=appetizer, 1=main, 2=dessert
    fsa_health_score: float  # Lower is healthier (1-15)
    who_health_score: float  # Lower is healthier (1-15)
    meal_affiliations: List[int]  # Which meals this course belongs to

@dataclass 
class QueryResult:
    """Result from RAG retrieval"""
    recipes: List[MealRecipe]
    reasoning: str
    total_found: int