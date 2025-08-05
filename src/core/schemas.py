"""
OpenAI function schemas for LLM tool calling
"""

from typing import List, Dict, Any


def get_tool_schemas() -> List[Dict[str, Any]]:
    """Get OpenAI function schemas for all available tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "filter_courses",
                "description": "Filter courses based on category, health scores, or other criteria",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "criteria": {
                            "type": "object",
                            "description": "Filtering criteria",
                            "properties": {
                                "category": {"type": "string", "enum": ["appetizer", "main", "dessert"], "description": "Course category"},
                                "max_fsa_score": {"type": "number", "description": "Maximum FSA health score (lower is healthier)"},
                                "max_who_score": {"type": "number", "description": "Maximum WHO health score (lower is healthier)"},
                                "limit": {"type": "integer", "description": "Maximum number of results", "default": 10}
                            }
                        }
                    },
                    "required": ["criteria"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "generate_meal_plan",
                "description": "Generate a complete meal plan (appetizer, main, dessert) based on dietary goals",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "object",
                            "description": "Meal planning goals and preferences",
                            "properties": {
                                "health_focus": {"type": "string", "enum": ["weight_loss", "heart_healthy", "balanced", "low_sodium"], "description": "Health focus"},
                                "max_avg_health_score": {"type": "number", "description": "Maximum average health score for the meal"},
                                "include_categories": {"type": "array", "items": {"type": "string"}, "description": "Categories to include"}
                            }
                        }
                    },
                    "required": ["goal"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_health_score",
                "description": "Calculate health score for a course or meal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "integer", "description": "Course or meal ID"},
                        "score_type": {"type": "string", "enum": ["fsa", "who", "combined"], "description": "Type of health score to calculate"},
                        "item_type": {"type": "string", "enum": ["course", "meal"], "description": "Whether calculating for course or meal"}
                    },
                    "required": ["item_id", "score_type", "item_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_history", 
                "description": "Get user's meal history and preferences",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "integer", "description": "User ID to analyze"}
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "swap_for_healthier",
                "description": "Find a healthier alternative to a given course in the same category",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "course_id": {"type": "integer", "description": "Original course ID to replace"},
                        "improvement_threshold": {"type": "number", "description": "Minimum health score improvement required", "default": 1.0}
                    },
                    "required": ["course_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "summarize_recipe",
                "description": "Generate a natural language summary of a course/recipe",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "integer", "description": "Course ID to summarize"}
                    },
                    "required": ["course_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_courses_by_category",
                "description": "Search for courses in a specific category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["appetizer", "main", "dessert"], "description": "Course category"},
                        "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                    },
                    "required": ["category"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_healthy_courses",
                "description": "Find the healthiest courses with optional category filter", 
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_fsa_score": {"type": "number", "description": "Maximum FSA score threshold"},
                        "category": {"type": "string", "enum": ["appetizer", "main", "dessert"], "description": "Optional category filter"},
                        "limit": {"type": "integer", "description": "Maximum results", "default": 10}
                    },
                    "required": ["max_fsa_score"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_meal_composition",
                "description": "Get all courses that make up a specific meal",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "meal_id": {"type": "integer", "description": "Meal ID to analyze"}
                    },
                    "required": ["meal_id"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "recommend_similar_meals",
                "description": "Find meals containing similar courses to a given course",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {"type": "integer", "description": "Reference course ID"},
                        "limit": {"type": "integer", "description": "Maximum results", "default": 5}
                    },
                    "required": ["course_id"]
                }
            }
        }
    ]