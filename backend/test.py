"""
Multi-LLM Hallucination Reduction System with OpenRouter
=========================================================
A sophisticated system that uses multiple Large Language Models via OpenRouter in a 
"Generate, Verify, Compare" architecture to reduce hallucinations in AI-generated answers.

Required Environment Variables:
- TAVILY_API_KEY: Your Tavily Search API key
- OPENROUTER_API_KEY: Your OpenRouter API key

Install required packages:
pip install langchain langchain-community langchain-openai tavily-python python-dotenv
"""

import os
import time
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

# Optional: Uncomment to use .env file
import dotenv
dotenv.load_dotenv()

# ===========================
# CONFIGURATION SECTION
# ===========================

# Set up API keys from environment variables
print("Checking for required API keys...")

# Required API keys
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    print("WARNING: TAVILY_API_KEY not found in environment variables")
    print("Set it using: export TAVILY_API_KEY='your-key-here'")

openrouter_api_key = os.getenv("OPENROUTER_API_KEY1")
openrouter_api_key1=os.getenv("OPENROUTER_API_KEY2")
openrouter_api_key2=os.getenv("OPENROUTER_API_KEY3")
if not openrouter_api_key:
    print("WARNING: OPENROUTER_API_KEY not found in environment variables")
    print("Set it using: export OPENROUTER_API_KEY='your-key-here'")

# ===========================
# MODEL INITIALIZATION
# ===========================

# Base URL for OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Generator Model - Creative but potentially hallucinatory
# Using X.AI's Grok model via OpenRouter
generator_llm = ChatOpenAI(
    model="meta-llama/llama-3.3-8b-instruct:free",
    temperature=0.7,  # Higher temperature for more creative responses
    openai_api_base=OPENROUTER_BASE_URL,
    openai_api_key=openrouter_api_key,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",  # Optional, for OpenRouter tracking
        "X-Title": "Multi-LLM Hallucination Reduction System"  # Optional, for OpenRouter tracking
    }
)

# Verifier Model - Grounded and factual
# Using DeepSeek model via OpenRouter for fact-checking
verifier_llm = ChatOpenAI(
    model="deepseek/deepseek-r1:free",
    temperature=0.2,  # Lower temperature for more factual responses
    openai_api_base=OPENROUTER_BASE_URL,
    openai_api_key=openrouter_api_key1,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Multi-LLM Hallucination Reduction System"
    }
)

# Comparer Model - Critical reasoner and synthesizer
# Using Qwen Coder model via OpenRouter for synthesis
comparer_llm = ChatOpenAI(
    model="nvidia/nemotron-nano-9b-v2:free",
    temperature=0.2,  # Low temperature for consistent synthesis
    openai_api_base=OPENROUTER_BASE_URL,
    openai_api_key=openrouter_api_key2,
    default_headers={
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Multi-LLM Hallucination Reduction System"
    }
)

# ===========================
# SEARCH TOOL INITIALIZATION
# ===========================

# Initialize Tavily search tool for retrieving real-world, up-to-date information
try:
    search_tool = TavilySearchResults(
        api_key=tavily_api_key,
        max_results=5,  # Retrieve top 5 search results for comprehensive context
        search_depth="advanced",  # Use advanced search for better results
        include_answer=True,  # Include direct answer if available
        include_raw_content=False,  # Don't include raw HTML
    )
    print(f"✅ Tavily Search Tool initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Tavily Search Tool: {e}")
    search_tool = None

# ===========================
# PROMPT TEMPLATES
# ===========================

# Generator Prompt Template
# Simple prompt for initial answer generation
generator_prompt_template = ChatPromptTemplate.from_template(
    """You are a helpful AI assistant. Please answer the following query to the best of your ability:

Query: {query}

Answer:"""
)

# Verifier Prompt Template
# Strict prompt that enforces grounding in search results only
verifier_prompt_template = ChatPromptTemplate.from_template(
    """You are a factual assistant. Answer the following user query based ONLY on the provided search results context. Do not use any of your internal knowledge. If the context does not contain the answer, state that you cannot answer based on the information provided.

Context:
{context}

Query: {query}"""
)

# Comparer Prompt Template
# Comprehensive prompt for comparing and synthesizing answers
comparer_prompt_template = ChatPromptTemplate.from_template(
    """You are a meticulous fact-checking and synthesis agent. Your goal is to produce the most accurate and reliable answer to the user's query by comparing two different AI-generated answers.

Original Query: {query}

---

Generator Model (creative but potentially unreliable):
{generator_answer}

---

Verifier Model (grounded in web search results):
{verifier_answer}

---

INSTRUCTIONS:
1.  Carefully compare the 'Generator Model' answer against the 'Verifier Model' answer.
2.  Identify any statements in the 'Generator Model' answer that are not supported by the facts in the 'Verifier Model' answer.
3.  Synthesize a final, comprehensive answer that corrects any inaccuracies or hallucinations from the 'Generator Model' using the factual information from the 'Verifier Model'.
4.  If the 'Verifier Model' provides more relevant or up-to-date information, prioritize it.
5.  **FORMATTING:** Use Markdown to make the answer highly readable.
    -   Use **bold** for key terms.
    -   Use bullet points or numbered lists for steps or lists.
    -   Use `#` Headers to organize sections.
6.  Present only the final, synthesized answer. Do not explain your reasoning process unless the query asks for it.

Final Corrected Answer:"""
)

# ===========================
# UTILITY FUNCTIONS
# ===========================

def format_search_results(results: List[Dict]) -> str:
    """
    Format search results into a readable context string.
    
    Args:
        results: List of search result dictionaries from Tavily
    
    Returns:
        Formatted string containing search results
    """
    if not results:
        return "No search results found."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        # Extract relevant fields from search result
        content = result.get('content', 'No content available')
        url = result.get('url', 'No URL')
        title = result.get('title', 'No title')
        
        formatted_results.append(
            f"Result {i}:\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Content: {content}\n"
        )
    
    return "\n".join(formatted_results)

def search_and_format(query: str) -> Dict[str, str]:
    """
    Search for information and format the results.
    
    Args:
        query: The search query
    
    Returns:
        Dictionary with query and formatted context
    """
    if search_tool is None:
        print("⚠️  Search tool not initialized. Using fallback context.")
        return {
            "query": query,
            "context": "Search functionality is not available. Please verify your Tavily API key."
        }
    
    try:
        print(f"🔍 Searching for: {query}")
        # Perform search
        search_results = search_tool.invoke(query)
        print(f"✅ Found {len(search_results)} search results")
        
        # Format results
        context = format_search_results(search_results)
        
        return {
            "query": query,
            "context": context
        }
    except Exception as e:
        print(f"❌ Search error: {e}")
        print(f"   Query was: {query}")
        return {
            "query": query,
            "context": f"Error performing search: {str(e)}. No context available."
        }

# ===========================
# COMPONENT CHAINS
# ===========================

# Component 1: Generator Chain
# Generates an initial, potentially creative but unverified answer using Grok
generator_chain = (
    {"query": RunnablePassthrough()}
    | generator_prompt_template
    | generator_llm
    | StrOutputParser()
)

# Component 2: Verifier Chain
# Searches for factual information and generates a grounded answer using DeepSeek

# Create a runnable lambda for search and format
search_runnable = RunnableLambda(search_and_format)

# Verifier chain that uses search results to generate grounded answer
verifier_chain = (
    search_runnable
    | verifier_prompt_template
    | verifier_llm
    | StrOutputParser()
)

# Component 3: Comparer Chain
# Compares and synthesizes the two answers to produce final output using Qwen
comparer_chain = (
    comparer_prompt_template
    | comparer_llm
    | StrOutputParser()
)

# ===========================
# MAIN SYSTEM CHAIN (LCEL)
# ===========================

# Complete system chain using LangChain Expression Language
# This orchestrates the entire "Generate, Verify, Compare" flow
complete_system = (
    # Step 1: Run Generator and Verifier in parallel
    RunnableParallel(
        query=RunnablePassthrough(),
        generator_answer=generator_chain,
        verifier_answer=verifier_chain,
    )
    # Step 2: Pass all results to the Comparer
    | comparer_chain
)

# ===========================
# MAIN UTILITY FUNCTION
# ===========================

def run_hallucination_reduction_system(query: str, verbose: bool = True) -> str:
    """
    Run the complete hallucination reduction system on a given query.
    
    Args:
        query: The user's question or query
        verbose: If True, print intermediate results for debugging
    
    Returns:
        The final, fact-checked and synthesized answer
    """
    if verbose:
        print("="*80)
        print(f"QUERY: {query}")
        print("="*80)
        
        # Run generator independently for verbose output
        print("\n[1] GENERATOR OUTPUT (Grok-4-fast):")
        print("-"*40)
        try:
            generator_result = generator_chain.invoke(query)
            print(generator_result)
        except Exception as e:
            print(f"Generator error: {e}")
            generator_result = "Error generating initial answer."
        
        # Run verifier independently for verbose output
        print("\n[2] VERIFIER OUTPUT (DeepSeek with Search Results):")
        print("-"*40)
        try:
            verifier_result = verifier_chain.invoke(query)
            print(verifier_result)
        except Exception as e:
            print(f"Verifier error: {e}")
            verifier_result = "Error verifying with search results."
        
        # Run the complete system
        print("\n[3] FINAL SYNTHESIZED OUTPUT (Meta Llama-3.2):")
        print("-"*40)
    
    try:
        # Run the complete system
        final_answer = complete_system.invoke(query)
        
        if verbose:
            print(final_answer)
            print("="*80)
        
        return final_answer
    except Exception as e:
        error_msg = f"System error: {e}"
        if verbose:
            print(error_msg)
            print("="*80)
        return error_msg

# ===========================
# TESTING FUNCTION
# ===========================

def test_individual_models(query: str = "What is the capital of France?"):
    """
    Test each model individually to ensure they're working properly.
    
    Args:
        query: Simple test query
    """
    print("\n" + "="*80)
    print("TESTING INDIVIDUAL MODELS")
    print("="*80)
    
    # Test Search Tool
    print("\nTesting Search Tool...")
    try:
        if search_tool:
            results = search_tool.invoke(query)
            print(f"✅ Search tool working: Found {len(results)} results")
        else:
            print("❌ Search tool not initialized")
    except Exception as e:
        print(f"❌ Search tool error: {e}")
    
    # Test Generator
    print("\nTesting Generator (Grok-4-fast)...")
    try:
        test_prompt = generator_prompt_template.format_messages(query=query)
        response = generator_llm.invoke(test_prompt)
        print(f"✅ Generator working: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Generator error: {e}")
    
    time.sleep(1)  # Avoid rate limits
    
    # Test Verifier
    print("\nTesting Verifier (DeepSeek)...")
    try:
        test_prompt = verifier_prompt_template.format_messages(
            query=query, 
            context="France is a country in Europe. Its capital city is Paris."
        )
        response = verifier_llm.invoke(test_prompt)
        print(f"✅ Verifier working: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Verifier error: {e}")
    
    time.sleep(1)  # Avoid rate limits
    
    # Test Comparer
    print("\nTesting Comparer (Meta Llama-3.2)...")
    try:
        test_prompt = comparer_prompt_template.format_messages(
            query=query,
            generator_answer="The capital of France is Paris.",
            verifier_answer="Based on the search results, the capital of France is Paris."
        )
        response = comparer_llm.invoke(test_prompt)
        print(f"✅ Comparer working: {response.content[:100]}...")
    except Exception as e:
        print(f"❌ Comparer error: {e}")
    
    print("="*80)

# ===========================
# MAIN EXECUTION BLOCK
# ===========================

if __name__ == "__main__":
    
    # Example queries that could be prone to hallucination
    example_queries = [
        "What were the key outcomes of the 2024 Nobel Prize announcements?",
        "What is the current status of the James Webb Space Telescope's latest discoveries?",
        "Explain the latest breakthroughs in quantum computing from 2024",
        "What are the most recent updates to Python 3.13 released in 2024?",
        "Who won the Formula 1 World Championship in 2024?",
        "Compare F1 standings 2024 and 2023",  # Your example query
    ]
    
    # Run the system with an example query
    print("\n" + "="*80)
    print("MULTI-LLM HALLUCINATION REDUCTION SYSTEM (via OpenRouter)")
    print("="*80)
    print("\nUsing models:")
    print("- Generator: x-ai/grok-4-fast:free")
    print("- Verifier: deepseek/deepseek-chat-v3.1:free")
    print("- Comparer: qwen/qwen3-coder:free")
    print("="*80)
    
    # Check if API keys are set
    if not tavily_api_key or not openrouter_api_key:
        print("\n⚠️  ERROR: Required API keys are not set!")
        print("\nPlease set the following environment variables:")
        print("1. TAVILY_API_KEY - Get from https://tavily.com")
        print("2. OPENROUTER_API_KEY - Get from https://openrouter.ai/keys")
        print("\nExample (Linux/Mac):")
        print("export TAVILY_API_KEY='your-tavily-key'")
        print("export OPENROUTER_API_KEY='your-openrouter-key'")
        print("\nExample (Windows):")
        print("set TAVILY_API_KEY=your-tavily-key")
        print("set OPENROUTER_API_KEY=your-openrouter-key")
        print("="*80)
    else:
        # Optional: Test individual models first
        print("\nDo you want to test individual models first? (y/n): ", end="")
        test_choice = input().strip().lower()
        if test_choice == 'y':
            test_individual_models()
        
        # Select a query (using your F1 example)
        test_query = input("Enter the query: ") # "Compare F1 standings 2024 and 2023"
        
        try:
            # Run the complete system with verbose output
            final_answer = run_hallucination_reduction_system(test_query, verbose=True)
            
            print("\n" + "="*80)
            print("SYSTEM EXECUTION COMPLETED SUCCESSFULLY")
            print("="*80)
            
            # Optional: Test with another query
            print("\n\nWould you like to test with another query? Here are some options:")
            for i, q in enumerate(example_queries, 1):
                print(f"{i}. {q}")
            print("\nEnter number (1-6) or 'q' to quit: ", end="")
            choice = input().strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(example_queries):
                selected_query = example_queries[int(choice) - 1]
                print(f"\nRunning with: {selected_query}")
                run_hallucination_reduction_system(selected_query, verbose=True)
            
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("\nTroubleshooting tips:")
            print("1. Verify your OpenRouter API key is valid")
            print("2. Check if you have credits/quota on OpenRouter")
            print("3. Verify your Tavily API key is valid")
            print("4. Ensure you have installed required packages:")
            print("   pip install langchain langchain-community langchain-openai tavily-python")
            print("5. Check your internet connection")
            print("\nYou can test individual models using the test function to isolate issues.")