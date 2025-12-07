import React, { useState, useEffect, useRef } from 'react';
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
  FileText,
  MessageSquare,
  Plus,
  Menu,
  X,
  Trash2,
  MoreVertical,
  Heart,
  Scale,
  DollarSign,
  GraduationCap,
  Code,
  Bot
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exampleQueries, setExampleQueries] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  // Chat History State
  const [chats, setChats] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [menuOpenId, setMenuOpenId] = useState(null);

  // Domain State
  const [domains, setDomains] = useState({});
  const [selectedDomain, setSelectedDomain] = useState('general');
  const [domainSelectorOpen, setDomainSelectorOpen] = useState(false);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchExampleQueries();
    checkHealth();
    fetchChats();
    fetchDomains();
  }, []);

  useEffect(() => {
    if (currentChatId) {
      fetchChatMessages(currentChatId);
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStep]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const deleteChat = async (e, chatId) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this chat?")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setChats(prev => prev.filter(c => c.id !== chatId));
        if (currentChatId === chatId) {
          startNewChat();
        }
      }
    } catch (err) {
      console.error('Failed to delete chat:', err);
    }
  };

  const toggleMenu = (e, chatId) => {
    e.stopPropagation();
    setMenuOpenId(menuOpenId === chatId ? null : chatId);
  };

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setMenuOpenId(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  const fetchChats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats`);
      if (response.ok) {
        const data = await response.json();
        setChats(data);
      }
    } catch (err) {
      console.error('Failed to fetch chats:', err);
    }
  };

  const fetchChatMessages = async (chatId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chats/${chatId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    }
  };

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

  const fetchDomains = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/domains`);
      const data = await response.json();
      setDomains(data.domains);
    } catch (err) {
      console.error('Failed to fetch domains:', err);
    }
  };

  const startNewChat = () => {
    setCurrentChatId(null);
    setMessages([]);
    setQuery('');
    setError(null);
    setSelectedDomain('general');
  };

  const getDomainIcon = (domainKey) => {
    const iconMap = {
      'general': Bot,
      'medical': Heart,
      'legal': Scale,
      'financial': DollarSign,
      'educational': GraduationCap,
      'technical': Code
    };
    return iconMap[domainKey] || Bot;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userQuery = query.trim();
    setQuery('');
    setLoading(true);
    setError(null);
    setCurrentStep(1);

    // Optimistically add user message
    const tempUserMsg = {
      id: 'temp-user',
      role: 'user',
      content: userQuery,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

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
          query: userQuery,
          verbose: true,
          chat_id: currentChatId,
          domain: selectedDomain
        })
      });

      clearInterval(stepInterval);
      setCurrentStep(4);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // If this was a new chat, update the ID and refresh chat list
      if (!currentChatId && data.chat_id) {
        setCurrentChatId(data.chat_id);
        fetchChats();
      }

      // Replace temp message and add response
      // Actually, we should just re-fetch messages to be safe and consistent, 
      // but for smooth UI we can append. 
      // Let's append the assistant response.
      const assistantMsg = {
        id: 'new-assistant',
        role: 'assistant',
        content: data.final_answer,
        metadata: data,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => prev.map(m => m.id === 'temp-user' ? { ...m, id: 'saved-user' } : m).concat(assistantMsg));

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

  const ResultCard = ({ result }) => {
    const [showDetails, setShowDetails] = useState(false);
    const domainConfig = result.domain_config || domains[result.domain];

    return (
      <div className="results-section">
        <div className="final-answer">
          <h3>
            <CheckCircle2 size={24} />
            {domainConfig ? `${domainConfig.name} Answer` : 'Final Fact-Checked Answer'}
            {domainConfig && React.createElement(getDomainIcon(result.domain), { size: 20, style: { marginLeft: '0.5rem' } })}
          </h3>
          <div className="final-answer-content">
            <ReactMarkdown children={result.final_answer} />
          </div>
        </div>

        <div className="processing-time">
          Processed in {formatTime(result.processing_time)}
        </div>

        {result.generator_answer && result.verifier_answer && (
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

            {showDetails && (
              <div className="details-content">
                 <div className="detail-card">
                   <h4>
                     <Sparkles size={20} />
                     Generator Model (LLama-3.3-8b)
                     {domainConfig && <span style={{fontSize: '0.8rem', opacity: 0.8}}> - {domainConfig.name} Context</span>}
                   </h4>
                  <div className="detail-card-content">
                    {result.generator_answer}
                  </div>
                </div>

                 <div className="detail-card">
                   <h4>
                     <Shield size={20} />
                     Verifier Model (DeepSeek with Search)
                     {domainConfig && <span style={{fontSize: '0.8rem', opacity: 0.8}}> - {domainConfig.name} Verification</span>}
                   </h4>
                  <div className="detail-card-content">
                    {result.verifier_answer}
                  </div>
                </div>

                {result.search_results && result.search_results.length > 0 && (
                  <div className="detail-card">
                    <h4>
                      <Globe size={20} />
                      Search Results
                    </h4>
                    <div className="search-results">
                      {result.search_results.map((r, index) => (
                        <div key={index} className="search-result">
                          <div className="search-result-title">{r.title}</div>
                          <div className="search-result-url">{r.url}</div>
                          <div className="search-result-content">{r.content}</div>
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
    );
  };

  return (
    <div className="app-container">
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
          background: #f0f2f5;
          height: 100vh;
          overflow: hidden;
        }

        .app-container {
          display: flex;
          height: 100vh;
          background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        }

        /* Sidebar Styles */
        .sidebar {
          width: 260px;
          background: rgba(0, 0, 0, 0.3);
          backdrop-filter: blur(10px);
          border-right: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          flex-direction: column;
          transition: width 0.3s ease;
          flex-shrink: 0;
        }

        .sidebar.closed {
          width: 0;
          overflow: hidden;
          border: none;
        }

        .new-chat-btn {
          margin: 1rem;
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          color: white;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .new-chat-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .domain-selector {
          margin: 1rem;
          margin-top: 0;
        }

        .domain-selector-btn {
          width: calc(100% - 2rem);
          padding: 0.75rem;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          color: white;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
          font-size: 0.9rem;
        }

        .domain-selector-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .domain-selector-btn .rotated {
          transform: rotate(180deg);
        }

        .domain-dropdown {
          margin-top: 0.5rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          overflow: hidden;
          backdrop-filter: blur(10px);
        }

        .domain-option {
          width: 100%;
          padding: 0.75rem;
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.8);
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .domain-option:last-child {
          border-bottom: none;
        }

        .domain-option:hover,
        .domain-option.active {
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }

        .domain-info {
          flex: 1;
        }

        .domain-name {
          font-weight: 500;
          margin-bottom: 0.25rem;
        }

        .domain-description {
          font-size: 0.8rem;
          opacity: 0.8;
          line-height: 1.3;
        }

        .chat-list {
          flex: 1;
          overflow-y: auto;
          padding: 0 1rem;
        }

        .chat-item {
          position: relative;
          padding: 0.75rem;
          margin-bottom: 0.5rem;
          border-radius: 8px;
          color: rgba(255, 255, 255, 0.8);
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding-right: 2rem;
        }

        .chat-item:hover {
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }

        .chat-item.active {
          background: rgba(255, 255, 255, 0.15);
          color: white;
        }

        .chat-item-title {
          flex: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .chat-menu-btn {
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.6);
          padding: 4px;
          border-radius: 4px;
          cursor: pointer;
          display: none;
          transition: all 0.2s;
        }

        .chat-item:hover .chat-menu-btn,
        .chat-menu-btn.active {
          display: block;
        }

        .chat-menu-btn:hover {
          background: rgba(255, 255, 255, 0.2);
          color: white;
        }

        .chat-menu-dropdown {
          position: absolute;
          right: 0;
          top: 100%;
          background: #2d3748;
          border: 1px solid #4a5568;
          border-radius: 6px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
          z-index: 100;
          min-width: 120px;
          overflow: hidden;
        }

        .chat-menu-item {
          padding: 8px 12px;
          color: #e2e8f0;
          font-size: 0.85rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
          transition: background 0.2s;
        }

        .chat-menu-item:hover {
          background: #4a5568;
        }

        .chat-menu-item.delete {
          color: #fc8181;
        }

        .chat-menu-item.delete:hover {
          background: rgba(252, 129, 129, 0.1);
        }

        /* Main Content Styles */
        .main-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100vh;
          position: relative;
        }

        .app-header {
          padding: 1rem 2rem;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          align-items: center;
          justify-content: space-between;
          color: white;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .toggle-sidebar-btn {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          padding: 0.5rem;
          border-radius: 4px;
        }

        .toggle-sidebar-btn:hover {
          background: rgba(255, 255, 255, 0.1);
        }

        .chat-area {
          flex: 1;
          overflow-y: auto;
          padding: 2rem;
          display: flex;
          flex-direction: column;
          gap: 2rem;
          scroll-behavior: smooth;
        }

        .empty-state {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: white;
          text-align: center;
        }

        .empty-state h1 {
          font-size: 2.5rem;
          margin-bottom: 1rem;
        }

        .message {
          max-width: 900px;
          margin: 0 auto;
          width: 100%;
        }

        .user-message {
          display: flex;
          justify-content: flex-end;
        }

        .user-bubble {
          background: rgba(255, 255, 255, 0.2);
          padding: 1rem 1.5rem;
          border-radius: 20px 20px 0 20px;
          color: white;
          font-size: 1.1rem;
          max-width: 80%;
        }

        .assistant-message {
          width: 100%;
        }

        .input-area {
          padding: 2rem;
          background: rgba(0, 0, 0, 0.2);
          backdrop-filter: blur(10px);
        }

        .input-container {
          max-width: 900px;
          margin: 0 auto;
          position: relative;
        }

        .query-input {
          width: 100%;
          padding: 1rem 3.5rem 1rem 1.5rem;
          font-size: 1rem;
          background: rgba(255, 255, 255, 0.95);
          border: none;
          border-radius: 12px;
          outline: none;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .submit-btn {
          position: absolute;
          right: 0.5rem;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #3b82f6;
          padding: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .submit-btn:hover:not(:disabled) {
          color: #2563eb;
          transform: translateY(-50%) scale(1.1);
        }

        .submit-btn:disabled {
          color: #9ca3af;
          cursor: not-allowed;
        }

        /* Reused Styles from previous version */
        .processing-steps {
          max-width: 600px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 1rem;
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

        .step-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 50%;
        }

        .results-section {
          background: rgba(255, 255, 255, 0.95);
          border-radius: 20px;
          padding: 2rem;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
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
          margin: 1.5rem auto 0;
          font-weight: 500;
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

        .example-queries {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          justify-content: center;
          margin-top: 2rem;
          max-width: 800px;
        }

        .example-query {
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 20px;
          color: white;
          font-size: 0.85rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .example-query:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-1px);
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.02); }
        }
      `}</style>

      {/* Sidebar */}
      <div className={`sidebar ${!sidebarOpen ? 'closed' : ''}`}>
        <button className="new-chat-btn" onClick={startNewChat}>
          <Plus size={20} />
          New Chat
        </button>

        {/* Domain Selector */}
        <div className="domain-selector">
          <button
            className="domain-selector-btn"
            onClick={() => setDomainSelectorOpen(!domainSelectorOpen)}
          >
            {React.createElement(getDomainIcon(selectedDomain), { size: 16 })}
            <span>{domains[selectedDomain]?.name || 'General'}</span>
            <ChevronDown size={14} className={domainSelectorOpen ? 'rotated' : ''} />
          </button>

          {domainSelectorOpen && (
            <div className="domain-dropdown">
              {Object.entries(domains).map(([key, domain]) => {
                const IconComponent = getDomainIcon(key);
                return (
                  <button
                    key={key}
                    className={`domain-option ${selectedDomain === key ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedDomain(key);
                      setDomainSelectorOpen(false);
                    }}
                  >
                    <IconComponent size={16} />
                    <div className="domain-info">
                      <div className="domain-name">{domain.name}</div>
                      <div className="domain-description">{domain.description}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>

        <div className="chat-list">
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
              onClick={() => setCurrentChatId(chat.id)}
            >
              <MessageSquare size={16} />
              <span className="chat-item-title">{chat.title}</span>

              <button
                className={`chat-menu-btn ${menuOpenId === chat.id ? 'active' : ''}`}
                onClick={(e) => toggleMenu(e, chat.id)}
              >
                <MoreVertical size={16} />
              </button>

              {menuOpenId === chat.id && (
                <div className="chat-menu-dropdown">
                  <div className="chat-menu-item delete" onClick={(e) => deleteChat(e, chat.id)}>
                    <Trash2 size={14} />
                    Delete
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <header className="app-header">
          <div className="header-left">
            <button
              className="toggle-sidebar-btn"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <Menu size={24} />
            </button>
            <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Brain className="logo-icon" size={24} />
              <h2 style={{ fontSize: '1.2rem' }}>TrueSynth</h2>
            </div>
          </div>
          {healthStatus && (
            <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', opacity: 0.8 }}>
              <span>Generator: {healthStatus.api_keys_configured.openrouter_1 ? '✅' : '❌'}</span>
              <span>Verifier: {healthStatus.api_keys_configured.openrouter_2 ? '✅' : '❌'}</span>
            </div>
          )}
        </header>

        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Brain size={64} style={{ marginBottom: '1rem', opacity: 0.8 }} />
              <h1>How can I help you today?</h1>
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
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                  {msg.role === 'user' ? (
                    <div className="user-bubble">{msg.content}</div>
                  ) : (
                    <ResultCard result={msg.metadata || { final_answer: msg.content }} />
                  )}
                </div>
              ))}
              {loading && (
                <div className="message assistant-message">
                  <ProcessingSteps />
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <div className="input-area">
          <form onSubmit={handleSubmit} className="input-container">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Message TrueSynth..."
              className="query-input"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="submit-btn"
            >
              {loading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;