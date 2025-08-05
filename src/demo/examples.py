"""
Example conversation demonstrations
"""


def run_example_demonstrations(chatbot):
    """Run preset example conversations"""
    print("\n💬 EXAMPLE CONVERSATIONS")
    print("=" * 50)
    
    examples = [
        "I want a healthy 3-course meal for weight loss",
        "Can you find me some very healthy appetizers?",
        "Tell me about course 12345",
        "What's in meal 674?",
        "Find me a healthier alternative to course 851"
    ]
    
    for i, query in enumerate(examples, 1):
        print(f"\n🗣️  CONVERSATION {i}")
        print("=" * 40)
        
        try:
            chatbot.chat(query)
            print(f"\n✅ Conversation {i} completed")
            
        except Exception as e:
            print(f"❌ Error in conversation {i}: {e}")
            print("   Make sure you have a valid OpenAI API key set.")
        
        # Reset conversation for next demo
        if i < len(examples):
            chatbot.reset_conversation()
            print("🔄 Conversation reset for next demo")
            input("\nPress Enter to continue...")
    
    print(f"\n✅ All {len(examples)} example conversations completed!")