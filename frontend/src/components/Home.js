import React from 'react';

const Home = () => {
  return (
    <div className="home">
      <h2>Welcome to Fake News Detector</h2>
      <p>This is the dashboard for analyzing news articles for authenticity.</p>
      
      <div className="feature-cards">
        <div className="card">
          <h3>Analyze News</h3>
          <p>Submit news content to check its authenticity</p>
          <button>Start Analysis</button>
        </div>
        
        <div className="card">
          <h3>View History</h3>
          <p>See your previous analysis results</p>
          <button>View History</button>
        </div>
      </div>
    </div>
  );
};

export default Home;