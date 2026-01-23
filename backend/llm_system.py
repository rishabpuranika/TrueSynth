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
# DOMAIN CONFIGURATION
# ===========================

DOMAINS = {
    "general": {
        "name": "General Assistant",
        "description": "General-purpose AI assistant for any topic",
        "icon": "brain",
        "system_prompt": "You are a helpful AI assistant. Please answer the following query to the best of your ability."
    },
    "medical": {
        "name": "Medical Assistant",
        "description": "Healthcare and medical information specialist",
        "icon": "heart",
        "system_prompt": """You are a medical information assistant. Provide accurate, helpful health information while always emphasizing that you are not a substitute for professional medical advice, diagnosis, or treatment. Always recommend consulting healthcare professionals for medical concerns. Focus on general health education, wellness tips, and reliable medical information."""
    },
    "legal": {
        "name": "Legal Assistant",
        "description": "Legal research and general legal information",
        "icon": "scale",
        "system_prompt": """You are a legal information assistant. Provide general legal information and explanations of legal concepts. Always clarify that you are not a lawyer and cannot provide legal advice, represent clients, or substitute for professional legal counsel. Recommend consulting qualified attorneys for specific legal situations."""
    },
    "financial": {
        "name": "Financial Advisor",
        "description": "Financial planning and investment guidance",
        "icon": "dollar-sign",
        "system_prompt": """You are a financial information assistant. Provide general financial education and information about investing, personal finance, and economic concepts. Always emphasize that you are not a licensed financial advisor and cannot provide personalized financial advice. Recommend consulting certified financial professionals for investment decisions."""
    },
    "educational": {
        "name": "Educational Tutor",
        "description": "Learning assistant for academic subjects",
        "icon": "graduation-cap",
        "system_prompt": """You are an educational tutor and learning assistant. Help students understand academic concepts, explain difficult topics, and provide study guidance. Focus on making complex subjects accessible and encouraging critical thinking. Adapt your explanations to different learning styles and levels."""
    },
    "technical": {
        "name": "Technical Assistant",
        "description": "Programming and technical support",
        "icon": "code",
        "system_prompt": """You are a technical assistant specializing in programming, software development, and technical problem-solving. Provide code examples, debugging help, best practices, and technical explanations. Focus on practical solutions while explaining the reasoning behind technical decisions."""
    }
}

def get_domain_config(domain: str = "general") -> Dict[str, Any]:
    """Get domain configuration by domain key."""
    return DOMAINS.get(domain, DOMAINS["general"])

# ===========================
# MODEL INITIALIZATION
# ===========================

# Base URL for OpenRouter
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Generator Model - Creative but potentially hallucinatory
generator_llm = None
if openrouter_api_key1:
    generator_llm = ChatOpenAI(
        model="meta-llama/llama-3.3-70b-instruct:free",
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
        model="tngtech/deepseek-r1t-chimera:free",
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

def create_generator_prompt_template(system_prompt: str = "You are a helpful AI assistant. Please answer the following query to the best of your ability."):
    return ChatPromptTemplate.from_template(
        f"""{system_prompt}

Query: {{query}}

Answer:"""
    )

def create_verifier_prompt_template(system_prompt: str = "You are a factual assistant. Answer the following user query based ONLY on the provided search results context. Do not use any of your internal knowledge. If the context does not contain the answer, state that you cannot answer based on the information provided."):
    return ChatPromptTemplate.from_template(
        f"""{system_prompt}

Context:
{{context}}

Query: {{query}}"""
    )

def create_comparer_prompt_template(system_prompt: str = "You are a meticulous fact-checking and synthesis agent. Your goal is to produce the most accurate and reliable answer to the user's query by comparing two different AI-generated answers."):
    return ChatPromptTemplate.from_template(
        f"""{system_prompt}

Original Query: {{query}}

---

Generator Model (creative but potentially unreliable):
{{generator_answer}}

---

Verifier Model (grounded in web search results):
{{verifier_answer}}

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

# Default templates for backward compatibility
generator_prompt_template = create_generator_prompt_template()
verifier_prompt_template = create_verifier_prompt_template()
comparer_prompt_template = create_comparer_prompt_template()

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
else:
    complete_system = None

# ===========================
# DOMAIN-SPECIFIC FUNCTIONS
# ===========================

def create_domain_chains(domain: str = "general"):
    """Create domain-specific chains with custom prompts."""
    domain_config = get_domain_config(domain)

    # Create domain-specific prompt templates
    gen_template = create_generator_prompt_template(domain_config["system_prompt"])
    ver_template = create_verifier_prompt_template("You are a factual assistant specialized in " + domain_config["description"].lower() + ". Answer the following user query based ONLY on the provided search results context. Do not use any of your internal knowledge. If the context does not contain the answer, state that you cannot answer based on the information provided.")
    comp_template = create_comparer_prompt_template("You are a meticulous fact-checking and synthesis agent specialized in " + domain_config["description"].lower() + ". Your goal is to produce the most accurate and reliable answer to the user's query by comparing two different AI-generated answers.")

    # Create domain-specific chains
    domain_generator_chain = None
    domain_verifier_chain = None
    domain_comparer_chain = None
    domain_complete_system = None

    if generator_llm:
        domain_generator_chain = (
            {"query": RunnablePassthrough()}
            | gen_template
            | generator_llm
            | StrOutputParser()
        )

    if verifier_llm:
        search_runnable = RunnableLambda(search_and_format)
        domain_verifier_chain = (
            search_runnable
            | ver_template
            | verifier_llm
            | StrOutputParser()
        )

    if comparer_llm:
        domain_comparer_chain = (
            comp_template
            | comparer_llm
            | StrOutputParser()
        )

    if all([domain_generator_chain, domain_verifier_chain, domain_comparer_chain]):
        domain_complete_system = (
            RunnableParallel(
                query=RunnablePassthrough(),
                generator_answer=domain_generator_chain,
                verifier_answer=domain_verifier_chain,
            )
            | domain_comparer_chain
        )

    return {
        "generator_chain": domain_generator_chain,
        "verifier_chain": domain_verifier_chain,
        "comparer_chain": domain_comparer_chain,
        "complete_system": domain_complete_system,
        "domain_config": domain_config
    }

# ===========================
# MAIN UTILITY FUNCTION
# ===========================

def run_hallucination_reduction_system(query: str, domain: str = "general", verbose: bool = True) -> str:
    """Run the complete hallucination reduction system on a given query with domain-specific prompts."""

    # Create domain-specific chains
    domain_chains = create_domain_chains(domain)

    if not domain_chains["complete_system"]:
        return "System not properly initialized. Please check API keys."

    try:
        final_answer = domain_chains["complete_system"].invoke(query)
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