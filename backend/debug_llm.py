import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from llm_system import run_hallucination_reduction_system

print("Running system...")
result = run_hallucination_reduction_system("Which language do all people in Europe speak?", verbose=True)

print("\n--- FINAL ANSWER ---")
print(result["answer"])

print("\n--- SCORES ---")
print(result["scores"])

print("\n--- DEBUG INFO ---")
print("Generator Raw:")
print(result["debug"]["generator_raw"])
print("\nVerifier Raw:")
print(result["debug"]["verifier_raw"])
