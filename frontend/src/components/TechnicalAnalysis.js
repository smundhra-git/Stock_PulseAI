import React, { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import './TechnicalAnalysis.css';

// Example sets of options for period and interval:
const PERIOD_OPTIONS = ["1w", "1month", "3months", "6months", "1y", "5y", "max"];
const INTERVAL_OPTIONS = ["1d", "2d", "5d", "1y", "73d", "100d"];

const TechnicalAnalysis = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(true);

  // --- LINE CHART STATES ---
  const [lineChartData, setLineChartData] = useState(null);
  const [loadingLineChart, setLoadingLineChart] = useState(true);
  const [linePeriod, setLinePeriod] = useState("1Y");    // default
  const [lineInterval, setLineInterval] = useState("1d"); // default

  // --- CANDLESTICK STATES ---
  const [candlestickData, setCandlestickData] = useState(null);
  const [loadingCandleStick, setLoadingCandleStick] = useState(true);
  const [candlePeriod, setCandlePeriod] = useState("1Y");   // default
  const [candleInterval, setCandleInterval] = useState("1d"); // default

  const ticker = "COIN";

  // Fetch Technical Analysis data
  useEffect(() => {
    setLoadingAnalysis(true);
    fetch(`http://localhost:8000/api/stock/${ticker.toLowerCase()}/technical`)
      .then(response => response.json())
      .then(data => {
        setAnalysis(data);
        setLoadingAnalysis(false);
      })
      .catch(() => setLoadingAnalysis(false));
  }, [ticker]);

  // Fetch line chart data whenever linePeriod or lineInterval changes
  useEffect(() => {
    setLoadingLineChart(true);
    // Convert "ALL" or "YTD" etc. to a valid query param for your backend if needed.
    // For example, if your API expects "max" for "ALL", handle that logic here.
    const periodParam = linePeriod.toLowerCase() === "all" ? "max" : linePeriod.toLowerCase();
    const intervalParam = lineInterval; // e.g. "1d", "5min", etc.

    // Example endpoint usage: /graph?period=1y or /graph?period=max
    fetch(`http://localhost:8000/api/stock/${ticker.toLowerCase()}/graph?period=${periodParam}`)
      .then(response => response.json())
      .then(data => {
        setLineChartData(data);
        setLoadingLineChart(false);
      })
      .catch(() => setLoadingLineChart(false));
  }, [ticker, linePeriod, lineInterval]);

  // Fetch candlestick data whenever candlePeriod or candleInterval changes
  useEffect(() => {
    setLoadingCandleStick(true);
    const periodParam = candlePeriod.toLowerCase() === "all" ? "max" : candlePeriod.toLowerCase();
    const intervalParam = candleInterval; // e.g. "1d", "5min", etc.

    fetch(`http://localhost:8000/api/stock/${ticker.toLowerCase()}/candlestick?period=${periodParam}&interval=${intervalParam}`)
      .then(response => response.json())
      .then(data => {
        setCandlestickData(data);
        setLoadingCandleStick(false);
      })
      .catch(() => setLoadingCandleStick(false));
  }, [ticker, candlePeriod, candleInterval]);

  // Handlers for user clicks on the period buttons
  const handleLinePeriodClick = (p) => setLinePeriod(p);
  const handleCandlePeriodClick = (p) => setCandlePeriod(p);

  return (
    <div className="technical-analysis">
      <div className="analysis-section">
        <h2>Technical Analysis for {ticker.toUpperCase()}</h2>
        {loadingAnalysis ? (
          <p>Loading analysis...</p>
        ) : analysis ? (
          <div className="analysis-data">
            <p><strong>Ticker:</strong> {analysis.ticker.toUpperCase()}</p>
            <p><strong>Recommendation:</strong> {analysis.recommendation}</p>
            <p><strong>Score:</strong> {analysis.score}</p>
          </div>
        ) : (
          <p>Analysis data unavailable.</p>
        )}
      </div>

      {/* Graph container with two sections: line chart and candlestick */}
      <div className="graph-container">

        {/* LINE CHART SECTION */}
        <div className="graph-section">
          <div className="interval-selector">
            {/* Period buttons for the line chart */}
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option}
                className={`interval-button ${linePeriod === option ? 'active' : ''}`}
                onClick={() => handleLinePeriodClick(option)}
              >
                {option}
              </button>
            ))}
          </div>

          {/* Actual line chart rendering */}
          {loadingLineChart ? (
            <p>Loading line graph...</p>
          ) : lineChartData ? (
            <Plot
              data={lineChartData.data}
              layout={{
                ...lineChartData.layout,
                autosize: true,
                margin: { l: 50, r: 50, t: 50, b: 50 }
              }}
              config={{ responsive: true }}
              style={{ width: "100%", height: "calc(100% - 40px)" }} 
              /* Deduct some space for the interval selector row */
            />
          ) : (
            <p>Line graph data unavailable.</p>
          )}
        </div>

        {/* CANDLESTICK SECTION */}
        <div className="graph-section">
          <div className="interval-selector">
            {/* Period buttons for the candlestick chart */}
            {PERIOD_OPTIONS.map((option) => (
              <button
                key={option}
                className={`interval-button ${candlePeriod === option ? 'active' : ''}`}
                onClick={() => handleCandlePeriodClick(option)}
              >
                {option}
              </button>
            ))}
            {/* Interval dropdown for the candlestick chart */}
            <select
              className="interval-dropdown"
              value={candleInterval}
              onChange={(e) => setCandleInterval(e.target.value)}
            >
              {INTERVAL_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          </div>

          {/* Actual candlestick chart rendering */}
          {loadingCandleStick ? (
            <p>Loading candlestick graph...</p>
          ) : candlestickData ? (
            <Plot
              data={candlestickData.data}
              layout={{
                ...candlestickData.layout,
                autosize: true,
                margin: { l: 50, r: 50, t: 50, b: 50 }
              }}
              config={{ responsive: true }}
              style={{ width: "100%", height: "calc(100% - 40px)" }}
            />
          ) : (
            <p>Candlestick graph data unavailable.</p>
          )}
        </div>

      </div>
    </div>
  );
};

export default TechnicalAnalysis;
