import React, { useState } from 'react';
import './Home.css';

const Home = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [selectedModel, setSelectedModel] = useState('roberta');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Reset previous results
    setError('');
    setResult(null);
    
    // Validate URL
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/scrape_predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          url: url,
          model: selectedModel
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze the article');
    } finally {
      setLoading(false);
    }
  };

  const getPredictionLabel = (prediction) => {
    return prediction === 1 ? 'Fake News' : 'Real News';
  };

  const getPredictionClass = (prediction) => {
    return prediction === 1 ? 'fake' : 'real';
  };
  
  const capitalizeSentences = (text) => {
    if (!text) return '';
    return text.replace(/(^\s*\w|[.!?]\s*\w)/g, (match) => match.toUpperCase());
  };

  return (
    <div className="home-container">
      <div className="header">
        <p>Enter a news article URL to check if it's fake or real</p>
      </div>

      {/* Only show form if there's no result */}
      {!result && (
        <>
          <form onSubmit={handleSubmit} className="url-form">
            <div className="input-group">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/article"
                className="url-input"
                disabled={loading}
              />
              <select 
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="model-select"
                disabled={loading}
              >
                <option value="roberta">RoBERTa</option>
                <option value="bert-tiny">BERT Tiny</option>
                <option value="BERT">BERT</option>
              </select>
              <button 
                type="submit" 
                className="submit-button"
                disabled={loading}
              >
                {loading ? 'Analyzing...' : 'Check Article'}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}

          {loading && (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Scraping and analyzing article...</p>
            </div>
          )}
        </>
      )}

      {/* Show results when available */}
      {result && !loading && (
        <div className="results-container">
          <div className={`prediction-badge ${getPredictionClass(result.prediction)}`}>
            <h2>{getPredictionLabel(result.prediction)}</h2>
            <div className="confidence-score">
              {result.prediction === 1 ? '🚫' : '✅'}
            </div>
          </div>

          <div className="article-details">
            {result.model_used && (
              <div className="model-info">
                <span>Analyzed with: {result.model_used}</span>
              </div>
            )}
            
            <div className="article-section">
              <h3>Article Title</h3>
              <p>{capitalizeSentences(result.title)}</p>
            </div>

            <div className="article-section">
              <h3>Article Content</h3>
              <div className="article-text">
                {capitalizeSentences(result.text.length > 500 
                  ? `${result.text.substring(0, 500)}...` 
                  : result.text)
                }
              </div>
            </div>
          </div>

          <button 
            onClick={() => {
              setUrl('');
              setResult(null);
              setError('');
            }}
            className="reset-button"
          >
            Check Another Article
          </button>
        </div>
      )}
    </div>
  );
};

export default Home;