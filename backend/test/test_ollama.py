#!/usr/bin/env python3
"""
Test script for Llama 3.2 model using Ollama
This script tests various capabilities of the llama3.2:latest model
"""

import requests
import json
import time

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:latest"

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✓ Ollama is running")
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            if MODEL_NAME in model_names:
                print(f"✓ {MODEL_NAME} is available")
                return True
            else:
                print(f"✗ {MODEL_NAME} not found. Available models: {model_names}")
                return False
        else:
            print("✗ Ollama is not responding properly")
            return False
    except Exception as e:
        print(f"✗ Error connecting to Ollama: {e}")
        print("  Make sure Ollama is running (try: ollama serve)")
        return False

def generate_response(prompt, stream=False):
    """Generate a response from the Llama model"""
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": stream
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=data, stream=stream)
        
        if stream:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        full_response += json_response['response']
                        print(json_response['response'], end='', flush=True)
            print()  # New line after streaming
            return full_response
        else:
            result = response.json()
            return result.get('response', '')
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

def run_tests():
    """Run a series of tests on the Llama model"""
    
    print("\n" + "="*60)
    print("LLAMA 3.2 MODEL TESTS")
    print("="*60 + "\n")
    
    # Check connection first
    if not test_ollama_connection():
        return
    
    tests = [
        {
            "name": "Basic Question Answering",
            "prompt": "What is the capital of France?",
        },
        {
            "name": "Mathematical Reasoning",
            "prompt": "If a train travels 120 km in 2 hours, what is its average speed?",
        },
        {
            "name": "Code Generation",
            "prompt": "Write a Python function to calculate the factorial of a number.",
        },
        {
            "name": "Creative Writing",
            "prompt": "Write a haiku about artificial intelligence.",
        },
        {
            "name": "Logical Reasoning",
            "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude that some roses fade quickly?",
        },
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*60}")
        print(f"Prompt: {test['prompt']}\n")
        
        start_time = time.time()
        response = generate_response(test['prompt'], stream=True)
        end_time = time.time()
        
        if response:
            print(f"\n⏱️  Time taken: {end_time - start_time:.2f} seconds")
            print(f"📝 Response length: {len(response)} characters")
        else:
            print("✗ Failed to get response")
    
    print("\n" + "="*60)
    print("TESTS COMPLETED")
    print("="*60 + "\n")

def interactive_mode():
    """Run interactive chat with the model"""
    print("\n" + "="*60)
    print("INTERACTIVE MODE")
    print("="*60)
    print("Type 'exit' or 'quit' to end the session\n")
    
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            print("\nLlama: ", end='', flush=True)
            generate_response(user_input, stream=True)
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        if test_ollama_connection():
            interactive_mode()
    else:
        run_tests()
        
        print("\nTo run in interactive mode, use: python test_llama3.2.py --interactive")