import React, { useState, useEffect } from "react";
import Plot from 'react-plotly.js';
import "./Front.css";

const PERIOD_OPTIONS = [
  { value: "1w", label: "1 Week" },
  { value: "1month", label: "1 Month" },
  { value: "3months", label: "3 Months" },
  { value: "6months", label: "6 Months" },
  { value: "1y", label: "1 Year" },
  { value: "5y", label: "5 Years" },
  { value: "max", label: "Max" }
];

const Front = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [lineChartData, setLineChartData] = useState(null);
  const [loadingLineChart, setLoadingLineChart] = useState(true);
  const [linePeriod, setLinePeriod] = useState("1y");
  const [marketNews, setMarketNews] = useState([]);

  // Define charts before using them in useEffect
  const charts = [
    { 
      name: 'S&P 500',
      endpoint: 'sp500-realtime'
    },
    { 
      name: 'NASDAQ 100',
      endpoint: 'nasdaq100-realtime'
    }
  ];

  // Fetch chart data
  useEffect(() => {
    const fetchChartData = async () => {
      setLoadingLineChart(true);
      try {
        const currentChart = charts[activeIndex];
        console.log(`Fetching ${currentChart.endpoint} with interval ${linePeriod}`);
        
        const response = await fetch(`http://localhost:8000/api/${currentChart.endpoint}?interval=${linePeriod}`);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to fetch data');
        }
        const data = await response.json();
        if (!data || !data.data || !Array.isArray(data.data)) {
          throw new Error('Invalid data format received');
        }
        setLineChartData(data);
      } catch (error) {
        console.error('Error fetching chart data:', error);
        // Show error message to user
        setLineChartData(null);
      } finally {
        setLoadingLineChart(false);
      }
    };

    fetchChartData();
  }, [activeIndex, linePeriod]);

  // Fetch news
  useEffect(() => {
    fetch('http://localhost:8000/api/front/news')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        if (data && Array.isArray(data)) {
          setMarketNews(data.slice(0, 5));
        } else {
          console.error('Invalid news data format');
        }
      })
      .catch(error => {
        console.error('Error fetching news:', error);
        setMarketNews([]); // Set empty array on error
      });
  }, []);

  return (
    <div className="front-container">
      <div className="market-section">
        {/* Chart Section */}
        <div className="chart-container">
          <div className="chart-header">
            <h2>{charts[activeIndex].name}</h2>
            <div className="chart-tabs">
              {charts.map((chart, index) => (
                <button
                  key={chart.name}
                  className={`chart-tab ${activeIndex === index ? 'active' : ''}`}
                  onClick={() => setActiveIndex(index)}
                >
                  {chart.name}
                </button>
              ))}
              <select 
                value={linePeriod} 
                onChange={(e) => setLinePeriod(e.target.value)}
                className="period-selector"
              >
                {PERIOD_OPTIONS.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="chart">
            {loadingLineChart ? (
              <div className="loading-chart">Loading chart data...</div>
            ) : lineChartData ? (
              <Plot
                data={lineChartData.data.map(trace => ({
                  ...trace,
                  line: { ...trace.line, color: '#0a192f' },
                  name: trace.name === 'Closing Price' ? 'Price' : trace.name
                }))}
                layout={{
                  ...lineChartData.layout,
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  autosize: true,
                  margin: { l: 50, r: 20, t: 10, b: 20 },
                  showlegend: false,
                  xaxis: {
                    ...lineChartData.layout.xaxis,
                    gridcolor: '#e5e7eb',
                    linecolor: '#e5e7eb',
                    title: null,
                    showgrid: true,
                    zeroline: false
                  },
                  yaxis: {
                    ...lineChartData.layout.yaxis,
                    gridcolor: '#e5e7eb',
                    linecolor: '#e5e7eb',
                    title: null,
                    showgrid: true,
                    zeroline: false
                  },
                  title: null
                }}
                config={{ 
                  responsive: true,
                  displayModeBar: false
                }}
                style={{ width: "100%", height: "400px" }}
              />
            ) : (
              <div className="error-chart">
                Unable to load chart data. Please try again later.
              </div>
            )}
          </div>
        </div>

        {/* News Section */}
        <div className="news-container">
          <h2>Latest Market News</h2>
          <div className="news-list">
            {marketNews.length > 0 ? (
              marketNews.map((news, index) => {
                // Format the timestamp
                const formattedTime = news.time === 'Recent' 
                  ? 'Recent'
                  : new Date(news.time).toLocaleString('en-US', {
                      relative: true,
                      style: 'numeric',
                      minimumFractionDigits: 0
                    });

                // Extract ticker and percentage if present
                const tickerMatch = news.title.match(/\(([^)]+)\)/);
                const percentageMatch = news.title.match(/([+-]\d+\.?\d*%)/);
                
                return (
                  <a 
                    key={index}
                    href={news.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="news-item"
                  >
                    <div className="news-header">
                      <span className="news-time">{formattedTime} ago</span>
                    </div>
                    <div className="news-content">
                      <h3 className="news-title">{news.title}</h3>
                      {tickerMatch && percentageMatch && (
                        <div className="news-tickers">
                          <span className="ticker">{tickerMatch[1]}</span>
                          <span className={`percentage ${percentageMatch[1].startsWith('+') ? 'positive' : 'negative'}`}>
                            {percentageMatch[1]}
                          </span>
                        </div>
                      )}
                    </div>
                  </a>
                );
              })
            ) : (
              <div className="news-empty">No news available at the moment</div>
            )}
          </div>
        </div>
      </div>

      {/* Widgets Section */}
      <div className="widgets-section">
        <div className="widget">
          <iframe 
            src="https://www.widgets.investing.com/top-cryptocurrencies?theme=darkTheme" 
            width="100%" 
            height="400" 
            frameBorder="0" 
            allowtransparency="true"
            title="Crypto Widget"
          />
        </div>

        {/* Economic Calendar Widget */}
        <div className="widget">
          <iframe 
            src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timezone&countries=25,32,6,37,72,22,17,39,14,10,35,43,56,36,110,11,26,12,4,5&calType=day&timeZone=8&lang=1"
            width="100%"
            height="467"
            frameBorder="0"
            allowTransparency="true"
            marginWidth="0"
            marginHeight="0"
            title="Economic Calendar"
          />
          <div className="poweredBy">
            <span>
              Real Time Economic Calendar provided by 
              <a 
                href="https://www.investing.com/" 
                rel="nofollow" 
                target="_blank"
                className="underline_link"
              >
                Investing.com
              </a>.
            </span>
          </div>
        </div>

        <div className="widget">
          <iframe 
            src="https://sslirates.investing.com/index.php?rows=2&bg1=FFFFFF&bg2=F1F5F8&text_color=333333&enable_border=show&border_color=0452A1&header_bg=0452A1&header_text=FFFFFF&force_lang=1"
            width="100%"
            height="100"
            frameBorder="0" 
            allowtransparency="true"
            title="Rates Widget"
          />
        </div>
      </div>
    </div>
  );
};

export default Front;


    