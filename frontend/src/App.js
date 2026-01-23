import React, { useState, useEffect, useRef } from 'react';
import {
  Search,
  Sparkles,
  Shield,
  ChevronDown,
  ChevronUp,
  Globe,
  Plus,
  Menu,
  Trash2,
  MoreVertical,
  Heart,
  Scale,
  DollarSign,
  GraduationCap,
  Code,
  Bot,
  Send,
  Loader2,
  CheckCircle2,
  AlertCircle,
  MessageSquare
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exampleQueries, setExampleQueries] = useState([]);

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
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: "smooth",
        block: "end"
      });
    }
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
                    {domainConfig && <span style={{ fontSize: '0.8rem', opacity: 0.8 }}> - {domainConfig.name} Context</span>}
                  </h4>
                  <div className="detail-card-content">
                    {result.generator_answer}
                  </div>
                </div>

                <div className="detail-card">
                  <h4>
                    <Shield size={20} />
                    Verifier Model (DeepSeek with Search)
                    {domainConfig && <span style={{ fontSize: '0.8rem', opacity: 0.8 }}> - {domainConfig.name} Verification</span>}
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
      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="app-header">
          <div className="header-left">
            <span style={{ fontWeight: 'bold' }}>Multi-LLM System</span>
          </div>
          <button
            className="toggle-sidebar-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <Menu size={20} />
          </button>
        </div>

        <button className="new-chat-btn" onClick={startNewChat}>
          <Plus size={20} />
          New Chat
        </button>

        <div className="domain-selector">
          <button
            className="domain-selector-btn"
            onClick={() => setDomainSelectorOpen(!domainSelectorOpen)}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {React.createElement(getDomainIcon(selectedDomain), { size: 16 })}
              {domains[selectedDomain]?.name || 'General Assistant'}
            </span>
            <ChevronDown size={16} style={{ transform: domainSelectorOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
          </button>

          {domainSelectorOpen && (
            <div className="domain-dropdown">
              {Object.entries(domains).map(([key, config]) => (
                <button
                  key={key}
                  className={`domain-option ${selectedDomain === key ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedDomain(key);
                    setDomainSelectorOpen(false);
                  }}
                >
                  {React.createElement(getDomainIcon(key), { size: 18 })}
                  <div className="domain-info">
                    <div className="domain-name">{config.name}</div>
                    <div className="domain-description">{config.description}</div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="chat-list">
          {chats.map(chat => (
            <div
              key={chat.id}
              className={`chat-item ${currentChatId === chat.id ? 'active' : ''}`}
              onClick={() => {
                setCurrentChatId(chat.id);
                if (window.innerWidth < 768) setSidebarOpen(false);
              }}
            >
              <MessageSquare size={16} />
              <div className="chat-item-title">{chat.title}</div>

              <button
                className={`chat-menu-btn ${menuOpenId === chat.id ? 'active' : ''}`}
                onClick={(e) => toggleMenu(e, chat.id)}
              >
                <MoreVertical size={16} />
              </button>

              {menuOpenId === chat.id && (
                <div className="chat-menu-dropdown">
                  <div
                    className="chat-menu-item delete"
                    onClick={(e) => deleteChat(e, chat.id)}
                  >
                    <Trash2 size={14} />
                    Delete Chat
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        {!sidebarOpen && (
          <div style={{ position: 'absolute', top: '1rem', left: '1rem', zIndex: 20 }}>
            <button
              className="toggle-sidebar-btn"
              onClick={() => setSidebarOpen(true)}
              style={{ background: 'rgba(15, 23, 42, 0.6)', backdropFilter: 'blur(10px)' }}
            >
              <Menu size={20} />
            </button>
          </div>
        )}

        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="empty-state">
              <h1>
                {domains[selectedDomain]?.name || 'Multi-LLM System'}
              </h1>
              <p>
                {domains[selectedDomain]?.description || 'Advanced hallucination reduction system using multiple LLMs for verification.'}
              </p>

              <div className="example-queries">
                {exampleQueries.map((q, i) => (
                  <div key={i} className="example-card" onClick={() => handleExampleClick(q)}>
                    <h3><Sparkles size={16} /> Example Query</h3>
                    {q}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div key={msg.id} className={`message ${msg.role === 'user' ? 'user-message' : 'assistant-message'}`}>
                  {msg.role === 'user' ? (
                    <div className="user-bubble">
                      {msg.content}
                    </div>
                  ) : (
                    msg.metadata ? (
                      <ResultCard result={msg.metadata} />
                    ) : (
                      <div className="results-section">
                        <div className="final-answer-content">
                          <ReactMarkdown children={msg.content} />
                        </div>
                      </div>
                    )
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
          <div className="input-container">
            <form onSubmit={handleSubmit}>
              <input
                type="text"
                className="query-input"
                placeholder={`Ask anything to ${domains[selectedDomain]?.name || 'General Assistant'}...`}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !query.trim()}
              >
                {loading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
              </button>
            </form>
            {error && (
              <div style={{
                color: '#ef4444',
                marginTop: '0.5rem',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                paddingLeft: '0.5rem'
              }}>
                <AlertCircle size={16} />
                {error}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;