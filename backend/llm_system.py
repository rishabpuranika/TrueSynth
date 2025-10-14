"""
Multi-LLM Hallucination Reduction System with OpenRouter
Modified for FastAPI Backend Integration
=========================================================
"""

import os
import time
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
import dotenv

# Load environment variables
dotenv.load_dotenv()

# ===========================
# CONFIGURATION SECTION
# ===========================

# Set up API keys from environment variables
tavily_api_key = os.getenv("TAVILY_API_KEY")
openrouter_api_key1 = os.getenv("OPENROUTER_API_KEY1")
openrouter_api_key2 = os.getenv("OPENROUTER_API_KEY2")
openrouter_api_key3 = os.getenv("OPENROUTER_API_KEY3")

# ===========================
# MODEL INITIALIZATION
# ===========================

# Base URL for OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Generator Model - Creative but potentially hallucinatory
generator_llm = None
if openrouter_api_key1:
    generator_llm = ChatOpenAI(
        model="meta-llama/llama-3.3-8b-instruct:free",
        temperature=0.7,
        openai_api_base=OPENROUTER_BASE_URL,
        openai_api_key=openrouter_api_key1,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Multi-LLM Hallucination Reduction System"
        }
    )

# Verifier Model - Grounded and factual
verifier_llm = None
if openrouter_api_key2:
    verifier_llm = ChatOpenAI(
        model="deepseek/deepseek-r1-0528-qwen3-8b:free",
        temperature=0.2,
        openai_api_base=OPENROUTER_BASE_URL,
        openai_api_key=openrouter_api_key2,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Multi-LLM Hallucination Reduction System"
        }
    )

# Comparer Model - Critical reasoner and synthesizer
comparer_llm = None
if openrouter_api_key3:
    comparer_llm = ChatOpenAI(
        model="nvidia/nemotron-nano-9b-v2:free",
        temperature=0.2,
        openai_api_base=OPENROUTER_BASE_URL,
        openai_api_key=openrouter_api_key3,
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Multi-LLM Hallucination Reduction System"
        }
    )

# ===========================
# SEARCH TOOL INITIALIZATION
# ===========================

search_tool = None
if tavily_api_key:
    try:
        search_tool = TavilySearchResults(
            api_key=tavily_api_key,
            max_results=5,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False,
        )
        print(f"✅ Tavily Search Tool initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing Tavily Search Tool: {e}")

# ===========================
# PROMPT TEMPLATES
# ===========================

generator_prompt_template = ChatPromptTemplate.from_template(
    """You are a helpful AI assistant. Please answer the following query to the best of your ability:

Query: {query}

Answer:"""
)

verifier_prompt_template = ChatPromptTemplate.from_template(
    """You are a factual assistant. Answer the following user query based ONLY on the provided search results context. Do not use any of your internal knowledge. If the context does not contain the answer, state that you cannot answer based on the information provided.

Context:
{context}

Query: {query}"""
)

comparer_prompt_template = ChatPromptTemplate.from_template(
    """You are a meticulous fact-checking and synthesis agent. Your goal is to produce the most accurate and reliable answer to the user's query by comparing two different AI-generated answers.

Original Query: {query}

---

Answer 1 (from a creative but potentially unreliable model):
{generator_answer}

---

Answer 2 (grounded in web search results):
{verifier_answer}

---

INSTRUCTIONS:
1.  Carefully compare 'Answer 1' against 'Answer 2'.
2.  Identify any statements in 'Answer 1' that are not supported by the facts in 'Answer 2'.
3.  Synthesize a final, comprehensive answer that corrects any inaccuracies or hallucinations from 'Answer 1' using the factual information from 'Answer 2'.
4.  If 'Answer 2' provides more relevant or up-to-date information, prioritize it.
5.  Present only the final, synthesized answer. Do not explain your reasoning process unless the query asks for it.

Final Corrected Answer:"""
)

# ===========================
# UTILITY FUNCTIONS
# ===========================

def format_search_results(results: List[Dict]) -> str:
    """Format search results into a readable context string."""
    if not results:
        return "No search results found."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
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
    """Search for information and format the results."""
    if search_tool is None:
        return {
            "query": query,
            "context": "Search functionality is not available. Please verify your Tavily API key."
        }
    
    try:
        search_results = search_tool.invoke(query)
        context = format_search_results(search_results)
        return {
            "query": query,
            "context": context
        }
    except Exception as e:
        return {
            "query": query,
            "context": f"Error performing search: {str(e)}. No context available."
        }

# ===========================
# COMPONENT CHAINS
# ===========================

# Initialize chains only if models are available
generator_chain = None
verifier_chain = None
comparer_chain = None
complete_system = None

if generator_llm:
    generator_chain = (
        {"query": RunnablePassthrough()}
        | generator_prompt_template
        | generator_llm
        | StrOutputParser()
    )

if verifier_llm:
    search_runnable = RunnableLambda(search_and_format)
    verifier_chain = (
        search_runnable
        | verifier_prompt_template
        | verifier_llm
        | StrOutputParser()
    )

if comparer_llm:
    comparer_chain = (
        comparer_prompt_template
        | comparer_llm
        | StrOutputParser()
    )

if all([generator_chain, verifier_chain, comparer_chain]):
    complete_system = (
        RunnableParallel(
            query=RunnablePassthrough(),
            generator_answer=generator_chain,
            verifier_answer=verifier_chain,
        )
        | comparer_chain
    )

# ===========================
# MAIN UTILITY FUNCTION
# ===========================

def run_hallucination_reduction_system(query: str, verbose: bool = True) -> str:
    """Run the complete hallucination reduction system on a given query."""
    
    if not complete_system:
        return "System not properly initialized. Please check API keys."
    
    try:
        final_answer = complete_system.invoke(query)
        return final_answer
    except Exception as e:
        return f"System error: {e}"

def test_individual_models(query: str = "What is the capital of France?"):
    """Test each model individually to ensure they're working properly."""
    results = {}
    
    # Test Search Tool
    if search_tool:
        try:
            search_results = search_tool.invoke(query)
            results['search'] = f"Found {len(search_results)} results"
        except Exception as e:
            results['search'] = f"Error: {e}"
    else:
        results['search'] = "Not initialized"
    
    # Test Generator
    if generator_llm:
        try:
            test_prompt = generator_prompt_template.format_messages(query=query)
            response = generator_llm.invoke(test_prompt)
            results['generator'] = response.content[:100] + "..."
        except Exception as e:
            results['generator'] = f"Error: {e}"
    else:
        results['generator'] = "Not initialized"
    
    # Test Verifier
    if verifier_llm:
        try:
            test_prompt = verifier_prompt_template.format_messages(
                query=query, 
                context="France is a country in Europe. Its capital city is Paris."
            )
            response = verifier_llm.invoke(test_prompt)
            results['verifier'] = response.content[:100] + "..."
        except Exception as e:
            results['verifier'] = f"Error: {e}"
    else:
        results['verifier'] = "Not initialized"
    
    # Test Comparer
    if comparer_llm:
        try:
            test_prompt = comparer_prompt_template.format_messages(
                query=query,
                generator_answer="The capital of France is Paris.",
                verifier_answer="Based on the search results, the capital of France is Paris."
            )
            response = comparer_llm.invoke(test_prompt)
            results['comparer'] = response.content[:100] + "..."
        except Exception as e:
            results['comparer'] = f"Error: {e}"
    else:
        results['comparer'] = "Not initialized"
    
    return results