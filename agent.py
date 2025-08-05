"""
AI Meal Planning Chatbot
Demonstrates LLM function calling with conversational interface
"""

import json
from typing import Dict, List, Any
import openai
from rag_database import MealRecRAGDatabase
from tools import MealPlanningTools


class MealPlanningChatbot:
    """AI Meal Planning Chatbot with LLM function calling"""

    def __init__(
        self, rag_db: MealRecRAGDatabase, openai_api_key: str, model: str = "gpt-4"
    ):
        self.rag_db = rag_db
        self.tools = MealPlanningTools(rag_db)
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.model = model
        self.conversation_history = []
        print("🤖 Meal Planning Chatbot initialized with function calling capabilities")

    def chat(self, user_message: str) -> str:
        """
        Main chatbot function - handles conversation with LLM function calling:
        1. Add user message to conversation
        2. Send to LLM with available tools
        3. Handle any function calls
        4. Return natural language response
        """
        
        print(f"\n💬 User: {user_message}")
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Get LLM response with function calling
        response = self._get_llm_response()
        
        print(f"🤖 Chatbot: {response}")
        return response

    def _get_llm_response(self) -> str:
        """Get response from LLM with function calling support"""
        
        # Add system message if this is the first interaction
        messages = []
        if not any(msg["role"] == "system" for msg in self.conversation_history):
            messages.append({
                "role": "system", 
                "content": """You are a helpful meal planning assistant. You have access to a real MealRec+ dataset with:
- 17,091 courses across 3 categories (appetizer, main, dessert)
- Real health scores (FSA/WHO) where lower scores = healthier
- Meal compositions showing how courses combine
- User preference data

Use the available tools to help users with meal planning, health goals, and recipe recommendations. 
Always provide natural, conversational responses after using tools."""
            })
        
        messages.extend(self.conversation_history)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self._get_tool_schemas(),
                tool_choice="auto",
                max_tokens=1000
            )
            
            response_message = response.choices[0].message
            
            # Handle function calls
            if response_message.tool_calls:
                return self._handle_function_calls(response_message)
            else:
                # Regular text response
                assistant_response = response_message.content
                self.conversation_history.append({"role": "assistant", "content": assistant_response})
                return assistant_response
                
        except Exception as e:
            error_msg = f"Sorry, I encountered an error: {e}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg

    def _handle_function_calls(self, response_message) -> str:
        """Execute function calls and get final response"""
        
        # Add the assistant's function call message to conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": response_message.tool_calls
        })
        
        # Execute each function call
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🔧 Calling tool: {function_name}({function_args})")
            
            # Execute the tool
            try:
                if hasattr(self.tools, function_name):
                    result = getattr(self.tools, function_name)(**function_args)
                    result_str = json.dumps(result, indent=2)
                else:
                    result_str = f"Error: Unknown function {function_name}"
                    
            except Exception as e:
                result_str = f"Error executing {function_name}: {e}"
            
            # Add function result to conversation
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_str
            })
        
        # Get final response from LLM after function execution
        try:
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                max_tokens=1000
            )
            
            final_content = final_response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": final_content})
            return final_content
            
        except Exception as e:
            error_msg = f"Error getting final response: {e}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg

    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
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

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history reset")