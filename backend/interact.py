import os
import sys
import asyncio
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_system import (
    generator_llm,
    verifier_llm,
    comparer_llm,
    search_tool,
    generator_prompt_template,
    verifier_prompt_template,
    comparer_prompt_template
)

# Load environment variables
load_dotenv()

def print_separator():
    print("\n" + "="*50 + "\n")

def get_multiline_input(prompt_text):
    print(prompt_text + " (Press Ctrl+D or Ctrl+Z on new line to finish):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    return "\n".join(lines)

def interact_with_model(model_name, model, prompt_template=None):
    if not model:
        print(f"❌ {model_name} is not initialized. Please check your API keys.")
        return

    print(f"\n🔵 Starting interaction with {model_name}.")
    print("Type 'exit' to go back to the main menu.")
    
    while True:
        user_input = input(f"\n[{model_name}] Enter prompt: ").strip()
        
        if user_input.lower() in ('exit', 'quit'):
            break
        
        if not user_input:
            continue

        try:
            print(f"⏳ {model_name} is thinking...")
            
            # Decide whether to use the prompt template or raw input
            # For simplicity in "raw" interaction, we'll try to just invoke the model
            # However, prompt templates set the system persona.
            
            msg = None
            if prompt_template:
                # If it's a ChatPromptTemplate, we can format it
                # But templates often expect specific variables (like 'query' or 'context')
                # Let's try to detect variables
                input_vars = prompt_template.input_variables
                
                # Special handling based on known templates in llm_system.py
                if model_name == "Generator":
                    msg = prompt_template.format_messages(query=user_input)
                elif model_name == "Verifier":
                    # Verifier usually needs context. 
                    # We can ask for context or just provide a placeholder/skip.
                    # Let's verify if we want to search first.
                    print("Options: [1] Just Chat  [2] Search & Verify")
                    sub_choice = input("Choice (default 1): ").strip()
                    
                    if sub_choice == "2":
                        if search_tool:
                            print("🔍 Searching Tavily...")
                            search_results = search_tool.invoke(user_input)
                            from llm_system import format_search_results
                            context = format_search_results(search_results)
                            print(f"✅ Found context ({len(search_results)} results)")
                            msg = prompt_template.format_messages(query=user_input, context=context)
                        else:
                            print("❌ Search tool not available. Using raw chat.")
                            msg = [("human", user_input)]
                    else:
                        # Raw chat, but verifier template expects 'context'
                        # We'll use a dummy context or just bypass template
                        # Bypassing template is safer for "raw" chat
                         msg = [("human", user_input)]

                elif model_name == "Comparer":
                    # Comparer expects generator_answer and verifier_answer
                    # This is complex to mock. We'll just bypass template for raw interaction.
                    msg = [("human", user_input)]
                else:
                     msg = [("human", user_input)]
            else:
                msg = [("human", user_input)]
            
            # Invoke model
            response = model.invoke(msg)
            
            print_separator()
            if hasattr(response, 'content'):
                print(response.content)
            else:
                print(response)
            print_separator()

        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    while True:
        print_separator()
        print("🤖 Multi-LLM Interactive Terminal")
        print("1. Interact with Generator (Creative)")
        print("2. Interact with Verifier (Factual/Search)")
        print("3. Interact with Comparer (Synthesis)")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ").strip()
        
        if choice == '1':
            interact_with_model("Generator", generator_llm, generator_prompt_template)
        elif choice == '2':
            interact_with_model("Verifier", verifier_llm, verifier_prompt_template)
        elif choice == '3':
            interact_with_model("Comparer", comparer_llm, comparer_prompt_template)
        elif choice == '4':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
