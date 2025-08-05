"""Core chatbot functionality"""

from .schemas import get_tool_schemas

# Try to import chatbot, but allow graceful failure if openai is not available
try:
    from .chatbot import MealPlanningChatbot
    __all__ = ['MealPlanningChatbot', 'get_tool_schemas']
except ImportError as e:
    if "openai" in str(e):
        # OpenAI not available - only export schemas
        __all__ = ['get_tool_schemas']
    else:
        raise