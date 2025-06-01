import React, { useState, useEffect } from 'react'; 
import './Home.css';
import Modal from './Modal'; 


const HistoryModalContent = ({ history, getPredictionLabel, getPredictionClass, onClose }) => {
  return (
    <div className="history-list-modal">
      {}
      {history && history.length > 0 ? (
        <ul>
          {history.map((item) => (
            <li key={item.id}>
              <strong>Model: {item.model_used}</strong>
              <em>URL: {item.url}</em>
              <div className="prediction-info">
                Prediction: <span className={getPredictionClass(item.prediction)}>
                  {getPredictionLabel(item.prediction)}
                </span>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-history-msg">No history records found.</p>

      )}
      {}
      <button onClick={onClose} className="hide-history-btn-modal">Hide History</button>
    </div>
  );
};


const Home = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [selectedModel, setSelectedModel] = useState('RoBERTa');
  const [history, setHistory] = useState([]);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false); 

  useEffect(() => {
    if (isHistoryModalOpen) {
      document.body.classList.add('modal-open-no-scroll'); 
    } else {
      document.body.classList.remove('modal-open-no-scroll'); 
    }
    return () => document.body.classList.remove('modal-open-no-scroll');
  }, [isHistoryModalOpen]);


  const fetchAndShowHistory = async () => {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      setError('User not logged in. Please log in to view history.');
      setIsHistoryModalOpen(false); 
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/history?user_id=${userId}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch history');
      }

      setHistory(data);
      setError('');
      setIsHistoryModalOpen(true);
    } catch (err) {
      setError(err.message || 'Error fetching history');
      setHistory([]);
      setIsHistoryModalOpen(true);
    }
  };

  const closeHistoryModal = () => {
    setIsHistoryModalOpen(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      setError('User not logged in.');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/scrape_predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, model: selectedModel, user_id: userId }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Something went wrong');
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

      {!result && (
        <>
          <div className="history-toggle">
            <button onClick={fetchAndShowHistory} className="history-btn">View My History</button>
          </div>

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
                <option value="RoBERTa">RoBERTa</option>
                <option value="BERT-tiny">BERT Tiny</option>
                <option value="BERT">BERT</option>
                <option value="My-BERT">My_BERT</option>
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

          {error && !isHistoryModalOpen && (
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

      <Modal
        isOpen={isHistoryModalOpen}
        onClose={closeHistoryModal}
        title="Your Detection History"
      >
        {error && isHistoryModalOpen && history.length === 0 && ( 
             <div className="error-message" style={{marginBottom: '15px', color: '#dc3545'}}>
                <span>⚠️ {error}</span>
             </div>
        )}
        <HistoryModalContent
          history={history}
          getPredictionLabel={getPredictionLabel}
          getPredictionClass={getPredictionClass}
          onClose={closeHistoryModal} 
        />
      </Modal>
    </div>
  );
};

export default Home; 
