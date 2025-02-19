import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Plot from 'react-plotly.js';
import "./StockAnalysis.css";

function StockAnalysis() {
  const { ticker } = useParams();
  const navigate = useNavigate();
  const [technicalData, setTechnicalData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [lineGraph, setLineGraph] = useState(null);
  const [candlestickGraph, setCandlestickGraph] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all data in parallel
        const [technicalRes, sentimentRes, lineRes, candlestickRes] = await Promise.all([
          fetch(`/api/stock/${ticker}/technical`),
          fetch(`/api/stock/${ticker}/sentiment`),
          fetch(`/api/stock/${ticker}/graph`),
          fetch(`/api/stock/${ticker}/candlestick`)
        ]);

        const [technical, sentiment, line, candlestick] = await Promise.all([
          technicalRes.json(),
          sentimentRes.json(),
          lineRes.json(),
          candlestickRes.json()
        ]);

        setTechnicalData(technical);
        setSentimentData(sentiment);
        setLineGraph(line);
        setCandlestickGraph(candlestick);
        
      } catch (err) {
        setError("Failed to fetch stock data");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (ticker) {
      fetchData();
    }
  }, [ticker]);

  if (loading) return <div className="analysis-container loading">Loading...</div>;
  if (error) return <div className="analysis-container error">{error}</div>;

  return (
    <div className="analysis-container">
      <button className="close-button" onClick={() => navigate('/')}>×</button>
      
      <h2>{ticker} Analysis</h2>
      
      <div className="analysis-section">
        <h3>Technical Analysis</h3>
        {technicalData && (
          <div className="technical-score">
            <div className={`recommendation ${technicalData.recommendation.toLowerCase()}`}>
              {technicalData.recommendation}
            </div>
            <div className="score">Score: {technicalData.score}</div>
          </div>
        )}
      </div>

      <div className="graphs-section">
        <div className="graph">
          <h4>Price History</h4>
          {lineGraph && <Plot data={lineGraph.data} layout={lineGraph.layout} />}
        </div>
        
        <div className="graph">
          <h4>Candlestick Chart</h4>
          {candlestickGraph && <Plot data={candlestickGraph.data} layout={candlestickGraph.layout} />}
        </div>
      </div>

      <div className="sentiment-section">
        <h3>Sentiment Analysis</h3>
        {sentimentData && (
          <div className="sentiment-scores">
            <div className="sentiment-bar">
              <label>News Sentiment</label>
              <div className="bar-container">
                <div 
                  className="bar" 
                  style={{ 
                    width: `${sentimentData.news_sentiment}%`,
                    backgroundColor: `hsl(${sentimentData.news_sentiment * 1.2}, 70%, 50%)`
                  }}
                >
                  {sentimentData.news_sentiment}
                </div>
              </div>
            </div>

            <div className="sentiment-bar">
              <label>Reddit Sentiment</label>
              <div className="bar-container">
                <div 
                  className="bar" 
                  style={{ 
                    width: `${sentimentData.reddit_sentiment}%`,
                    backgroundColor: `hsl(${sentimentData.reddit_sentiment * 1.2}, 70%, 50%)`
                  }}
                >
                  {sentimentData.reddit_sentiment}
                </div>
              </div>
            </div>

            <div className="sentiment-bar">
              <label>SEC Sentiment</label>
              <div className="bar-container">
                <div 
                  className="bar" 
                  style={{ 
                    width: `${sentimentData.sec_sentiment}%`,
                    backgroundColor: `hsl(${sentimentData.sec_sentiment * 1.2}, 70%, 50%)`
                  }}
                >
                  {sentimentData.sec_sentiment}
                </div>
              </div>
            </div>

            <div className="sentiment-bar overall">
              <label>Overall Sentiment</label>
              <div className="bar-container">
                <div 
                  className="bar" 
                  style={{ 
                    width: `${sentimentData.overall_sentiment}%`,
                    backgroundColor: `hsl(${sentimentData.overall_sentiment * 1.2}, 70%, 50%)`
                  }}
                >
                  {sentimentData.overall_sentiment}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default StockAnalysis; 