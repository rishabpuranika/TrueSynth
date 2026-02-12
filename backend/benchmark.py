"""
Benchmark Script for TrueSynth
==============================
Evaluates the system against the TruthfulQA dataset.
"""

import pandas as pd
import os
import time
import asyncio
from datetime import datetime
from tqdm import tqdm
from llm_system import run_hallucination_reduction_system
from judge_utils import evaluate_answer
import random

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "../TruthfulQA/TruthfulQA.csv")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SAMPLE_SIZE = 1  # Number of questions to evaluate

def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at {path}")
    return pd.read_csv(path)

def run_benchmark():
    print(f"Loading dataset from {DATASET_PATH}...")
    df = load_dataset(DATASET_PATH)
    
    # Select random sample
    # Random state for reproducibility
    sample_df = df.sample(n=SAMPLE_SIZE, random_state=42)
    
    print(f"Selected {SAMPLE_SIZE} questions for evaluation.")
    
    results = []
    
    # Create results directory if it doesn't exist
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\nStarting evaluation...")
    print("=" * 60)
    
    for index, row in tqdm(sample_df.iterrows(), total=SAMPLE_SIZE):
        question = row['Question']
        best_answer = row['Best Answer']
        correct_answers = row['Correct Answers']
        category = row['Category']
        
        # Run System
        start_time = time.time()
        try:
            # Note: The system prompt has been updated to not mention "Verifier" etc.
            result_payload = run_hallucination_reduction_system(question, verbose=False)
            
            scores = {}
            if isinstance(result_payload, dict):
                final_answer = result_payload.get("answer", "")
                scores = result_payload.get("scores", {})
            else:
                final_answer = str(result_payload)
        except Exception as e:
            final_answer = f"Error: {str(e)}"
            scores = {}
        end_time = time.time()
        processing_time = end_time - start_time

        # Rate limit mitigation
        time.sleep(5)

        
        # Evaluate Result
        eval_result = evaluate_answer(question, final_answer, best_answer, correct_answers)
        
        # Compute Text Metrics
        from judge_utils import compute_text_metrics, compute_soft_metrics
        f1, prec, rec = compute_text_metrics(final_answer, best_answer)
        soft_rec, soft_prec, inclusion = compute_soft_metrics(final_answer, best_answer)
        
        # Get LLM-reported scores (may be 0 if model didn't output them)
        llm_factual = scores.get("Factual Accuracy", 0)
        llm_trust = scores.get("Final Trust", 0)
        
        judge_score = eval_result['score']
        hallucination = eval_result['hallucination']
        
        # Compute Factual Accuracy fallback from judge score when LLM didn't report it
        if llm_factual == 0 and judge_score > 0:
            factual_accuracy = (judge_score / 10.0) * 100
            if hallucination:
                factual_accuracy *= 0.5
        else:
            factual_accuracy = llm_factual
        
        # Compute Final Trust as weighted composite when LLM didn't report it
        if llm_trust == 0 and judge_score > 0:
            final_trust = (
                0.40 * (judge_score / 10.0 * 100) +
                0.30 * factual_accuracy +
                0.20 * (soft_rec * 100) +
                0.10 * (inclusion * 100)
            )
            if hallucination:
                final_trust *= 0.5
        else:
            final_trust = llm_trust
        
        result_entry = {
            "Question": question,
            "Category": category,
            "System Answer": final_answer,
            "Best Answer": best_answer,
            "Score": judge_score,
            "Hallucination": hallucination,
            "Reasoning": eval_result['reasoning'],
            "Time (s)": round(processing_time, 2),
            "Confidence": scores.get("Confidence", 0),
            "Factual Accuracy": round(factual_accuracy, 2),
            "Hallucination Score": scores.get("Hallucination Score", 0),
            "Agreement": scores.get("Agreement", 0),
            "Final Trust": round(final_trust, 2),
            "F1 Score": round(f1, 2),
            "Precision": round(prec, 2),
            "Recall": round(rec, 2),
            "Soft Recall": round(soft_rec, 2),
            "Soft Precision": round(soft_prec, 2),
            "Inclusion Score": round(inclusion, 2)
        }
        
        results.append(result_entry)
        
        # Save intermediate results
        pd.DataFrame(results).to_csv(f"{RESULTS_DIR}/benchmark_partial_{timestamp}.csv", index=False)
        
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Calculate Metrics
    avg_score = results_df['Score'].mean()
    hallucination_rate = (results_df['Hallucination'].sum() / len(results_df)) * 100
    avg_time = results_df['Time (s)'].mean()
    
    # Calculate averages for new metrics
    avg_conf = results_df['Confidence'].mean()
    avg_fact = results_df['Factual Accuracy'].mean()
    avg_trust = results_df['Final Trust'].mean()
    avg_prec = results_df['Precision'].mean()
    avg_rec = results_df['Recall'].mean()
    avg_f1 = results_df['F1 Score'].mean()
    avg_soft_rec = results_df['Soft Recall'].mean()
    avg_soft_prec = results_df['Soft Precision'].mean()
    avg_inclusion = results_df['Inclusion Score'].mean()
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETION SUMMARY")
    print("=" * 60)
    print("KEY RESEARCH METRICS:")
    print(f"1. Judge Score (Quality):      {avg_score:.2f} / 10")
    print(f"2. Hallucination Rate:         {hallucination_rate:.2f}%")
    print(f"3. Factual Accuracy:           {avg_fact:.2f} / 100")
    print(f"4. Soft Recall (Semantic):     {avg_soft_rec:.2f}")
    print(f"5. Final Trust Score:          {avg_trust:.2f} / 100")
    print("-" * 30)
    print(f"Samples: {SAMPLE_SIZE}")
    print(f"Average Processing Time: {avg_time:.2f}s")
    print("-" * 30)
    print("OTHER METRICS:")
    print(f"Avg Precision: {avg_prec:.2f}")
    print(f"Avg Recall: {avg_rec:.2f}")
    print(f"Avg F1 Score: {avg_f1:.2f}")
    print(f"Avg Inclusion Score: {avg_inclusion:.2f}")
    print("=" * 60)
    
    # Save Final CSV
    csv_filename = f"{RESULTS_DIR}/benchmark_run_{timestamp}.csv"
    results_df.to_csv(csv_filename, index=False)
    print(f"Detailed results saved to {csv_filename}")
    
    # Generate Markdown Summary
    md_filename = f"{RESULTS_DIR}/summary_table.md"
    
    # Truncate System Answer for better readability in table
    df_display = results_df.copy()
    df_display['System Answer'] = df_display['System Answer'].apply(lambda x: (str(x).replace('\n', ' ')[:100] + '...') if len(str(x)) > 100 else str(x).replace('\n', ' '))
    
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(f"# Benchmark Results ({timestamp})\n\n")
        f.write("## Key Research Metrics\n")
        f.write(f"1. **Judge Score**: {avg_score:.2f}/10\n")
        f.write(f"2. **Hallucination Rate**: {hallucination_rate:.2f}%\n")
        f.write(f"3. **Factual Accuracy**: {avg_fact:.2f}/100\n")
        f.write(f"4. **Soft Recall**: {avg_soft_rec:.2f}\n")
        f.write(f"5. **Final Trust**: {avg_trust:.2f}/100\n\n")
        
        f.write("## Other Details\n")
        f.write(f"- **Samples**: {SAMPLE_SIZE}\n")
        f.write(f"- **Avg Time**: {avg_time:.2f}s\n")
        f.write(f"- **Inclusion Score**: {avg_inclusion:.2f}\n")
        f.write(f"- **Legacy F1**: {avg_f1:.2f}\n\n")
        
        f.write("## Detailed Results Table\n\n")
        columns_to_show = ['Question', 'System Answer', 'Score', 'Factual Accuracy', 'Final Trust', 'Soft Recall', 'Hallucination']
        f.write(df_display[columns_to_show].to_markdown(index=False))
        
    print(f"Summary table saved to {md_filename}")

if __name__ == "__main__":
    run_benchmark()
