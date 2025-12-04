"""
FastAPI Backend for Multi-LLM Hallucination Reduction System
============================================================
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import asyncio
from datetime import datetime
import dotenv
import database

# Import the LLM system module
from llm_system import (
    run_hallucination_reduction_system,
    test_individual_models,
    generator_chain,
    verifier_chain,
    complete_system,
    search_and_format
)

# Load environment variables
dotenv.load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-LLM Hallucination Reduction API",
    description="API for multi-LLM fact-checking system using OpenRouter",
    version="1.0.0"
)

# Initialize Database
@app.on_event("startup")
async def startup_event():
    database.init_db()

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    verbose: Optional[bool] = True
    chat_id: Optional[str] = None

class QueryResponse(BaseModel):
    query: str
    generator_answer: Optional[str] = None
    verifier_answer: Optional[str] = None
    final_answer: str
    search_results: Optional[List[Dict]] = None
    processing_time: float
    timestamp: str
    success: bool
    error: Optional[str] = None
    chat_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    api_keys_configured: Dict[str, bool]
    timestamp: str

class ModelTestResponse(BaseModel):
    generator: Dict[str, Any]
    verifier: Dict[str, Any]
    comparer: Dict[str, Any]
    search_tool: Dict[str, Any]

# Utility Functions
async def run_generator_async(query: str) -> str:
    """Run generator chain asynchronously"""
    try:
        result = await asyncio.to_thread(generator_chain.invoke, query)
        return result
    except Exception as e:
        return f"Generator error: {str(e)}"

async def run_verifier_async(query: str) -> str:
    """Run verifier chain asynchronously"""
    try:
        result = await asyncio.to_thread(verifier_chain.invoke, query)
        return result
    except Exception as e:
        return f"Verifier error: {str(e)}"

async def run_search_async(query: str) -> Dict:
    """Run search asynchronously"""
    try:
        result = await asyncio.to_thread(search_and_format, query)
        return result
    except Exception as e:
        return {"query": query, "context": f"Search error: {str(e)}"}

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-LLM Hallucination Reduction API",
        "docs": "Visit /docs for API documentation"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health and configuration status"""
    return HealthResponse(
        status="healthy",
        api_keys_configured={
            "tavily": bool(os.getenv("TAVILY_API_KEY")),
            "openrouter_1": bool(os.getenv("OPENROUTER_API_KEY1")),
            "openrouter_2": bool(os.getenv("OPENROUTER_API_KEY2")),
            "openrouter_3": bool(os.getenv("OPENROUTER_API_KEY3")),
        },
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/chats")
async def get_chats():
    """Get all chat sessions"""
    return await asyncio.to_thread(database.get_all_chats)

@app.get("/api/chats/{chat_id}")
async def get_chat_details(chat_id: str):
    """Get messages for a specific chat"""
    return await asyncio.to_thread(database.get_chat_messages, chat_id)

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query through the multi-LLM system
    
    This endpoint:
    1. Generates an initial answer using Grok
    2. Searches and verifies using DeepSeek
    3. Synthesizes final answer using Nemotron
    """
    start_time = datetime.now()
    
    # Handle Chat ID
    chat_id = request.chat_id
    if not chat_id:
        # Create new chat if not provided
        # Use the query as the title (truncated)
        title = request.query[:50] + "..." if len(request.query) > 50 else request.query
        chat_id = await asyncio.to_thread(database.create_chat, title)
    
    # Save User Message
    await asyncio.to_thread(
        database.add_message, 
        chat_id, 
        "user", 
        request.query, 
        None
    )

    try:
        # Check API keys
        if not all([
            os.getenv("TAVILY_API_KEY"),
            os.getenv("OPENROUTER_API_KEY1"),
            os.getenv("OPENROUTER_API_KEY2"),
            os.getenv("OPENROUTER_API_KEY3")
        ]):
            raise HTTPException(
                status_code=500,
                detail="Missing required API keys. Please configure all API keys."
            )
        
        # Run all components in parallel for better performance
        generator_task = asyncio.create_task(run_generator_async(request.query))
        verifier_task = asyncio.create_task(run_verifier_async(request.query))
        search_task = asyncio.create_task(run_search_async(request.query))
        
        # Wait for all tasks to complete
        generator_answer = await generator_task
        verifier_answer = await verifier_task
        search_results = await search_task
        
        # Run the complete system for final answer
        final_answer = await asyncio.to_thread(
            complete_system.invoke,
            request.query
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Parse search results for frontend display
        search_context = search_results.get("context", "")
        parsed_search_results = []
        
        if "Result" in search_context:
            # Simple parsing of search results
            results = search_context.split("Result")[1:]
            for result in results[:5]:  # Limit to 5 results
                lines = result.strip().split("\n")
                result_dict = {}
                for line in lines:
                    if "Title:" in line:
                        result_dict["title"] = line.replace("Title:", "").strip()
                    elif "URL:" in line:
                        result_dict["url"] = line.replace("URL:", "").strip()
                    elif "Content:" in line:
                        result_dict["content"] = line.replace("Content:", "").strip()[:200] + "..."
                if result_dict:
                    parsed_search_results.append(result_dict)
        
        # Prepare response data
        response_data = {
            "query": request.query,
            "generator_answer": generator_answer if request.verbose else None,
            "verifier_answer": verifier_answer if request.verbose else None,
            "final_answer": final_answer,
            "search_results": parsed_search_results if request.verbose else None,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "error": None,
            "chat_id": chat_id
        }

        # Save Assistant Message
        await asyncio.to_thread(
            database.add_message,
            chat_id,
            "assistant",
            final_answer,
            response_data # Save full details in metadata
        )

        return QueryResponse(**response_data)
        
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        
        error_response = {
            "query": request.query,
            "generator_answer": None,
            "verifier_answer": None,
            "final_answer": f"Error processing query: {str(e)}",
            "search_results": None,
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e),
            "chat_id": chat_id
        }
        
        # Save Error Message
        await asyncio.to_thread(
            database.add_message,
            chat_id,
            "assistant",
            error_response["final_answer"],
            error_response
        )

        return QueryResponse(**error_response)

@app.get("/api/test-models", response_model=ModelTestResponse)
async def test_models():
    """Test individual model connections"""
    test_query = "What is the capital of France?"
    
    results = {
        "generator": {"status": "unknown", "message": ""},
        "verifier": {"status": "unknown", "message": ""},
        "comparer": {"status": "unknown", "message": ""},
        "search_tool": {"status": "unknown", "message": ""}
    }
    
    # Test Generator
    try:
        gen_result = await run_generator_async(test_query)
        if gen_result and "error" not in gen_result.lower():
            results["generator"] = {
                "status": "success",
                "message": "Generator (Grok-4-fast) is working",
                "sample": gen_result[:100] + "..."
            }
        else:
            results["generator"] = {"status": "error", "message": gen_result}
    except Exception as e:
        results["generator"] = {"status": "error", "message": str(e)}
    
    # Test Verifier
    try:
        ver_result = await run_verifier_async(test_query)
        if ver_result and "error" not in ver_result.lower():
            results["verifier"] = {
                "status": "success",
                "message": "Verifier (DeepSeek) is working",
                "sample": ver_result[:100] + "..."
            }
        else:
            results["verifier"] = {"status": "error", "message": ver_result}
    except Exception as e:
        results["verifier"] = {"status": "error", "message": str(e)}
    
    # Test Comparer (using complete system)
    try:
        comp_result = await asyncio.to_thread(complete_system.invoke, test_query)
        if comp_result and "error" not in comp_result.lower():
            results["comparer"] = {
                "status": "success",
                "message": "Comparer (Nemotron) is working",
                "sample": comp_result[:100] + "..."
            }
        else:
            results["comparer"] = {"status": "error", "message": comp_result}
    except Exception as e:
        results["comparer"] = {"status": "error", "message": str(e)}
    
    # Test Search Tool
    try:
        search_result = await run_search_async(test_query)
        if search_result and "context" in search_result:
            results["search_tool"] = {
                "status": "success",
                "message": "Tavily Search is working",
                "sample": search_result["context"][:100] + "..."
            }
        else:
            results["search_tool"] = {"status": "error", "message": "No search results"}
    except Exception as e:
        results["search_tool"] = {"status": "error", "message": str(e)}
    
    return ModelTestResponse(**results)

@app.get("/api/example-queries")
async def get_example_queries():
    """Get example queries for testing"""
    return {
        "queries": [
            "What were the key outcomes of the 2024 Nobel Prize announcements?",
            "What is the current status of the James Webb Space Telescope's latest discoveries?",
            "Explain the latest breakthroughs in quantum computing from 2024",
            "What are the most recent updates to Python 3.13 released in 2024?",
            "Who won the Formula 1 World Championship in 2024?",
            "Compare F1 standings 2024 and 2023",
            "What are the latest developments in AI safety research?",
            "Summarize the recent climate change reports from 2024",
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)