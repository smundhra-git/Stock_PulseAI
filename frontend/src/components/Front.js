import React, { useState, useEffect } from "react";
import "./Front.css";

function Front() {
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchMarketOverview = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/sp500-realtime"); // ✅ Replace with your API URL
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
  }, []);

  return (
    <div className="market-overview">
      <h1>Market Overview</h1>

      {loading ? (
        <p>Loading market data...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : marketData ? (
        <div className="market-content">
          {/* ✅ Display S&P 500 Current Price */}
          <div className="market-section">
            <h2>S&P 500</h2>
            <p>Current Price: ${marketData.sp500?.current_price ?? "N/A"}</p>
            <p>Change: {marketData.sp500?.change} ({marketData.sp500?.percent_change}%)</p>
          </div>

          {/* ✅ Upcoming Earnings */}
          <div className="market-section">
            <h2>Upcoming Earnings</h2>
            <ul>
              {marketData.earnings?.length > 0 ? (
                marketData.earnings.map((earn, index) => (
                  <li key={index}>
                    {earn.company} - {earn.date} ({earn.estimate})
                  </li>
                ))
              ) : (
                <p>No upcoming earnings</p>
              )}
            </ul>
          </div>

          {/* ✅ Top Gainers & Losers */}
          <div className="market-section">
            <h2>Top Gainers</h2>
            <ul>
              {marketData.top_gainers?.map((stock, index) => (
                <li key={index}>{stock.ticker} - {stock.price} ({stock.change}%)</li>
              ))}
            </ul>

            <h2>Top Losers</h2>
            <ul>
              {marketData.top_losers?.map((stock, index) => (
                <li key={index}>{stock.ticker} - {stock.price} ({stock.change}%)</li>
              ))}
            </ul>
          </div>
        </div>
      ) : (
        <p>No market data available.</p>
      )}
    </div>
  );
}

export default Front;
