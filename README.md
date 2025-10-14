# TrueSynth: Multi-LLM Hallucination Reduction System

TrueSynth is a sophisticated system that uses multiple Large Language Models (LLMs) in a "Generate, Verify, Compare" architecture to reduce hallucinations and improve the factual accuracy of AI-generated answers. It is composed of a Python FastAPI backend and a React frontend.

## Features

  * **Multi-LLM Architecture:** Utilizes three different LLMs for generating, verifying, and comparing answers to provide a more reliable result.
  * **Fact-Checking with Web Search:** The verifier model uses Tavily Search to ground its answers in real-world, up-to-date information.
  * **React Frontend:** A user-friendly interface to interact with the system, view the final answer, and see the intermediate steps of the generation process.
  * **FastAPI Backend:** A robust and high-performance backend that serves the multi-LLM system via a REST API.
  * **Health Check Endpoint:** An endpoint to check the status of the API and the configuration of the required API keys.

## Architecture

The system is composed of a frontend application and a backend API.

### Backend

The backend is a FastAPI application that orchestrates the multi-LLM system. It uses three different LLMs from OpenRouter:

1.  **Generator Model (`meta-llama/llama-3.3-8b-instruct:free`):** Generates an initial, creative answer to the user's query.
2.  **Verifier Model (`deepseek/deepseek-r1-0528-qwen3-8b:free`):** Takes the user's query and search results from the Tavily Search API to generate a fact-based answer.
3.  **Comparer Model (`nvidia/nemotron-nano-9b-v2:free`):** Compares the answers from the Generator and Verifier models and synthesizes a final, corrected answer.

The backend exposes an API to process queries and provides health status checks.

### Frontend

The frontend is a React application that provides a user interface for the system. It allows users to:

  * Enter a query.
  * View the final fact-checked answer.
  * See the intermediate outputs from the Generator and Verifier models.
  * View the search results used by the Verifier model.

## Getting Started

### Prerequisites

  * Node.js and npm for the frontend.
  * Python 3.7+ and pip for the backend.
  * API keys for OpenRouter and Tavily.

### Backend Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/rishabpuranika/truesynth.git
    cd truesynth/backend
    ```

2.  **Create a virtual environment and install dependencies:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory and add your API keys:

    ```
    OPENROUTER_API_KEY1="your_openrouter_api_key"
    OPENROUTER_API_KEY2="your_openrouter_api_key"
    OPENROUTER_API_KEY3="your_openrouter_api_key"
    TAVILY_API_KEY="your_tavily_api_key"
    ```

4.  **Run the backend server:**

    ```bash
    uvicorn app:app --reload --port 8000
    ```

    The backend will be running at `http://localhost:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**

    ```bash
    cd ../frontend
    ```

2.  **Install dependencies:**

    ```bash
    npm install
    ```

3.  **Start the frontend development server:**

    ```bash
    npm start
    ```

    The frontend will be running at `http://localhost:3000`.

## API Endpoints

The backend provides the following API endpoints:

  * `GET /`: Root endpoint with a welcome message.
  * `GET /api/health`: Health check endpoint to verify the API status and API key configurations.
  * `POST /api/query`: Processes a user's query and returns the generated, verified, and final answers.
  * `GET /api/test-models`: Endpoint to test the individual models.
  * `GET /api/example-queries`: Returns a list of example queries.

## Environment Variables

The following environment variables are required for the backend to function correctly:

  * `OPENROUTER_API_KEY1`: Your OpenRouter API key for the Generator model.
  * `OPENROUTER_API_KEY2`: Your OpenRouter API key for the Verifier model.
  * `OPENROUTER_API_KEY3`: Your OpenRouter API key for the Comparer model.
  * `TAVILY_API_KEY`: Your Tavily Search API key.