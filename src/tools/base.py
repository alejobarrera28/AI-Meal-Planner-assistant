"""
Base tool functionality and utilities
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Base class for all meal planning tools"""
    
    def __init__(self, meal_db):
        self.meal_db = meal_db
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass


class ToolUtils:
    """Common utilities for tools"""
    
    @staticmethod
    def get_real_course_id(meal_db, course_idx: int) -> int:
        """Get real course ID from course index"""
        for real_id, idx in meal_db.course_to_index.items():
            if idx == course_idx:
                return real_id
        return course_idx  # Fallback to course index

    @staticmethod
    def get_health_rating(score: float) -> str:
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

    @staticmethod
    def convert_course_id_to_index(meal_db, course_id: int) -> int:
        """Convert real course ID to course index if needed"""
        if course_id in meal_db.course_to_index:
            return meal_db.course_to_index[course_id]
        return course_id