import React, { useState, useEffect } from "react";
import "./Front.css";
import Plot from 'react-plotly.js';

const PERIOD_OPTIONS = ["1w", "1month", "3months", "6months", "1y", "5y", "max"];

const Front = () => {
  const [lineChartData, setLineChartData] = useState(null);
  const [loadingLineChart, setLoadingLineChart] = useState(true);
  const [linePeriod, setLinePeriod] = useState("1y");

  useEffect(() => {
    setLoadingLineChart(true);
    const periodParam = linePeriod.toLowerCase() === "all" ? "max" : linePeriod.toLowerCase();
    
    fetch(`http://localhost:8000/api/sp500-realtime?interval=${periodParam}`)
      .then(response => response.json())
      .then(data => {
        setLineChartData(data);
        setLoadingLineChart(false);
      })
      .catch(() => setLoadingLineChart(false)); 
  }, [linePeriod]); 

  return (
    <div className="market-overview">
      <h1>Market Overview</h1>

      <div className="period-selector">
        <label htmlFor="period">Select Period: </label>
        <select 
          id="period" 
          value={linePeriod} 
          onChange={(e) => setLinePeriod(e.target.value)}
        >
          {PERIOD_OPTIONS.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      {loadingLineChart ? (
        <p>Loading market data...</p>
      ) : lineChartData ? (
        <Plot
          data={lineChartData.data}
          layout={{
            ...lineChartData.layout,
            autosize: true,
            margin: {l: 50, r: 50, t: 50, b: 50},
          }}
          config={{ responsive: true }}
          style={{ width: "100%", height: "500px" }}
        />
      ) : (
        <p>Market data unavailable.</p>
      )}
    </div>
  );
};

export default Front;


    