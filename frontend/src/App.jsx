import { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || "https://ai-texr-summarizer.onrender.com";

function App() {
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [minLength, setMinLength] = useState(25);
  const [maxLength, setMaxLength] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState(null);

  const handleSummarize = async () => {
    if (!text.trim()) {
      setError('Please enter some text to summarize');
      return;
    }

    setLoading(true);
    setError('');
    setSummary('');
    setStats(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/summarize`,
        {
          text: text,
          min_length: parseInt(minLength),
          max_length: parseInt(maxLength)
        },
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 60000 // 60 second timeout
        }
      );

      if (response.data.success) {
        setSummary(response.data.summary);
        setStats({
          original: response.data.original_length,
          summary: response.data.summary_length
        });
      }
    } catch (err) {
      console.error('Error:', err);
      
      if (err.code === 'ECONNABORTED') {
        setError('Request timed out. The text might be too long or the server is busy. Please try again.');
      } else if (err.response) {
        setError(err.response.data.error || 'An error occurred during summarization');
      } else if (err.request) {
        setError('Cannot connect to the server. Please ensure the backend is running on ' + API_URL);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
    setSummary('');
    setError('');
    setStats(null);
  };

  const exampleText = "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans. AI research has been defined as the field of study of intelligent agents, which refers to any system that perceives its environment and takes actions that maximize its chance of achieving its goals. The term artificial intelligence had previously been used to describe machines that mimic and display human cognitive skills that are associated with the human mind, such as learning and problem-solving. This definition has since been rejected by major AI researchers who now describe AI in terms of rationality and acting rationally, which does not limit how intelligence can be articulated. AI applications include advanced web search engines, recommendation systems, understanding human speech, self-driving cars, automated decision-making, and competing at the highest level in strategic game systems.";

  return (
    <div className="app">
      <div className="container">
        <header>
          <h1>🤖 AI Text Summarizer</h1>
          <p className="subtitle">Powered by Hugging Face BART Model</p>
        </header>

        <div className="controls-section">
          <div className="control-group">
            <label>
              Min Length: <span className="value">{minLength}</span>
            </label>
            <input
              type="range"
              min="10"
              max="200"
              value={minLength}
              onChange={(e) => setMinLength(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="control-group">
            <label>
              Max Length: <span className="value">{maxLength}</span>
            </label>
            <input
              type="range"
              min="20"
              max="500"
              value={maxLength}
              onChange={(e) => setMaxLength(e.target.value)}
              disabled={loading}
            />
          </div>
        </div>

        <div className="input-section">
          <div className="section-header">
            <h2>Input Text</h2>
            <button 
              className="btn-secondary"
              onClick={() => setText(exampleText)}
              disabled={loading}
            >
              Load Example
            </button>
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter or paste your text here (minimum 10 words, maximum 10000 characters)..."
            disabled={loading}
            rows={10}
          />
          <div className="char-count">
            Characters: {text.length} / 10000 | Words: {text.trim().split(/\s+/).filter(Boolean).length}
          </div>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="button-group">
          <button
            className="btn-primary"
            onClick={handleSummarize}
            disabled={loading || !text.trim()}
          >
            {loading ? '⏳ Summarizing...' : '✨ Summarize Text'}
          </button>
          <button
            className="btn-secondary"
            onClick={handleClear}
            disabled={loading}
          >
            🗑️ Clear All
          </button>
        </div>

        {summary && (
          <div className="output-section">
            <div className="section-header">
              <h2>Summary</h2>
              {stats && (
                <div className="stats">
                  <span>Original: {stats.original} words</span>
                  <span>Summary: {stats.summary} words</span>
                  <span className="reduction">
                    {Math.round((1 - stats.summary / stats.original) * 100)}% reduction
                  </span>
                </div>
              )}
            </div>
            <div className="summary-box">
              {summary}
            </div>
          </div>
        )}

        {loading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Processing your text with AI model...</p>
          </div>
        )}

        <footer>
          <p>Built with Flask, Hugging Face Transformers, and React.js</p>
        </footer>
      </div>
    </div>
  );
}

export default App;