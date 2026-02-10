"""
Model Response Time Tester
==========================
Tests the response time of each model in the TrueSynth system.
"""

import time
from llm_system import (
    generator_llm,
    verifier_llm,
    comparer_llm,
    generator_prompt_template,
    verifier_prompt_template,
    comparer_prompt_template,
    search_tool
)

def test_model_times(query: str = "What is the capital of France?"):
    """Test response times for each model."""
    
    print("=" * 60)
    print("TrueSynth Model Response Time Test")
    print("=" * 60)
    print(f"\nTest Query: {query}\n")
    
    results = {}
    
    # Test Generator Model (Local Ollama deepseek-r1:1.5b)
    print("-" * 40)
    print("Testing Generator Model (deepseek-r1:1.5b via Ollama)...")
    if generator_llm:
        try:
            start_time = time.time()
            test_prompt = generator_prompt_template.format_messages(query=query)
            response = generator_llm.invoke(test_prompt)
            end_time = time.time()
            elapsed = end_time - start_time
            results['generator'] = {
                'time': elapsed,
                'status': 'success',
                'preview': response.content[:150] + "..." if len(response.content) > 150 else response.content
            }
            print(f"[OK] Generator: {elapsed:.2f}s")
        except Exception as e:
            results['generator'] = {'time': None, 'status': 'error', 'error': str(e)}
            print(f"[ERROR] Generator Error: {e}")
    else:
        results['generator'] = {'time': None, 'status': 'not_initialized'}
        print("[WARN] Generator not initialized")
    
    # Test Verifier Model (deepseek-r1-0528 via OpenRouter)
    print("-" * 40)
    print("Testing Verifier Model (deepseek-r1-0528 via OpenRouter)...")
    if verifier_llm:
        try:
            # Include context for verifier
            context = "France is a country in Western Europe. Paris is the capital and largest city of France."
            start_time = time.time()
            test_prompt = verifier_prompt_template.format_messages(query=query, context=context)
            response = verifier_llm.invoke(test_prompt)
            end_time = time.time()
            elapsed = end_time - start_time
            results['verifier'] = {
                'time': elapsed,
                'status': 'success',
                'preview': response.content[:150] + "..." if len(response.content) > 150 else response.content
            }
            print(f"[OK] Verifier: {elapsed:.2f}s")
        except Exception as e:
            results['verifier'] = {'time': None, 'status': 'error', 'error': str(e)}
            print(f"[ERROR] Verifier Error: {e}")
    else:
        results['verifier'] = {'time': None, 'status': 'not_initialized'}
        print("[WARN] Verifier not initialized")
    
    # Test Comparer Model (nemotron-nano-9b via OpenRouter)
    print("-" * 40)
    print("Testing Comparer Model (nemotron-nano-9b via OpenRouter)...")
    if comparer_llm:
        try:
            start_time = time.time()
            test_prompt = comparer_prompt_template.format_messages(
                query=query,
                generator_answer="The capital of France is Paris, a beautiful city known for the Eiffel Tower.",
                verifier_answer="Based on the search results, Paris is confirmed as the capital of France."
            )
            response = comparer_llm.invoke(test_prompt)
            end_time = time.time()
            elapsed = end_time - start_time
            results['comparer'] = {
                'time': elapsed,
                'status': 'success',
                'preview': response.content[:150] + "..." if len(response.content) > 150 else response.content
            }
            print(f"[OK] Comparer: {elapsed:.2f}s")
        except Exception as e:
            results['comparer'] = {'time': None, 'status': 'error', 'error': str(e)}
            print(f"[ERROR] Comparer Error: {e}")
    else:
        results['comparer'] = {'time': None, 'status': 'not_initialized'}
        print("[WARN] Comparer not initialized")
    
    # Test Search Tool
    print("-" * 40)
    print("Testing Tavily Search Tool...")
    if search_tool:
        try:
            start_time = time.time()
            search_results = search_tool.invoke(query)
            end_time = time.time()
            elapsed = end_time - start_time
            results['search'] = {
                'time': elapsed,
                'status': 'success',
                'result_count': len(search_results)
            }
            print(f"[OK] Search: {elapsed:.2f}s ({len(search_results)} results)")
        except Exception as e:
            results['search'] = {'time': None, 'status': 'error', 'error': str(e)}
            print(f"[ERROR] Search Error: {e}")
    else:
        results['search'] = {'time': None, 'status': 'not_initialized'}
        print("[WARN] Search tool not initialized")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_time = 0
    for model, data in results.items():
        if data['time']:
            total_time += data['time']
            status = f"{data['time']:.2f}s"
        else:
            status = data.get('error', data['status'])
        print(f"{model.capitalize():12} : {status}")
    
    print("-" * 40)
    print(f"{'Total':12} : {total_time:.2f}s")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    test_model_times()
