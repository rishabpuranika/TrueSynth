import os
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


# Required API keys
tavily_api_key = os.getenv("TAVILY_API_KEY")
watsonx_api_key=os.getenv("WATSONX_API_KEY")
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
watsonx_project_id=os.getenv("WATSONX_PROJECT_ID")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
WATSONX_BASE_URL="https://eu-de.ml.cloud.ibm.com"
# Generator Model - Creative but potentially hallucinatory
# Using X.AI's Grok model via OpenRouter
# generator_llm = ChatOpenAI(
#     model="x-ai/grok-4-fast:free",
#     temperature=0.7,  # Higher temperature for more creative responses
#     openai_api_base=OPENROUTER_BASE_URL,
#     openai_api_key=openrouter_api_key,
#     default_headers={
#         "HTTP-Referer": "http://localhost:3000",  # Optional, for OpenRouter tracking
#         "X-Title": "Multi-LLM Hallucination Reduction System"  # Optional, for OpenRouter tracking
#     }
# )

# Use Watsonx hosted LLM for generator_llm
from langchain_ibm import WatsonxLLM

parameters = {"decoding_method": "greedy", "max_new_tokens": 500}
generator_llm = WatsonxLLM(
    model_id="meta-llama/llama-4-maverick-17b-128e-instruct-fp8",  # Update to your desired model
    url=WATSONX_BASE_URL,
    params=parameters,
    project_id=watsonx_project_id,
    apikey=watsonx_api_key
)

print(generator_llm.invoke("Points table of Formula 1 World Championship in 2024?"))