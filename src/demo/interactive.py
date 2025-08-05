"""
Interactive chatbot demonstration
"""


def run_interactive_demo(chatbot):
    """Run interactive chatbot session"""
    print("\n🗣️  INTERACTIVE MODE")
    print("=" * 50)
    print("Chat with the AI Meal Planning Assistant!")
    print("\nCommands:")
    print("  - Type your meal planning questions")
    print("  - Type 'quit' to exit")
    print("  - Type 'reset' to clear conversation history")
    
    chatbot.reset_conversation()  # Fresh start
    
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