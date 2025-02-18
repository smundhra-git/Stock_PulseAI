import React, { useState, useEffect } from "react";
import "./Front.css";
import Plot from 'react-plotly.js';

const PERIOD_OPTIONS = ["1w", "1month", "3months", "6months", "1y", "5y", "max"];

function Front() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [period, setPeriod] = useState("1y"); // Default period

  useEffect(() => {
    const fetchMarketOverview = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/sp500-realtime?interval=${period}`);
        const data = await response.json();
        
        if (!response.ok) throw new Error(data.detail || "Failed to fetch market data");

        setMarketData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMarketOverview();
  }, [period]);

  return (
    <div className="market-overview">
      <h1>Market Overview</h1>

      <div className="period-selector">
        <label htmlFor="period">Select Period: </label>
        <select id="period" value={period} onChange={(e) => setPeriod(e.target.value)}>
          {PERIOD_OPTIONS.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <p>Loading market data...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : marketData ? (
        <div className="market-content">
          <Plot
            data={marketData.data}
            layout={marketData.layout}
            config={{ responsive: true }}
            style={{ width: "100%", height: "500px" }}
          />
        </div>
      ) : (
        <p>No market data available.</p>
      )}
    </div>
  );
}

export default Front;