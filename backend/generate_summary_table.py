import pandas as pd
import os

# Configuration
# CSV_FILE = "./results/benchmark_run_20260211_201027.csv"
CSV_FILE = "C:/Users/nullc/Desktop/TrueSynth/backend/results/benchmark_run_20260211_201027.csv"
OUTPUT_FILE = "C:/Users/nullc/Desktop/TrueSynth/backend/results/summary_table.md"

def generate_summary():
    if not os.path.exists(CSV_FILE):
        print(f"Error: CSV file not found at {CSV_FILE}")
        return

    try:
        df = pd.read_csv(CSV_FILE)
        
        # Calculate metrics
        avg_score = df['Score'].mean()
        # count "True" strings or boolean Trues
        hallucination_count = df['Hallucination'].apply(lambda x: str(x).lower() == 'true').sum()
        hallucination_rate = (hallucination_count / len(df)) * 100
        avg_time = df['Time (s)'].mean()
        
        markdown_content = f"# Benchmark Results\n\n"
        markdown_content += f"- **Samples**: {len(df)}\n"
        markdown_content += f"- **Avg Score**: {avg_score:.2f}/10\n"
        markdown_content += f"- **Hallucination Rate**: {hallucination_rate:.2f}%\n"
        markdown_content += f"- **Avg Time**: {avg_time:.2f}s\n\n"
        markdown_content += "## Detailed Results Table\n\n"
        # Truncate System Answer for better readability in table
        df_display = df.copy()
        df_display['System Answer'] = df_display['System Answer'].apply(lambda x: (str(x)[:100] + '...') if len(str(x)) > 100 else str(x))
        
        markdown_content += df_display[['Question', 'System Answer', 'Score', 'Hallucination']].to_markdown(index=False)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        print(f"Summary table saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error generating summary: {e}")

if __name__ == "__main__":
    generate_summary()
