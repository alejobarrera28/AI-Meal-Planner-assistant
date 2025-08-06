"""
Simple configuration and tool schemas for LLM function calling
Educational demonstration of AI agent tool definitions
"""

# Simple tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_courses_by_category",
            "description": "Search for courses in a specific category (appetizer, main, dessert)",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category to search: appetizer, main, or dessert",
                        "enum": ["appetizer", "main", "dessert"]
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["category"]
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "filter_healthy_courses",
            "description": "Find healthy courses with low FSA health scores (lower scores = healthier), optionally filtered by category",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_fsa_score": {
                        "type": "number",
                        "description": "Maximum FSA health score (lower is healthier, typical range 0-10)",
                        "default": 5.0
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter: appetizer, main, or dessert",
                        "enum": ["appetizer", "main", "dessert"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return", 
                        "default": 10
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_meal_plan", 
            "description": "Generate a complete meal plan with appetizer, main course, and dessert",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Type of meal plan to generate",
                        "enum": ["healthy", "balanced", "varied"],
                        "default": "balanced"
                    },
                    "num_meals": {
                        "type": "integer",
                        "description": "Number of complete meals to plan",
                        "default": 3
                    }
                },
                "required": []
            }
        }
    }
]

# System prompt for the AI agent
SYSTEM_PROMPT = """You are a meal planning assistant. You MUST call tools before providing any meal recommendations.

CRITICAL: You are FORBIDDEN from providing course names, IDs, or health scores without first calling tools.

WORKFLOW:
1. User asks for meals/courses → You MUST call appropriate tool FIRST
2. Tool returns real data → Then you respond using ONLY that data
3. NEVER make up course names like "Grilled Shrimp" or IDs like "CR1234"

Tools available:
- search_courses_by_category: Find appetizers/mains/desserts  
- filter_healthy_courses: Find courses with low FSA scores (category optional)
- generate_meal_plan: Create complete meal plans

EXAMPLE: User says "find healthy appetizers" → You call filter_healthy_courses(max_fsa_score=5.0, category="appetizer", limit=5) → Use returned data only.

You CANNOT provide meal information without calling tools first."""