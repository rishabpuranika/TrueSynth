import React, { useState, useEffect } from 'react';
import { 
  Send, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Search,
  Sparkles,
  Shield,
  Zap,
  ChevronDown,
  ChevronUp,
  Globe,
  Brain,
  FileText
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [exampleQueries, setExampleQueries] = useState([]);
  const [showDetails, setShowDetails] = useState(false);
  const [healthStatus, setHealthStatus] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    // Load example queries
    fetchExampleQueries();
    // Check health status
    checkHealth();
  }, []);

  const fetchExampleQueries = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/example-queries`);
      const data = await response.json();
      setExampleQueries(data.queries);
    } catch (err) {
      console.error('Failed to fetch example queries:', err);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      const data = await response.json();
      setHealthStatus(data);
    } catch (err) {
      setError('Backend server is not running. Please start the server.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);
    setCurrentStep(1);

    try {
      // Simulate step progression
      const stepInterval = setInterval(() => {
        setCurrentStep(prev => Math.min(prev + 1, 3));
      }, 2000);

      const response = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          verbose: true
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      clearInterval(stepInterval);
      setCurrentStep(4);
      setResults(data);
      setShowDetails(false);
    } catch (err) {
      setError(err.message || 'Failed to process query. Please try again.');
      setCurrentStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  const formatTime = (seconds) => {
    return `${seconds.toFixed(2)}s`;
  };

  const getStepStatus = (step) => {
    if (currentStep > step) return 'completed';
    if (currentStep === step) return 'active';
    return 'pending';
  };

  const ProcessingSteps = () => (
    <div className="processing-steps">
      <div className={`step ${getStepStatus(1)}`}>
        <div className="step-icon">
          <Sparkles size={20} />
        </div>
        <div className="step-content">
          <div className="step-title">Generating Initial Answer</div>
          <div className="step-subtitle">LLama3.3-8b Model</div>
        </div>
      </div>
      <div className={`step ${getStepStatus(2)}`}>
        <div className="step-icon">
          <Search size={20} />
        </div>
        <div className="step-content">
          <div className="step-title">Searching & Verifying Facts</div>
          <div className="step-subtitle">DeepSeek + Tavily Search</div>
        </div>
      </div>
      <div className={`step ${getStepStatus(3)}`}>
        <div className="step-icon">
          <Shield size={20} />
        </div>
        <div className="step-content">
          <div className="step-title">Synthesizing Final Answer</div>
          <div className="step-subtitle">Nemotron Model</div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
            'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
            sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
        }

        .app {
          min-height: 100vh;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }

        .app-header {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          padding: 1.5rem 0;
        }

        .header-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 2rem;
          text-align: center;
        }

        .logo {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 1rem;
          margin-bottom: 0.5rem;
        }

        .logo-icon {
          width: 40px;
          height: 40px;
          color: #fff;
        }

        .logo h1 {
          color: #fff;
          font-size: 1.8rem;
          font-weight: 600;
        }

        .header-subtitle {
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9rem;
        }

        .health-status {
          display: flex;
          justify-content: center;
          gap: 2rem;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.2);
          backdrop-filter: blur(10px);
        }

        .status-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: rgba(255, 255, 255, 0.9);
          font-size: 0.85rem;
        }

        .status-indicator {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #666;
        }

        .status-indicator.active {
          background: #4ade80;
          box-shadow: 0 0 10px rgba(74, 222, 128, 0.5);
        }

        .status-indicator.inactive {
          background: #ef4444;
        }

        .main-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .query-section {
          background: rgba(255, 255, 255, 0.95);
          border-radius: 20px;
          padding: 2rem;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }

        .query-form {
          display: flex;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .query-input {
          flex: 1;
          padding: 1rem 1.5rem;
          font-size: 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          transition: all 0.3s;
          outline: none;
        }

        .query-input:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .submit-button {
          padding: 1rem 2rem;
          background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .submit-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }

        .submit-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .example-queries {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .example-query {
          padding: 0.5rem 1rem;
          background: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .example-query:hover {
          background: #e5e7eb;
          transform: translateY(-1px);
        }

        .processing-steps {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          margin: 2rem 0;
        }

        .step {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background: white;
          border-radius: 12px;
          opacity: 0.5;
          transition: all 0.3s;
        }

        .step.active {
          opacity: 1;
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          animation: pulse 2s infinite;
        }

        .step.completed {
          opacity: 1;
          background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.02); }
        }

        .step-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 50%;
        }

        .step-title {
          font-weight: 600;
          color: #1f2937;
        }

        .step-subtitle {
          font-size: 0.85rem;
          color: #6b7280;
        }

        .results-section {
          background: rgba(255, 255, 255, 0.95);
          border-radius: 20px;
          padding: 2rem;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          margin-bottom: 2rem;
        }

        .final-answer {
          padding: 1.5rem;
          background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
          border-radius: 12px;
          margin-bottom: 1.5rem;
        }

        .final-answer h3 {
          color: #075985;
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .final-answer-content {
          color: #0c4a6e;
          line-height: 1.6;
        }

        .processing-time {
          text-align: center;
          color: #6b7280;
          font-size: 0.9rem;
          margin-top: 1rem;
        }

        .details-toggle {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          background: #f3f4f6;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          margin: 1.5rem auto;
          font-weight: 500;
        }

        .details-toggle:hover {
          background: #e5e7eb;
        }

        .details-content {
          display: grid;
          gap: 1rem;
          margin-top: 1.5rem;
        }

        .detail-card {
          padding: 1.5rem;
          background: #f9fafb;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
        }

        .detail-card h4 {
          color: #374151;
          margin-bottom: 1rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .detail-card-content {
          color: #4b5563;
          line-height: 1.6;
        }

        .search-results {
          display: grid;
          gap: 0.75rem;
          margin-top: 1rem;
        }

        .search-result {
          padding: 1rem;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
        }

        .search-result-title {
          font-weight: 600;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }

        .search-result-url {
          font-size: 0.8rem;
          color: #3b82f6;
          margin-bottom: 0.5rem;
        }

        .search-result-content {
          font-size: 0.9rem;
          color: #6b7280;
          line-height: 1.4;
        }

        .error-message {
          padding: 1rem;
          background: #fee2e2;
          border: 1px solid #fecaca;
          border-radius: 8px;
          color: #991b1b;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin: 1rem 0;
        }
      `}</style>

      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo">
            <Brain className="logo-icon" />
            <h1>Multi-LLM Hallucination Reduction System</h1>
          </div>
          <div className="header-subtitle">
            Powered by LLama, DeepSeek, and Nemotron via OpenRouter
          </div>
        </div>
      </header>

      {/* Health Status Bar */}
      {healthStatus && (
        <div className="health-status">
          <div className="status-item">
            <div className={`status-indicator ${healthStatus.api_keys_configured.tavily ? 'active' : 'inactive'}`} />
            Tavily Search
          </div>
          <div className="status-item">
            <div className={`status-indicator ${healthStatus.api_keys_configured.openrouter_1 ? 'active' : 'inactive'}`} />
            Generator Model
          </div>
          <div className="status-item">
            <div className={`status-indicator ${healthStatus.api_keys_configured.openrouter_2 ? 'active' : 'inactive'}`} />
            Verifier Model
          </div>
          <div className="status-item">
            <div className={`status-indicator ${healthStatus.api_keys_configured.openrouter_3 ? 'active' : 'inactive'}`} />
            Comparer Model
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        {/* Query Section */}
        <div className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your query here..."
              className="query-input"
              disabled={loading}
            />
            <button type="submit" disabled={loading || !query.trim()} className="submit-button">
              {loading ? (
                <>
                  <Loader2 size={20} className="animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send size={20} />
                  Analyze Query
                </>
              )}
            </button>
          </form>

          {/* Example Queries */}
          {exampleQueries.length > 0 && !loading && !results && (
            <div className="example-queries">
              {exampleQueries.slice(0, 4).map((eq, index) => (
                <div
                  key={index}
                  className="example-query"
                  onClick={() => handleExampleClick(eq)}
                >
                  {eq}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Processing Steps */}
        {loading && <ProcessingSteps />}

        {/* Results Section */}
        {results && !loading && (
          <div className="results-section">
            <div className="final-answer">
              <h3>
                <CheckCircle2 size={24} />
                Final Fact-Checked Answer
              </h3>
              <div className="final-answer-content">
                {/* 👇 Use ReactMarkdown here */}
                <ReactMarkdown children={results.final_answer} />
              </div>
            </div>

            {/* Processing Time */}
            <div className="processing-time">
              Processed in {formatTime(results.processing_time)}
            </div>

            {/* Toggle Details */}
            {results.generator_answer && results.verifier_answer && (
              <>
                <button
                  className="details-toggle"
                  onClick={() => setShowDetails(!showDetails)}
                >
                  {showDetails ? (
                    <>
                      <ChevronUp size={20} />
                      Hide Details
                    </>
                  ) : (
                    <>
                      <ChevronDown size={20} />
                      Show Details
                    </>
                  )}
                </button>

                {/* Details Content */}
                {showDetails && (
                  <div className="details-content">
                    {/* Generator Answer */}
                    <div className="detail-card">
                      <h4>
                        <Sparkles size={20} />
                        Generator Model (LLama-3.3-8b)
                      </h4>
                      <div className="detail-card-content">
                        {results.generator_answer}
                      </div>
                    </div>

                    {/* Verifier Answer */}
                    <div className="detail-card">
                      <h4>
                        <Shield size={20} />
                        Verifier Model (DeepSeek with Search)
                      </h4>
                      <div className="detail-card-content">
                        {results.verifier_answer}
                      </div>
                    </div>

                    {/* Search Results */}
                    {results.search_results && results.search_results.length > 0 && (
                      <div className="detail-card">
                        <h4>
                          <Globe size={20} />
                          Search Results
                        </h4>
                        <div className="search-results">
                          {results.search_results.map((result, index) => (
                            <div key={index} className="search-result">
                              <div className="search-result-title">{result.title}</div>
                              <div className="search-result-url">{result.url}</div>
                              <div className="search-result-content">{result.content}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;