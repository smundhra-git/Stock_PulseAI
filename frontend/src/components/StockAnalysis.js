import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Plot from "react-plotly.js";
import {
  ToggleRight,
  ToggleLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  LineChart as LineChartIcon,
  Brain,
  Newspaper,
  Activity,
} from "lucide-react";
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
  const [activeTab, setActiveTab] = useState("technical"); // Handles Tabs

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [technicalRes, sentimentRes, lineRes, candlestickRes] = await Promise.all([
          fetch(`http://localhost:8000/api/stock/${ticker}/technical`),
          fetch(`http://localhost:8000/api/stock/${ticker}/sentiment`),
          fetch(`http://localhost:8000/api/stock/${ticker}/graph`),
          fetch(`http://localhost:8000/api/stock/${ticker}/candlestick`),
        ]);

        if (!technicalRes.ok || !sentimentRes.ok || !lineRes.ok || !candlestickRes.ok) {
          throw new Error("One or more API calls failed");
        }

        const [technical, sentiment, line, candlestick] = await Promise.all([
          technicalRes.json(),
          sentimentRes.json(),
          lineRes.json(),
          candlestickRes.json(),
        ]);

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

  const commonLayout = {
    autosize: true,
    margin: { l: 50, r: 20, t: 20, b: 30 },
    height: 400,
    paper_bgcolor: "white",
    plot_bgcolor: "#f8fafc",
    font: {
      family: "system-ui, -apple-system, sans-serif",
      color: "#0a192f",
    },
    xaxis: {
      gridcolor: "#e2e8f0",
      linecolor: "#e2e8f0",
    },
    yaxis: {
      gridcolor: "#e2e8f0",
      linecolor: "#e2e8f0",
    },
  };

  return (
    <div className="analysis-container">
      <button className="close-button" onClick={() => navigate("/")}>×</button>

      {/* Stock Header */}
      <div className="stock-header">
        <h1 className="stock-title">{ticker} Stock Analysis</h1>
        <div className="stock-price">
          <span className="price">${technicalData.price}</span>
          <div className="price-change">
            <TrendingUp className="text-green-600" size={20} />
            <span className="text-green-600">{technicalData["price-change"]}%</span>
          </div>
        </div>
      </div>

      {/* Graphs Section */}
      <div className="graphs-section">
        <div className="chart-container">
          <div className="chart-header">
            <h4>Price Chart</h4>
            <button className="toggle-button" onClick={toggleChartType}>
              {chartType === "price" ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
              <span>{chartType === "price" ? "Candlestick" : "Line"}</span>
            </button>
          </div>

          {chartType === "price" ? (
            lineGraph && (
              <Plot data={lineGraph.data} layout={{ ...lineGraph.layout, ...commonLayout }} config={{ responsive: true, displayModeBar: false }} style={{ width: "100%", height: "400px" }} />
            )
          ) : (
            candlestickGraph && (
              <Plot data={candlestickGraph.data} layout={{ ...candlestickGraph.layout, ...commonLayout }} config={{ responsive: true, displayModeBar: false }} style={{ width: "100%", height: "400px" }} />
            )
          )}
        </div>
      </div>

      {/* Technical & Sentiment Analysis */}
      <div className="tabs">
        <button className={`tab ${activeTab === "technical" ? "active" : ""}`} onClick={() => setActiveTab("technical")}>
          <Activity className="tab-icon" /> Technical Analysis
        </button>
        <button className={`tab ${activeTab === "sentiment" ? "active" : ""}`} onClick={() => setActiveTab("sentiment")}>
          <Brain className="tab-icon" /> Sentiment Analysis
        </button>
      </div>

      {activeTab === "technical" && (
        <div className="tab-content">
          <p className="text-gray-600">RSI (14): <span className="text-gray-900">65.42</span></p>
          <p className="text-gray-600">MACD: <span className="text-gray-900">12.33</span></p>
        </div>
      )}

      {activeTab === "sentiment" && (
        <div className="tab-content">
          <p className="text-gray-600">News Sentiment: <span className="text-yellow-600">Neutral</span></p>
          <p className="text-gray-600">Analyst Rating: <span className="text-gray-900">Buy</span></p>
        </div>
      )}
    </div>
  );
}

export default StockAnalysis;
