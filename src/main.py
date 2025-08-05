#!/usr/bin/env python3
"""
AI Meal Planner - Main Entry Point
Educational demo of RAG + LLM Tool Calls + AI Agents using MealRec+ dataset
"""

import os
import sys
from pathlib import Path

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, continue with regular env vars
    pass

# Add parent directory to path to access MealRec+ dataset
sys.path.append(str(Path(__file__).parent.parent))

from data.database import MealDatabase
from tools.registry import ToolRegistry
from core.chatbot import MealPlanningChatbot
from demo.interactive import run_interactive_demo
from demo.examples import run_example_demonstrations


def main():
    """Main entry point"""
    print("🎓 AI MEAL PLANNER - Educational Demo")
    print("=" * 50)
    print("Demonstrating: RAG + LLM Tool Calls + AI Agents")
    print("Dataset: MealRec+ (Educational subset)")
    print()
    
    # Initialize Meal Database
    print("1️⃣ INITIALIZING MEAL DATABASE")
    meal_db = MealDatabase()
    
    # Show dataset statistics
    summary = meal_db.get_real_data_summary()
    print(f"\n📈 DATASET STATISTICS:")
    print(f"   • {summary['total_courses']:,} courses")
    print(f"   • {summary['total_meals']:,} meal compositions")
    print(f"   • {summary['user_course_interactions']:,} user interactions")
    print(f"   • Course ID range: {summary['course_id_range']}")
    print(f"   • Health scores: {'✅' if summary['health_scores_available'] else '❌'}")
    
    # Initialize Tool Registry
    print("\n2️⃣ INITIALIZING TOOL REGISTRY")
    tool_registry = ToolRegistry(meal_db)
    tools = tool_registry.list_available_tools()
    print(f"\n🔧 AVAILABLE TOOLS ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"   {i:2d}. {tool}")
    
    # Check for Together.ai API key
    api_key = os.getenv("TOGETHER_API_KEY")
    
    if not api_key:
        print("\n❌ No Together.ai API key found!")
        print("Set environment variable: export TOGETHER_API_KEY='your-key-here'")
        print("Or create a .env file with: TOGETHER_API_KEY=your-key-here")
        return
    
    # Initialize Chatbot
    print("\n3️⃣ INITIALIZING AI CHATBOT")
    chatbot = MealPlanningChatbot(meal_db, tool_registry, api_key)
    
    # Run demonstrations
    print("\n4️⃣ RUNNING DEMONSTRATIONS")
    choice = input("\nChoose demo mode:\n1. Example conversations\n2. Interactive mode\n3. Both\nChoice (1-3): ").strip()
    
    if choice in ['1', '3']:
        run_example_demonstrations(chatbot)
    
    if choice in ['2', '3']:
        run_interactive_demo(chatbot)
    
    print("\n👋 Demo completed!")



if __name__ == "__main__":
    main()