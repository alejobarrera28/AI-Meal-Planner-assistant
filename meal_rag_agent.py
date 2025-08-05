#!/usr/bin/env python3
"""
Educational AI Meal Planning Agent
Demonstrates RAG (Retrieval-Augmented Generation) + Tool Calls + AI Agents

For lecture on:
- RAG: Using real MealRec+ dataset as knowledge base
- Tool Calls: Structured functions for data retrieval and filtering  
- AI Agents: Intelligent meal planning with reasoning chains
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Optional dependencies with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

@dataclass
class MealRecipe:
    """Structured representation of a recipe from MealRec+ dataset"""
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

class MealRecRAGDatabase:
    """
    RAG Knowledge Base using real MealRec+ dataset files
    Demonstrates retrieval-augmented generation concepts
    """
    
    def __init__(self, data_path: str = "MealRec+/MealRec+H"):
        self.data_path = data_path
        print(f"🔍 Loading MealRec+ RAG database from: {data_path}")
        
        # Load real dataset components
        self.course_categories = self._load_course_categories()
        self.course_fsa_scores = self._load_health_scores('fsa')
        self.course_who_scores = self._load_health_scores('who')
        self.meal_course_mapping = self._load_meal_course_mapping()
        self.course_names = self._generate_course_names()
        
        # Create structured knowledge base
        self.recipes_db = self._build_recipe_database()
        
        print(f"📊 RAG Database loaded:")
        print(f"   - {len(self.recipes_db)} recipes indexed")
        print(f"   - {len(self.course_categories)} course categories")
        print(f"   - {len(self.meal_course_mapping)} meal compositions")
        
    def _load_course_categories(self) -> Dict[int, int]:
        """Load course category mapping from real data"""
        categories = {}
        file_path = os.path.join(self.data_path, 'course_category.txt')
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        course_idx = int(parts[0])
                        category = int(parts[1])
                        categories[course_idx] = category
        except Exception as e:
            print(f"⚠️  Error loading categories: {e}")
            
        return categories
    
    def _load_health_scores(self, score_type: str) -> Dict[int, float]:
        """Load FSA or WHO health scores from real data"""
        scores = {}
        file_path = os.path.join(self.data_path, 'healthiness', f'course_{score_type}.txt')
        
        try:
            with open(file_path, 'r') as f:
                for idx, line in enumerate(f):
                    score = float(line.strip())
                    scores[idx] = score
        except Exception as e:
            print(f"⚠️  Error loading {score_type} scores: {e}")
            
        return scores
    
    def _load_meal_course_mapping(self) -> Dict[int, List[int]]:
        """Load meal-to-course relationships from real data"""
        mapping = {}
        file_path = os.path.join(self.data_path, 'meal_course.txt')
        
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        meal_idx = int(parts[0])
                        course_idx = int(parts[1])
                        if meal_idx not in mapping:
                            mapping[meal_idx] = []
                        mapping[meal_idx].append(course_idx)
        except Exception as e:
            print(f"⚠️  Error loading meal-course mapping: {e}")
            
        return mapping
    
    def _generate_course_names(self) -> Dict[int, str]:
        """Generate meaningful course names for educational purposes"""
        # Educational recipe names for different categories
        recipe_templates = {
            0: [  # Appetizers
                "Mediterranean Bruschetta", "Spinach Artichoke Dip", "Stuffed Mushrooms",
                "Caprese Skewers", "Hummus Platter", "Caesar Salad", "Soup of the Day"
            ],
            1: [  # Main Courses  
                "Grilled Herb Chicken", "Pan-Seared Salmon", "Vegetarian Pasta Primavera",
                "Lean Beef Stir Fry", "Mediterranean Tofu Bowl", "Baked Cod with Vegetables",
                "Quinoa Power Bowl", "Turkey Meatballs", "Vegetable Curry"
            ],
            2: [  # Desserts
                "Mixed Berry Fruit Salad", "Dark Chocolate Avocado Mousse", 
                "Greek Yogurt Parfait", "Baked Cinnamon Apple", "Chia Seed Pudding",
                "Fresh Fruit Tart", "Coconut Rice Pudding"
            ]
        }
        
        names = {}
        name_counter = {0: 0, 1: 0, 2: 0}
        
        for course_idx, category in self.course_categories.items():
            if category in recipe_templates:
                templates = recipe_templates[category]
                name_idx = name_counter[category] % len(templates)
                names[course_idx] = templates[name_idx]
                name_counter[category] += 1
            else:
                names[course_idx] = f"Course {course_idx}"
                
        return names
    
    def _build_recipe_database(self) -> Dict[int, MealRecipe]:
        """Build structured recipe database for RAG retrieval"""
        recipes = {}
        
        for course_idx in self.course_categories.keys():
            # Find which meals this course belongs to
            meal_affiliations = []
            for meal_idx, courses in self.meal_course_mapping.items():
                if course_idx in courses:
                    meal_affiliations.append(meal_idx)
            
            recipe = MealRecipe(
                course_index=course_idx,
                course_name=self.course_names.get(course_idx, f"Course {course_idx}"),
                category=self.course_categories[course_idx],
                fsa_health_score=self.course_fsa_scores.get(course_idx, 8.0),
                who_health_score=self.course_who_scores.get(course_idx, 7.0),
                meal_affiliations=meal_affiliations
            )
            recipes[course_idx] = recipe
            
        return recipes
    
    def retrieve_recipes(self, 
                        category: Optional[int] = None,
                        max_fsa_score: Optional[float] = None,
                        max_who_score: Optional[float] = None,
                        limit: int = 10) -> QueryResult:
        """
        RAG Retrieval: Find relevant recipes based on criteria
        Demonstrates retrieval component of RAG
        """
        
        matching_recipes = []
        
        for recipe in self.recipes_db.values():
            # Category filter
            if category is not None and recipe.category != category:
                continue
                
            # Health score filters (lower is healthier)
            if max_fsa_score is not None and recipe.fsa_health_score > max_fsa_score:
                continue
            if max_who_score is not None and recipe.who_health_score > max_who_score:
                continue
                
            matching_recipes.append(recipe)
        
        # Sort by health scores (lower is better)
        matching_recipes.sort(key=lambda r: r.fsa_health_score + r.who_health_score)
        
        # Limit results
        limited_recipes = matching_recipes[:limit]
        
        # Generate reasoning for educational purposes
        category_names = {0: "appetizers", 1: "main courses", 2: "desserts"}
        reasoning = f"Retrieved {len(limited_recipes)} recipes"
        if category is not None:
            reasoning += f" from {category_names.get(category, 'unknown')} category"
        if max_fsa_score is not None:
            reasoning += f" with FSA health score ≤ {max_fsa_score}"
        if max_who_score is not None:
            reasoning += f" and WHO health score ≤ {max_who_score}"
        reasoning += f". Sorted by healthiness (best scores first)."
        
        return QueryResult(
            recipes=limited_recipes,
            reasoning=reasoning,
            total_found=len(matching_recipes)
        )

class MealPlanningTools:
    """
    Tool Calls Interface - Structured functions for AI agent to use
    Demonstrates function calling patterns for AI agents
    """
    
    def __init__(self, rag_db: MealRecRAGDatabase):
        self.rag_db = rag_db
    
    def search_healthy_recipes(self, 
                             category: str = "any",
                             health_preference: str = "balanced") -> Dict[str, Any]:
        """
        Tool: Search for healthy recipes
        
        Args:
            category: "appetizer", "main", "dessert", or "any"  
            health_preference: "very_healthy", "healthy", or "balanced"
        
        Returns:
            Dict with recipes and metadata
        """
        
        # Parse category
        category_map = {"appetizer": 0, "main": 1, "dessert": 2}
        category_filter = category_map.get(category.lower()) if category != "any" else None
        
        # Parse health preference to score thresholds
        health_thresholds = {
            "very_healthy": (6.0, 6.0),    # Very strict
            "healthy": (8.0, 8.0),         # Moderate  
            "balanced": (10.0, 10.0)       # Relaxed
        }
        max_fsa, max_who = health_thresholds.get(health_preference, (10.0, 10.0))
        
        # Retrieve using RAG
        result = self.rag_db.retrieve_recipes(
            category=category_filter,
            max_fsa_score=max_fsa,
            max_who_score=max_who,
            limit=5
        )
        
        return {
            "tool": "search_healthy_recipes",
            "parameters": {"category": category, "health_preference": health_preference},
            "recipes_found": len(result.recipes),
            "total_available": result.total_found,
            "recipes": [
                {
                    "name": recipe.course_name,
                    "category": ["appetizer", "main", "dessert"][recipe.category],
                    "fsa_score": recipe.fsa_health_score,
                    "who_score": recipe.who_health_score,
                    "meal_count": len(recipe.meal_affiliations)
                } for recipe in result.recipes
            ],
            "reasoning": result.reasoning
        }
    
    def get_meal_composition_analysis(self, meal_ids: List[int]) -> Dict[str, Any]:
        """
        Tool: Analyze meal compositions from dataset
        
        Args:
            meal_ids: List of meal IDs to analyze
            
        Returns:
            Analysis of meal structures
        """
        
        analysis = {
            "tool": "get_meal_composition_analysis", 
            "meal_analyses": [],
            "patterns": {"single_course": 0, "multi_course": 0, "avg_courses": 0}
        }
        
        total_courses = 0
        
        for meal_id in meal_ids[:5]:  # Limit for demo
            if meal_id in self.rag_db.meal_course_mapping:
                course_indices = self.rag_db.meal_course_mapping[meal_id]
                courses_info = []
                
                for course_idx in course_indices:
                    if course_idx in self.rag_db.recipes_db:
                        recipe = self.rag_db.recipes_db[course_idx]
                        courses_info.append({
                            "name": recipe.course_name,
                            "category": ["appetizer", "main", "dessert"][recipe.category],
                            "health_score": (recipe.fsa_health_score + recipe.who_health_score) / 2
                        })
                
                meal_analysis = {
                    "meal_id": meal_id,
                    "course_count": len(courses_info),
                    "courses": courses_info,
                    "avg_health_score": sum(c["health_score"] for c in courses_info) / len(courses_info) if courses_info else 0
                }
                
                analysis["meal_analyses"].append(meal_analysis)
                total_courses += len(courses_info)
                
                if len(courses_info) == 1:
                    analysis["patterns"]["single_course"] += 1
                else:
                    analysis["patterns"]["multi_course"] += 1
        
        analysis["patterns"]["avg_courses"] = total_courses / len(meal_ids) if meal_ids else 0
        
        return analysis
    
    def calculate_health_metrics(self, recipe_names: List[str]) -> Dict[str, Any]:
        """
        Tool: Calculate health metrics for selected recipes
        
        Args:
            recipe_names: List of recipe names to analyze
            
        Returns:
            Health metrics analysis
        """
        
        # Find recipes by name
        found_recipes = []
        for recipe in self.rag_db.recipes_db.values():
            if recipe.course_name in recipe_names:
                found_recipes.append(recipe)
        
        if not found_recipes:
            return {
                "tool": "calculate_health_metrics",
                "error": "No matching recipes found",
                "searched_names": recipe_names
            }
        
        # Calculate metrics
        fsa_scores = [r.fsa_health_score for r in found_recipes]
        who_scores = [r.who_health_score for r in found_recipes]
        
        return {
            "tool": "calculate_health_metrics",
            "recipe_count": len(found_recipes),
            "health_analysis": {
                "avg_fsa_score": sum(fsa_scores) / len(fsa_scores),
                "avg_who_score": sum(who_scores) / len(who_scores),
                "healthiest_recipe": min(found_recipes, key=lambda r: r.fsa_health_score + r.who_health_score).course_name,
                "health_distribution": {
                    "excellent": len([s for s in fsa_scores if s <= 5]),
                    "good": len([s for s in fsa_scores if 5 < s <= 8]),
                    "moderate": len([s for s in fsa_scores if s > 8])
                }
            },
            "recipes_analyzed": [
                {
                    "name": r.course_name,
                    "fsa_score": r.fsa_health_score,
                    "who_score": r.who_health_score,
                    "category": ["appetizer", "main", "dessert"][r.category]
                } for r in found_recipes
            ]
        }

class MealPlanningAgent:
    """
    AI Agent for Meal Planning
    Demonstrates AI agent patterns with reasoning chains
    """
    
    def __init__(self, rag_db: MealRecRAGDatabase, openai_api_key: Optional[str] = None):
        self.rag_db = rag_db
        self.tools = MealPlanningTools(rag_db)
        self.has_llm = openai_api_key and OPENAI_AVAILABLE
        
        if self.has_llm:
            self.client = openai.OpenAI(api_key=openai_api_key)
            print("🤖 AI Agent initialized with LLM capabilities")
        else:
            print("🤖 AI Agent initialized with rule-based reasoning")
    
    def plan_meal(self, user_request: str) -> Dict[str, Any]:
        """
        Main agent function - demonstrates reasoning chain
        
        1. Parse user request
        2. Use tools to gather information (RAG retrieval)
        3. Reason about options
        4. Generate final recommendation
        """
        
        print(f"\n🎯 Agent Processing: '{user_request}'")
        
        # Step 1: Parse request
        parsed_request = self._parse_user_request(user_request)
        print(f"📝 Parsed request: {parsed_request}")
        
        # Step 2: Use tools for information gathering (RAG)
        tool_results = self._gather_information(parsed_request)
        print(f"🔧 Tool results: Found {len(tool_results)} relevant data points")
        
        # Step 3: Reasoning (with or without LLM)
        if self.has_llm:
            recommendation = self._llm_reasoning(user_request, tool_results)
        else:
            recommendation = self._rule_based_reasoning(parsed_request, tool_results)
        
        # Step 4: Format final response
        return {
            "user_request": user_request,
            "agent_reasoning": recommendation["reasoning"],
            "recommended_recipes": recommendation["recipes"],
            "tool_calls_made": len(tool_results),
            "data_sources_used": list(set([tr["tool"] for tr in tool_results])),
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
        if "appetizer" in request_lower or "starter" in request_lower:
            parsed["categories"].append("appetizer")
        if "main" in request_lower or "dinner" in request_lower or "entree" in request_lower:
            parsed["categories"].append("main")
        if "dessert" in request_lower:
            parsed["categories"].append("dessert")
        
        # If no specific category, assume main
        if not parsed["categories"]:
            parsed["categories"] = ["main"]
        
        # Health preference
        if "very healthy" in request_lower or "super healthy" in request_lower:
            parsed["health_preference"] = "very_healthy"
        elif "healthy" in request_lower:
            parsed["health_preference"] = "healthy"
        
        # Meal type
        if "3-course" in request_lower or "multi-course" in request_lower or "full meal" in request_lower:
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
        
        # Get meal composition analysis (educational demo)
        sample_meals = list(self.rag_db.meal_course_mapping.keys())[:10]
        if sample_meals:
            composition_analysis = self.tools.get_meal_composition_analysis(sample_meals)
            tool_results.append(composition_analysis)
        
        return tool_results
    
    def _rule_based_reasoning(self, parsed_request: Dict[str, Any], tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Rule-based reasoning when LLM not available"""
        
        # Collect all recipe candidates
        all_recipes = []
        for result in tool_results:
            if "recipes" in result:
                all_recipes.extend(result["recipes"])
        
        # Select best recipes (lowest health scores)
        if parsed_request["meal_type"] == "multi_course":
            # Select best from each category
            selected = {}
            for recipe in all_recipes:
                category = recipe["category"]
                if category not in selected or recipe["fsa_score"] < selected[category]["fsa_score"]:
                    selected[category] = recipe
            final_recipes = list(selected.values())
        else:
            # Select single best recipe
            if all_recipes:
                final_recipes = [min(all_recipes, key=lambda r: r["fsa_score"] + r["who_score"])]
            else:
                final_recipes = []
        
        reasoning = f"Used rule-based selection to find {len(final_recipes)} recipes matching your {parsed_request['health_preference']} health preference"
        if parsed_request["meal_type"] == "multi_course":
            reasoning += " across multiple courses"
        
        return {
            "recipes": final_recipes,
            "reasoning": reasoning
        }
    
    def _llm_reasoning(self, user_request: str, tool_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LLM-powered reasoning (when available)"""
        
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
                        "content": "You are a meal planning AI agent. Use the provided recipe data to make recommendations. Focus on health scores (lower is better) and user preferences. Respond with a JSON object containing 'recipes' (list) and 'reasoning' (string)."
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
            # Fallback to rule-based
            return self._rule_based_reasoning({"categories": ["main"], "health_preference": "healthy", "meal_type": "single"}, tool_results)

def demo_educational_system():
    """
    Educational demo showing RAG + Tool Calls + AI Agents
    Perfect for lecture demonstration
    """
    
    print("🎓 EDUCATIONAL DEMO: RAG + Tool Calls + AI Agents")
    print("=" * 60)
    
    # Initialize system components
    print("\n1️⃣ INITIALIZING RAG DATABASE")
    rag_db = MealRecRAGDatabase()
    
    print("\n2️⃣ SETTING UP TOOL CALLS")
    tools = MealPlanningTools(rag_db)
    
    # Demo tool calls
    print("\n🔧 Demo Tool Call: search_healthy_recipes")
    tool_result = tools.search_healthy_recipes(category="main", health_preference="healthy")
    print(f"   Found: {tool_result['recipes_found']} recipes")
    print(f"   Reasoning: {tool_result['reasoning']}")
    
    print("\n3️⃣ INITIALIZING AI AGENT")
    agent = MealPlanningAgent(rag_db)
    
    print("\n4️⃣ AGENT REASONING DEMONSTRATIONS")
    
    test_queries = [
        "I want a healthy main course",
        "Give me a very healthy appetizer", 
        "Plan a 3-course healthy meal"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🤖 Agent Test {i}: '{query}'")
        print("-" * 50)
        
        result = agent.plan_meal(query)
        
        print(f"📊 Agent made {result['tool_calls_made']} tool calls")
        print(f"🔍 Retrieved {result['rag_retrieval_count']} recipes from RAG")
        print(f"💭 Reasoning: {result['agent_reasoning']}")
        print(f"🍽️  Recommended: {len(result['recommended_recipes'])} recipes")
        
        for recipe in result['recommended_recipes']:
            print(f"   - {recipe['name']} ({recipe['category']}, Health: FSA {recipe['fsa_score']}, WHO {recipe['who_score']})")

if __name__ == "__main__":
    demo_educational_system()