import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Plot from 'react-plotly.js';
import { ToggleRight, ToggleLeft } from 'lucide-react';
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
  const [chartType, setChartType] = useState("price");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [technicalRes, sentimentRes, lineRes, candlestickRes] = await Promise.all([
          fetch(`http://localhost:8000/api/stock/${ticker}/technical`),
          fetch(`http://localhost:8000/api/stock/${ticker}/sentiment`),
          fetch(`http://localhost:8000/api/stock/${ticker}/graph`),
          fetch(`http://localhost:8000/api/stock/${ticker}/candlestick`)
        ]);

        // Check if responses are ok
        if (!technicalRes.ok || !sentimentRes.ok || !lineRes.ok || !candlestickRes.ok) {
          throw new Error('One or more API calls failed');
        }

        const [technical, sentiment, line, candlestick] = await Promise.all([
          technicalRes.json(),
          sentimentRes.json(),
          lineRes.json(),
          candlestickRes.json()
        ]);

        console.debug('Technical Data:', technical);
        console.debug('Sentiment Data:', sentiment);
        console.debug('Line Graph Data:', line);
        console.debug('Candlestick Data:', candlestick);

        setTechnicalData(technical);
        setSentimentData(sentiment);
        setLineGraph(line);
        setCandlestickGraph(candlestick);
        
      } catch (err) {
        setError("Failed to fetch stock data: " + err.message);
        console.error("API Error:", err);
      } finally {
        setLoading(false);
      }
    };

    if (ticker) {
      fetchData();
    }
  }, [ticker]);

  const toggleChartType = () => {
    setChartType((prevChartType) => (prevChartType === "price" ? "candlestick" : "price"));
  };
  

  if (loading) return <div className="analysis-container loading">Loading...</div>;
  if (error) return <div className="analysis-container error">{error}</div>;

  // Update the Plot components' layout
  const commonLayout = {
    autosize: true,
    margin: { l: 50, r: 20, t: 20, b: 30 },
    height: 400,
    paper_bgcolor: 'white',
    plot_bgcolor: '#f8fafc',
    font: {
      family: 'system-ui, -apple-system, sans-serif',
      color: '#0a192f'
    },
    xaxis: {
      gridcolor: '#e2e8f0',
      linecolor: '#e2e8f0',
    },
    yaxis: {
      gridcolor: '#e2e8f0',
      linecolor: '#e2e8f0',
    }
  };

  return (
    <div className="analysis-container">
      <button className="close-button" onClick={() => navigate('/')}>×</button>
      
      <h2>{ticker} Analysis</h2>
      
      <div className="analysis-section">
        <h3>Technical Analysis</h3>
        {technicalData && (
          <div className="technical-score">
            <div className={`recommendation ${technicalData[0]?.toLowerCase()}`}>
              {technicalData[0]}
            </div>
            <div className="score">Score: {technicalData[1]}</div>
          </div>
        )}
      </div>

      <div className="graphs-section">
        <div className="chart-container">
          <div className="chart-header">
            <h4>Price Chart</h4>
            <div className="chart-controls">
              <button 
                className="toggle-button"
                onClick={toggleChartType}
                title={`Switch to ${chartType === "price" ? "Candlestick" : "Line"} Chart`}
              >
                <div className="chart-icon">
                  {chartType === "price" ? (
                    <ToggleRight size={20} strokeWidth={2.5} />
                  ) : (
                    <ToggleLeft size={20} strokeWidth={2.5} />
                  )}
                </div>
                <span>{chartType === "price" ? "Candlestick" : "Line"}</span>
              </button>
            </div>
          </div>
          
          <div className="chart-content">
            {chartType === "price" ? (
              lineGraph && (
                <Plot
                  data={lineGraph.data}
                  layout={{
                    ...lineGraph.layout,
                    ...commonLayout
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: "100%", height: "400px" }}
                />
              )
            ) : (
              candlestickGraph && (
                <Plot
                  data={candlestickGraph.data}
                  layout={{
                    ...candlestickGraph.layout,
                    ...commonLayout
                  }}
                  config={{ responsive: true, displayModeBar: false }}
                  style={{ width: "100%", height: "400px" }}
                />
              )
            )}
          </div>
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