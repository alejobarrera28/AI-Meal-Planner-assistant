#!/usr/bin/env python3
"""
AI Meal Planner - Main Entry Point
Educational demo of RAG + LLM Tool Calls + AI Agents using MealRec+ dataset
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to access MealRec+ dataset
sys.path.append(str(Path(__file__).parent.parent))

from data.database import MealRecRAGDatabase
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
    
    # Initialize RAG Database
    print("1️⃣ INITIALIZING RAG DATABASE")
    rag_db = MealRecRAGDatabase()
    
    # Show dataset statistics
    summary = rag_db.get_real_data_summary()
    print(f"\n📈 DATASET STATISTICS:")
    print(f"   • {summary['total_courses']:,} courses")
    print(f"   • {summary['total_meals']:,} meal compositions")
    print(f"   • {summary['user_course_interactions']:,} user interactions")
    print(f"   • Course ID range: {summary['course_id_range']}")
    print(f"   • Health scores: {'✅' if summary['health_scores_available'] else '❌'}")
    
    # Initialize Tool Registry
    print("\n2️⃣ INITIALIZING TOOL REGISTRY")
    tool_registry = ToolRegistry(rag_db)
    tools = tool_registry.list_available_tools()
    print(f"\n🔧 AVAILABLE TOOLS ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        print(f"   {i:2d}. {tool}")
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("\n❌ No OpenAI API key found!")
        print("\nOptions:")
        print("1. Set API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run tool capabilities demo (no LLM required)")
        
        choice = input("\nRun tool demo without LLM? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            demo_tool_capabilities(tool_registry)
        else:
            print("Set your API key and try again.")
        return
    
    # Initialize Chatbot
    print("\n3️⃣ INITIALIZING AI CHATBOT")
    chatbot = MealPlanningChatbot(rag_db, tool_registry, api_key)
    
    # Run demonstrations
    print("\n4️⃣ RUNNING DEMONSTRATIONS")
    choice = input("\nChoose demo mode:\n1. Example conversations\n2. Interactive mode\n3. Both\nChoice (1-3): ").strip()
    
    if choice in ['1', '3']:
        run_example_demonstrations(chatbot)
    
    if choice in ['2', '3']:
        run_interactive_demo(chatbot)
    
    print("\n👋 Demo completed!")


def demo_tool_capabilities(tool_registry):
    """Quick demo of tool capabilities without LLM"""
    print("\n🔧 TOOL CAPABILITIES DEMO (No LLM Required)")
    print("=" * 50)
    
    print("\n📋 Sample Tool Executions:")
    
    # 1. Filter courses
    print("\n1. Filter healthy main courses:")
    result = tool_registry.execute_tool("filter_courses", criteria={
        "category": "main",
        "max_fsa_score": 6.0,
        "limit": 3
    })
    if "courses" in result:
        print(f"   Found {len(result['courses'])} courses")
        for course in result['courses'][:2]:
            print(f"   - {course['course_name']} (FSA: {course['fsa_score']})")
    
    # 2. Generate meal plan
    print("\n2. Generate weight loss meal plan:")
    result = tool_registry.execute_tool("generate_meal_plan", goal={
        "health_focus": "weight_loss"
    })
    if "meal_plan" in result:
        print(f"   Created {result['courses_included']}-course meal")
        print(f"   Average FSA score: {result['average_fsa_score']}")
    
    # 3. Tool registry info
    print(f"\n3. Tool registry statistics:")
    print(f"   Available tools: {len(tool_registry.list_available_tools())}")
    print(f"   Registry functional: {'✅' if tool_registry.has_tool('filter_courses') else '❌'}")
    
    print("\n✅ Tool capabilities demonstrated!")


if __name__ == "__main__":
    main()