"""
AI Agent for Meal Planning
Demonstrates AI agent patterns with reasoning chains
"""

import json
from typing import Dict, List, Any
import openai
from rag_database import MealRecRAGDatabase
from tools import MealPlanningTools

class MealPlanningAgent:
    """AI Agent for Meal Planning with LLM reasoning"""
    
    def __init__(self, rag_db: MealRecRAGDatabase, openai_api_key: str):
        self.rag_db = rag_db
        self.tools = MealPlanningTools(rag_db)
        self.client = openai.OpenAI(api_key=openai_api_key)
        print("🤖 AI Agent initialized with LLM capabilities")
    
    def plan_meal(self, user_request: str) -> Dict[str, Any]:
        """
        Main agent function - demonstrates reasoning chain:
        1. Parse user request
        2. Use tools to gather information (RAG retrieval)
        3. LLM reasoning
        4. Generate final recommendation
        """
        
        print(f"\n🎯 Agent Processing: '{user_request}'")
        
        # Step 1: Parse request
        parsed_request = self._parse_user_request(user_request)
        print(f"📝 Parsed: {parsed_request}")
        
        # Step 2: Use tools for information gathering (RAG)
        tool_results = self._gather_information(parsed_request)
        print(f"🔧 Tool results: {len(tool_results)} data points gathered")
        
        # Step 3: LLM Reasoning
        recommendation = self._llm_reasoning(user_request, tool_results)
        
        # Step 4: Format final response
        return {
            "user_request": user_request,
            "agent_reasoning": recommendation["reasoning"],
            "recommended_recipes": recommendation["recipes"],
            "tool_calls_made": len(tool_results),
            "rag_retrieval_count": sum(tr.get("recipes_found", 0) for tr in tool_results)
        }
    
    def _parse_user_request(self, request: str) -> Dict[str, Any]:
        """Parse user request into structured format"""
        request_lower = request.lower()
        
        parsed = {
            "categories": [],
            "health_preference": "balanced",
            "meal_type": "single"
        }
        
        # Category detection
        if "appetizer" in request_lower:
            parsed["categories"].append("appetizer")
        if "main" in request_lower or "dinner" in request_lower:
            parsed["categories"].append("main")
        if "dessert" in request_lower:
            parsed["categories"].append("dessert")
        
        # Default to main if no category specified
        if not parsed["categories"]:
            parsed["categories"] = ["main"]
        
        # Health preference
        if "very healthy" in request_lower:
            parsed["health_preference"] = "very_healthy"
        elif "healthy" in request_lower:
            parsed["health_preference"] = "healthy"
        
        # Multi-course detection
        if "3-course" in request_lower or "multi-course" in request_lower:
            parsed["meal_type"] = "multi_course"
            parsed["categories"] = ["appetizer", "main", "dessert"]
        
        return parsed
    
    def _gather_information(self, parsed_request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use tools to gather relevant information"""
        tool_results = []
        
        # Search for recipes in requested categories
        for category in parsed_request["categories"]:
            result = self.tools.search_healthy_recipes(
                category=category,
                health_preference=parsed_request["health_preference"]
            )
            tool_results.append(result)
        
        # Get meal composition analysis for educational demo
        composition_analysis = self.tools.analyze_meal_compositions()
        tool_results.append(composition_analysis)
        
        return tool_results
    
    def _llm_reasoning(self, user_request: str, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LLM-powered reasoning"""
        
        # Format tool results for LLM context
        context = "Available recipe data from MealRec+ dataset:\n"
        for result in tool_results:
            context += f"\nTool: {result.get('tool', 'unknown')}\n"
            if "recipes" in result:
                context += f"Found {len(result['recipes'])} recipes:\n"
                for recipe in result["recipes"][:3]:  # Limit for token efficiency
                    context += f"- {recipe['name']} ({recipe['category']}, FSA: {recipe['fsa_score']}, WHO: {recipe['who_score']})\n"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a meal planning AI agent. Use the provided recipe data to make recommendations. Focus on health scores (lower is better) and user preferences. Respond with a JSON object containing 'recipes' (list of recipe names) and 'reasoning' (string explanation)."
                    },
                    {
                        "role": "user", 
                        "content": f"User request: {user_request}\n\n{context}\n\nPlease recommend the best recipes and explain your reasoning."
                    }
                ],
                max_tokens=500
            )
            
            # Parse LLM response
            llm_response = response.choices[0].message.content
            try:
                parsed_response = json.loads(llm_response)
                return parsed_response
            except:
                return {
                    "recipes": [],
                    "reasoning": f"LLM provided reasoning: {llm_response}"
                }
                
        except Exception as e:
            print(f"LLM error: {e}")
            raise Exception(f"LLM reasoning failed: {e}")