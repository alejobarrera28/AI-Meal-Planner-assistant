#!/usr/bin/env python3
"""
Educational Demo: LLM Function Calling Chatbot
Perfect for lecture demonstration using real MealRec+ dataset with true function calling
"""

import os
import sys
from rag_database import MealRecRAGDatabase
from tools import MealPlanningTools
from agent import MealPlanningChatbot


def demo_chatbot_system(openai_api_key: str):
    """
    Educational demo showing LLM Function Calling Chatbot

    Args:
        openai_api_key: Required OpenAI API key for LLM functionality
    """

    print("🎓 EDUCATIONAL DEMO: LLM Function Calling Chatbot")
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

    # 2. Initialize Function Calling Chatbot
    print("\n2️⃣ INITIALIZING FUNCTION CALLING CHATBOT")
    chatbot = MealPlanningChatbot(rag_db, openai_api_key)

    # Show available tools
    print(f"\n🔧 AVAILABLE TOOLS FOR LLM:")
    tool_names = [
        "filter_courses", "generate_meal_plan", "calculate_health_score",
        "get_user_history", "swap_for_healthier", "summarize_recipe",
        "search_courses_by_category", "find_healthy_courses", 
        "get_meal_composition", "recommend_similar_meals"
    ]
    for i, tool in enumerate(tool_names, 1):
        print(f"   {i:2d}. {tool}")

    # 3. Demonstrate Conversational Function Calling
    print("\n3️⃣ CHATBOT CONVERSATIONS WITH FUNCTION CALLING")

    demo_conversations = [
        "I want a healthy 3-course meal for weight loss",
        "Can you find me some very healthy appetizers?",
        "Tell me about course 12345",
        "What's in meal 674?",
        "Find me a healthier alternative to course 851"
    ]

    for i, query in enumerate(demo_conversations, 1):
        print(f"\n🗣️  CONVERSATION {i}")
        print("=" * 50)
        
        try:
            chatbot.chat(query)
            print(f"\n✅ Conversation completed successfully")
            
        except Exception as e:
            print(f"❌ Error in conversation: {e}")
            print("   Make sure you have a valid OpenAI API key set.")
        
        # Reset conversation for next demo
        if i < len(demo_conversations):
            chatbot.reset_conversation()
            print("🔄 Conversation reset for next demo\n")

    # 4. Interactive Mode (Optional)
    print("\n4️⃣ INTERACTIVE MODE")
    print("You can now chat with the meal planning assistant!")
    print("Available commands:")
    print("  - Type your meal planning questions")
    print("  - Type 'quit' to exit")
    print("  - Type 'reset' to clear conversation history")
    
    chatbot.reset_conversation()  # Fresh start for interactive mode
    
    try:
        while True:
            print("\n" + "-" * 50)
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                chatbot.reset_conversation()
                continue
            elif not user_input:
                continue
                
            try:
                chatbot.chat(user_input)
                # Response already printed by chatbot
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


def demo_tool_capabilities():
    """Quick demo of tool capabilities without LLM"""
    print("\n🔧 TOOL CAPABILITIES DEMO (No LLM Required)")
    print("=" * 50)
    
    # Initialize just the RAG database and tools
    rag_db = MealRecRAGDatabase()
    tools = MealPlanningTools(rag_db)
    
    print("\n📋 Sample Tool Calls:")
    
    # 1. Filter courses
    print("\n1. Filter healthy main courses:")
    result = tools.filter_courses({
        "category": "main",
        "max_fsa_score": 6.0,
        "limit": 3
    })
    print(f"   Found {len(result['courses'])} courses")
    for course in result['courses'][:2]:
        print(f"   - {course['course_name']} (FSA: {course['fsa_score']})")
    
    # 2. Generate meal plan
    print("\n2. Generate weight loss meal plan:")
    result = tools.generate_meal_plan({
        "health_focus": "weight_loss"
    })
    print(f"   Created {result['courses_included']}-course meal")
    print(f"   Average FSA score: {result['average_fsa_score']}")
    
    # 3. Get meal composition
    print("\n3. Analyze meal composition:")
    first_meal_id = list(rag_db.meal_course_mapping.keys())[0]
    result = tools.get_meal_composition(first_meal_id)
    print(f"   Meal {first_meal_id} has {result['course_count']} courses")
    print(f"   Average health score: {result['average_scores']['fsa']}")
    
    print("\n✅ Tool capabilities demonstrated!")


def main():
    """Main entry point"""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No OpenAI API key found!")
        print("\nYou can either:")
        print("1. Set API key: export OPENAI_API_KEY='your-key-here'")
        print("2. Run tool demo only (no LLM required)")
        
        choice = input("\nRun tool demo without LLM? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            demo_tool_capabilities()
        else:
            print("Set your API key and try again.")
        sys.exit(1)
    
    print("🔑 OpenAI API key found - running full chatbot demo")
    demo_chatbot_system(api_key)


if __name__ == "__main__":
    main()