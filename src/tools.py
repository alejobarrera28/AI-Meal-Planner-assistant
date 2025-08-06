"""
Simple AI Tools - Educational demonstration of tool calling
Contains 3 core tools for meal planning AI agent
"""

import random
from typing import Dict, List, Any


def search_courses_by_category(database, category: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for courses in a specific category (appetizer, main, dessert)
    
    Args:
        category: Category to search for
        limit: Maximum number of results
    """
    results = database.search_courses_by_category(category, limit)
    
    return {
        "tool": "search_courses_by_category",
        "query": {"category": category, "limit": limit},
        "results": results,
        "count": len(results),
        "message": f"Found {len(results)} {category} courses"
    }


def filter_healthy_courses(database, max_fsa_score: float = 5.0, category: str = None, limit: int = 10) -> Dict[str, Any]:
    """
    Find healthy courses with low FSA scores (lower = healthier)
    
    Args:
        max_fsa_score: Maximum FSA health score (lower is healthier)
        category: Optional category filter (appetizer, main, dessert)
        limit: Maximum number of results
    """
    # First get healthy courses
    healthy_results = database.filter_healthy_courses(max_fsa_score, limit * 3)  # Get more to filter by category
    
    # Filter by category if specified
    if category:
        healthy_results = [course for course in healthy_results if course.get("category") == category]
    
    # Limit final results
    results = healthy_results[:limit]
    
    category_msg = f" {category}" if category else ""
    return {
        "tool": "filter_healthy_courses", 
        "query": {"max_fsa_score": max_fsa_score, "category": category, "limit": limit},
        "results": results,
        "count": len(results),
        "message": f"Found {len(results)} healthy{category_msg} courses with FSA ≤ {max_fsa_score}"
    }


def generate_meal_plan(database, goal: str = "balanced", num_meals: int = 3) -> Dict[str, Any]:
    """
    Generate a meal plan with appetizer, main, and dessert
    
    Args:
        goal: Type of meal plan (healthy, balanced, varied)
        num_meals: Number of meals to plan
    """
    meals = []
    
    for i in range(num_meals):
        meal = {"meal_id": i + 1, "courses": []}
        
        # Get one course from each category
        for category in ["appetizer", "main", "dessert"]:
            if goal == "healthy":
                # For healthy meals, prefer lower FSA scores
                candidates = database.filter_healthy_courses(max_fsa_score=4.0, limit=50)
                # Filter by category
                category_candidates = [c for c in candidates if c.get("category") == category]
            else:
                # For balanced/varied meals, get any from category
                category_candidates = database.search_courses_by_category(category, limit=50)
            
            if category_candidates:
                # Randomly select to add variety
                selected = random.choice(category_candidates)
                meal["courses"].append(selected)
        
        meals.append(meal)
    
    # Calculate overall health score
    total_fsa = sum(
        course.get("fsa", 5.0) 
        for meal in meals 
        for course in meal["courses"]
    )
    avg_fsa = total_fsa / max(1, sum(len(meal["courses"]) for meal in meals))
    
    return {
        "tool": "generate_meal_plan",
        "query": {"goal": goal, "num_meals": num_meals},
        "meals": meals,
        "total_meals": len(meals),
        "avg_health_score": round(avg_fsa, 2),
        "health_rating": "Excellent" if avg_fsa < 3 else "Good" if avg_fsa < 5 else "Fair",
        "message": f"Generated {len(meals)} {goal} meals with average FSA score {avg_fsa:.1f}"
    }


# Tool registry for easy access
AVAILABLE_TOOLS = {
    "search_courses_by_category": search_courses_by_category,
    "filter_healthy_courses": filter_healthy_courses, 
    "generate_meal_plan": generate_meal_plan
}


def execute_tool(database, tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by name with given parameters"""
    if tool_name not in AVAILABLE_TOOLS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    # Check for malformed tool calls (when LLM passes schema instead of parameters)
    if "properties" in kwargs or "type" in kwargs or "required" in kwargs:
        return {
            "error": "LLM passed tool schema instead of parameters - this is a function calling error",
            "suggestion": f"The LLM should call {tool_name} with actual parameter values, not the schema definition"
        }
    
    try:
        tool_function = AVAILABLE_TOOLS[tool_name]
        return tool_function(database, **kwargs)
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


def list_tools() -> List[str]:
    """Get list of available tool names"""
    return list(AVAILABLE_TOOLS.keys())