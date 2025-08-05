#!/usr/bin/env python3
"""
Educational Demo: RAG + Tool Calls + AI Agents
Perfect for lecture demonstration using real MealRec+ dataset
"""

import os
import sys
from rag_database import MealRecRAGDatabase
from tools import MealPlanningTools
from agent import MealPlanningAgent


def demo_educational_system(openai_api_key: str):
    """
    Educational demo showing RAG + Tool Calls + AI Agents

    Args:
        openai_api_key: Required OpenAI API key for LLM functionality
    """

    print("🎓 EDUCATIONAL DEMO: RAG + Tool Calls + AI Agents")
    print("=" * 60)

    # 1. Initialize RAG Database
    print("\n1️⃣ INITIALIZING RAG DATABASE")
    rag_db = MealRecRAGDatabase()

    # Show real data statistics
    summary = rag_db.get_real_data_summary()
    print(f"\n📈 REAL DATA STATISTICS:")
    print(f"   • {summary['total_courses']:,} real courses from MealRec+ dataset")
    print(f"   • {summary['total_meals']:,} real meal compositions")
    print(f"   • {summary['user_course_interactions']:,} user-course interactions")
    print(f"   • {summary['user_meal_train']:,} training interactions")
    print(f"   • Course ID range: {summary['course_id_range']}")
    print(
        f"   • Real health scores: {'✅' if summary['health_scores_available'] else '❌'}"
    )
    print(
        f"   • Course metadata: {'✅' if summary['has_course_metadata'] else '❌ Not available'}"
    )

    # 2. Setup Tool Calls
    print("\n2️⃣ SETTING UP TOOL CALLS")
    tools = MealPlanningTools(rag_db)

    # Demo tool call
    print("\n🔧 Demo Tool Call: search_healthy_recipes")
    tool_result = tools.search_healthy_recipes(
        category="main", health_preference="healthy"
    )
    print(f"   Found: {tool_result['recipes_found']} recipes")
    print(f"   Reasoning: {tool_result['reasoning']}")

    # 3. Initialize AI Agent
    print("\n3️⃣ INITIALIZING AI AGENT")
    agent = MealPlanningAgent(rag_db, openai_api_key)

    # 4. Agent Reasoning Demonstrations
    print("\n4️⃣ AGENT REASONING DEMONSTRATIONS")

    test_queries = [
        "I want a healthy main course",
        "Give me a very healthy appetizer",
        "Plan a 3-course healthy meal",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🤖 Agent Test {i}: '{query}'")
        print("-" * 50)

        try:
            result = agent.plan_meal(query)

            print(f"📊 Agent made {result['tool_calls_made']} tool calls")
            print(f"🔍 Retrieved {result['rag_retrieval_count']} recipes from RAG")
            print(f"💭 Reasoning: {result['agent_reasoning']}")
            print(f"🍽️  Recommended: {len(result['recommended_recipes'])} recipes")

            for recipe in result["recommended_recipes"]:
                print(f"   - {recipe}")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("   Make sure you have a valid OpenAI API key set.")


def main():
    """Main entry point"""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API key required!")
        print("Set your API key: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    demo_educational_system(api_key)


if __name__ == "__main__":
    main()
