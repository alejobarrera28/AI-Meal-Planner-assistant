#!/usr/bin/env python3
"""
Simple AI Meal Planner - Educational Demo
Demonstrates RAG + Tool Calls + AI Agents in ~600 lines total

Key concepts shown:
- RAG: Real data from MealRec+ dataset
- Tool Calls: LLM calls Python functions
- AI Agents: Autonomous meal planning
"""

import os
from dotenv import load_dotenv
import json
from openai import OpenAI
from database import MealDatabase
from tools import execute_tool
from config import TOOL_SCHEMAS, SYSTEM_PROMPT


class SimpleMealPlannerBot:
    """Simple AI meal planning bot with tool calling"""

    def __init__(self, api_key: str):
        self.database = MealDatabase()
        self.client = OpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
        self.model = "Qwen/Qwen3-235B-A22B-Instruct-2507-tput"
        self.conversation = []

    def chat(self, user_message: str) -> str:
        """Main chat function - handles user input and tool calls"""

        # Add user message to conversation
        self.conversation.append({"role": "user", "content": user_message})

        # Get LLM response with tools
        response = self._get_llm_response()
        return response

    def _get_llm_response(self) -> str:
        """Get response from LLM with function calling"""
        # Add system prompt if first message
        messages = []
        if not any(msg["role"] == "system" for msg in self.conversation):
            messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.extend(self.conversation)

        # Show complete conversation
        print("\n--- CONVERSATION ---")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg['role'].upper()}")
            if msg['role'] == 'system':
                print(f"Content: {msg['content']}")
            elif msg['role'] == 'user':
                print(f"Content: {msg['content']}")
            elif msg['role'] == 'tool':
                print(f"Tool call ID: {msg['tool_call_id']}")
                print(f"Content: {msg['content']}")
            elif msg['role'] == 'assistant':
                if msg.get('content'):
                    print(f"Content: {msg['content']}")
                if msg.get('tool_calls'):
                    print(f"Tool calls: {len(msg['tool_calls'])}")
                    for j, tc in enumerate(msg['tool_calls']):
                        print(f"  Call {j+1}: {tc.function.name}({tc.function.arguments})")
            print("-" * 50)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                max_tokens=800,
                temperature=1,
            )

            response_message = response.choices[0].message
            print(f"\n--- LLM RESPONSE ---")
            print(f"Content: {response_message.content}")
            if response_message.tool_calls:
                print(f"Tool calls: {len(response_message.tool_calls)}")
                for i, tc in enumerate(response_message.tool_calls):
                    print(f"  Call {i+1}: {tc.function.name}({tc.function.arguments})")
            print("-" * 50)

            # Handle tool calls if present
            if response_message.tool_calls:
                return self._handle_tool_calls(response_message)
            else:
                # Regular text response
                content = response_message.content
                # Check if content looks like it should be a tool call but isn't parsed correctly
                if content and ("function" in str(content) or "tool" in str(content)):
                    content = "ERROR: LLM returned malformed tool call. This is a model consistency issue with function calling."
                self.conversation.append({"role": "assistant", "content": content})
                return content

        except Exception as e:
            error_msg = f"Sorry, error occurred: {e}"
            self.conversation.append({"role": "assistant", "content": error_msg})
            return error_msg

    def _handle_tool_calls(self, response_message) -> str:
        """Execute tool calls and get final response"""
        # Add assistant message with tool calls
        self.conversation.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls,
            }
        )

        # Execute each tool
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Execute tool
            try:
                result = execute_tool(self.database, tool_name, **tool_args)
                result_str = json.dumps(result, indent=2)
            except Exception as e:
                result_str = f"Error: {e}"

            # Display function output
            print(f"\n--- FUNCTION OUTPUT ---")
            print(f"Function: {tool_name}")
            print(f"Result: {result_str}")
            print("-" * 50)

            # Add tool result to conversation
            self.conversation.append(
                {"role": "tool", "tool_call_id": tool_call.id, "content": result_str}
            )

        # Get final response after tool execution
        try:
            final_response = self.client.chat.completions.create(
                model=self.model, messages=self.conversation, max_tokens=600
            )

            final_content = final_response.choices[0].message.content
            self.conversation.append({"role": "assistant", "content": final_content})
            return final_content

        except Exception as e:
            error_msg = f"Error getting response: {e}"
            self.conversation.append({"role": "assistant", "content": error_msg})
            return error_msg


def run_examples(bot):
    """Run example conversations to demonstrate capabilities"""

    examples = [
        "Find me 5 healthy appetizers",
        "Create a balanced meal plan for 2 meals",
        "Show me main courses with FSA score under 3",
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n\nEXAMPLE {i}: {example}")
        print("=" * 80)
        try:
            response = bot.chat(example)
            print(f"\nFINAL ASSISTANT RESPONSE:\n{response}")
        except Exception as e:
            print(f"\nERROR in Example {i}: {e}")
            print("This is likely due to LLM model inconsistency with function calling.")

        if i < len(examples):
            input("\nPress Enter for next example...")


def interactive_mode(bot):
    """Simple interactive chat mode"""
    print("Type your meal planning requests (or 'quit' to exit)")

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if user_input:
            response = bot.chat(user_input)
            print(f"\nAssistant: {response}")


def main():
    """Main entry point"""
    print("SIMPLE AI MEAL PLANNER")

    # Check for API key
    load_dotenv()
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("\nAPI key required!")
        return

    # Initialize bot
    bot = SimpleMealPlannerBot(api_key)

    # Database is ready

    # Choose demo mode
    print("\nChoose mode:")
    print("1. Run examples (shows key concepts)")
    print("2. Interactive chat")
    print("3. Both")

    choice = input("Choice (1-3): ").strip()

    if choice in ["1", "3"]:
        run_examples(bot)

    if choice in ["2", "3"]:
        interactive_mode(bot)

    print("\nDemo completed!")


if __name__ == "__main__":
    main()