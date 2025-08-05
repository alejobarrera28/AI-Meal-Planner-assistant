"""
AI Meal Planning Chatbot with LLM function calling
"""

import json
from typing import Dict, List, Any
import openai
from .schemas import get_tool_schemas


class MealPlanningChatbot:
    """AI Meal Planning Chatbot with LLM function calling"""

    def __init__(
        self, rag_db, tool_registry, openai_api_key: str, model: str = "gpt-4"
    ):
        self.rag_db = rag_db
        self.tool_registry = tool_registry
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
                tools=get_tool_schemas(),
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
            
            # Execute the tool using the registry
            try:
                result = self.tool_registry.execute_tool(function_name, **function_args)
                result_str = json.dumps(result, indent=2)
                    
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

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history reset")