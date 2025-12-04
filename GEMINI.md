# GEMINI.md

## Project Overview

This project, "TrueSynth," is a web application designed to reduce hallucinations in AI-generated answers. It utilizes a multi-LLM (Large Language Model) architecture with a "Generate, Verify, Compare" workflow.

The project is structured as a monorepo with two main components:

*   **Frontend:** A React application that provides a user interface to interact with the system.
*   **Backend:** A Python FastAPI server that orchestrates the multi-LLM system, using models from OpenRouter and fact-checking with Tavily Search.

The backend and frontend are configured for deployment on Vercel, as indicated by the `vercel.json` file.

## Building and Running

### Backend (Python/FastAPI)

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory with the following content:
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
    The backend will be available at `http://localhost:8000`.

### Frontend (React)

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Start the frontend development server:**
    ```bash
    npm start
    ```
    The frontend will be available at `http://localhost:3000`.

## Development Conventions

*   **Backend:**
    *   The backend is built with FastAPI and follows standard Python practices.
    *   It uses `asyncio` for concurrent operations.
    *   Dependencies are managed with `pip` and `requirements.txt`.
    *   The main application logic is in `app.py` and `llm_system.py`.

*   **Frontend:**
    *   The frontend is a standard Create React App project.
    *   It uses functional components with hooks (`useState`, `useEffect`).
    *   API requests to the backend are made using `fetch`.
    *   Styling is done using CSS-in-JS within the `App.js` component.
    *   The `lucide-react` library is used for icons.

*   **API:**
    *   The API is documented within the FastAPI application and can be accessed at `/docs` when the backend is running.
    *   The main endpoint for processing queries is `POST /api/query`.
