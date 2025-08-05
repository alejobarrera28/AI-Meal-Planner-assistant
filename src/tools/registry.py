"""
Tool registry and management for dynamic tool loading
"""

from typing import Dict, Any, List
from .filtering import FilterCoursesTool, SearchCoursesByCategoryTool, FindHealthyCoursesTool
from .meal_planning import GenerateMealPlanTool, GetMealCompositionTool
from .health import CalculateHealthScoreTool, SwapForHealthierTool
from .user import GetUserHistoryTool
from .analysis import SummarizeRecipeTool, RecommendSimilarMealsTool


class ToolRegistry:
    """Registry for managing all available tools"""
    
    def __init__(self, meal_db):
        self.meal_db = meal_db
        self._tools = self._initialize_tools()
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize all available tools"""
        return {
            "filter_courses": FilterCoursesTool(self.meal_db),
            "search_courses_by_category": SearchCoursesByCategoryTool(self.meal_db),
            "find_healthy_courses": FindHealthyCoursesTool(self.meal_db),
            "generate_meal_plan": GenerateMealPlanTool(self.meal_db),
            "get_meal_composition": GetMealCompositionTool(self.meal_db),
            "calculate_health_score": CalculateHealthScoreTool(self.meal_db),
            "swap_for_healthier": SwapForHealthierTool(self.meal_db),
            "get_user_history": GetUserHistoryTool(self.meal_db),
            "summarize_recipe": SummarizeRecipeTool(self.meal_db),
            "recommend_similar_meals": RecommendSimilarMealsTool(self.meal_db)
        }
    
    def get_tool(self, tool_name: str):
        """Get a specific tool by name"""
        return self._tools.get(tool_name)
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def list_available_tools(self) -> List[str]:
        """Get list of all available tool names"""
        return list(self._tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool exists"""
        return tool_name in self._tools


# Legacy compatibility wrapper - maintains the original interface
class MealPlanningTools:
    """Legacy wrapper to maintain compatibility with existing code"""
    
    def __init__(self, meal_db):
        self.registry = ToolRegistry(meal_db)
    
    def filter_courses(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        return self.registry.execute_tool("filter_courses", criteria=criteria)
    
    def generate_meal_plan(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        return self.registry.execute_tool("generate_meal_plan", goal=goal)
    
    def calculate_health_score(self, item_id: int, score_type: str, item_type: str = "course") -> Dict[str, Any]:
        return self.registry.execute_tool("calculate_health_score", item_id=item_id, score_type=score_type, item_type=item_type)
    
    def get_user_history(self, user_id: int) -> Dict[str, Any]:
        return self.registry.execute_tool("get_user_history", user_id=user_id)
    
    def swap_for_healthier(self, course_id: int, improvement_threshold: float = 1.0) -> Dict[str, Any]:
        return self.registry.execute_tool("swap_for_healthier", course_id=course_id, improvement_threshold=improvement_threshold)
    
    def summarize_recipe(self, course_id: int) -> Dict[str, Any]:
        return self.registry.execute_tool("summarize_recipe", course_id=course_id)
    
    def search_courses_by_category(self, category: str, limit: int = 10) -> Dict[str, Any]:
        return self.registry.execute_tool("search_courses_by_category", category=category, limit=limit)
    
    def find_healthy_courses(self, max_fsa_score: float, category: str = None, limit: int = 10) -> Dict[str, Any]:
        return self.registry.execute_tool("find_healthy_courses", max_fsa_score=max_fsa_score, category=category, limit=limit)
    
    def get_meal_composition(self, meal_id: int) -> Dict[str, Any]:
        return self.registry.execute_tool("get_meal_composition", meal_id=meal_id)
    
    def recommend_similar_meals(self, course_id: int, limit: int = 5) -> Dict[str, Any]:
        return self.registry.execute_tool("recommend_similar_meals", course_id=course_id, limit=limit)