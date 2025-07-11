# 📈 Stock Pulse AI

> **AI-Powered Financial Market Analysis Platform**

Stock Pulse AI is a comprehensive financial analysis platform that combines **technical analysis**, **sentiment analysis**, and **real-time market data** to provide intelligent insights for stock market investments. The platform uses advanced AI models to analyze news sentiment, social media trends, SEC filings, and technical indicators to generate actionable investment intelligence.

## 📋 Table of Contents

- [Features](#-features)
- [Technologies Used](#-technologies-used)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Development Roadmap](#-development-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 **Core Analytics**
- **Technical Analysis**: 9-factor scoring system rating stocks from -9 to +9
- **Sentiment Analysis**: Multi-source sentiment scoring using AI/NLP models
- **Real-time Market Data**: Live stock prices, charts, and market indicators
- **Interactive Visualizations**: Candlestick charts, line graphs, and technical indicators

### 🧠 **AI-Powered Insights**
- **News Sentiment**: Analysis of financial news using FinBERT and VADER models
- **Social Media Sentiment**: Reddit and social platform sentiment tracking
- **SEC Filings Analysis**: Automated analysis of company filings and reports
- **Multi-timeframe Analysis**: 1-day, 1-month, 1-year predictions and trends

### 🌐 **Platform Features**
- **RESTful API**: FastAPI backend with automatic OpenAPI documentation
- **Modern Frontend**: React-based dashboard with responsive design
- **Real-time Updates**: Live market data and sentiment updates
- **Authentication**: Secure user management and API access
- **Market Coverage**: S&P 500, NASDAQ, and individual stock analysis

## 🛠 Technologies Used

### **Backend**
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.9+** - Core programming language
- **PostgreSQL** - Primary database for data storage
- **SQLAlchemy** - Database ORM and query builder

### **AI/ML Stack**
- **PyTorch** - Deep learning framework for AI models
- **Transformers (Hugging Face)** - Pre-trained NLP models (FinBERT)
- **VADER Sentiment** - Rule-based sentiment analysis
- **scikit-learn** - Machine learning algorithms and tools
- **pandas** - Data manipulation and analysis

### **Data Sources & APIs**
- **yfinance** - Yahoo Finance API for stock data
- **NewsAPI** - Financial news and sentiment data
- **Reddit API (PRAW)** - Social sentiment analysis
- **SEC EDGAR** - Official company filings and reports

### **Frontend**
- **React 18** - Frontend framework
- **Plotly.js** - Interactive data visualizations
- **React Router** - Client-side routing
- **Recharts** - Additional charting library

### **DevOps & Deployment**
- **Docker** - Containerization
- **Git** - Version control
- **GitHub Actions** - CI/CD pipelines

## 💻 System Requirements

### **Minimum Requirements**
- **Python**: 3.9 or higher
- **Node.js**: 16.0 or higher
- **npm**: 8.0 or higher
- **Memory**: 4GB RAM (8GB recommended)
- **Storage**: 2GB free space

### **Recommended Setup**
- **Operating System**: macOS, Linux, or Windows 10/11
- **Python**: 3.10+
- **Memory**: 8GB+ RAM for optimal AI model performance
- **GPU**: Optional, for faster AI model inference

### **External Dependencies**
- **NewsAPI Key**: For financial news data (free tier available)
- **Internet Connection**: For real-time market data and API access

## 🚀 Installation

### **1. Clone the Repository**
```bash
git clone https://github.com/smundhra-git/Stock_PulseAI.git
cd Stock_PulseAI
```

### **2. Backend Setup**

#### **Create Virtual Environment**
```bash
# Create and activate conda environment
conda create -n stockpulse python=3.9 -y
conda activate stockpulse

# OR using venv
python -m venv stockpulse_env
source stockpulse_env/bin/activate  # On Windows: stockpulse_env\Scripts\activate
```

#### **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

#### **Environment Configuration**
Create a `.env` file in the root directory:
```bash
# Required API Keys
NEWSAPI=your_newsapi_key_here

# Optional: Database Configuration
DATABASE_URL=postgresql://username:password@localhost/stockpulse

# Optional: Reddit API (for enhanced social sentiment)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
```

**Get your NewsAPI key:**
1. Visit [NewsAPI.org](https://newsapi.org/)
2. Sign up for a free account
3. Copy your API key to the `.env` file

### **3. Frontend Setup**
```bash
cd frontend
npm install
```

### **4. Start the Application**

#### **Start Backend (Terminal 1)**
```bash
# From project root directory
conda activate stockpulse  # if using conda
uvicorn fastapi_service.main:app --reload --port 8080
```

#### **Start Frontend (Terminal 2)**
```bash
# From frontend directory
cd frontend
npm start
```

### **5. Access the Application**
- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **Alternative API Docs**: http://localhost:8080/redoc

## 📖 Usage

### **API Endpoints**
- **Technical Analysis**: `GET /api/stock/{ticker}/technical`
- **Sentiment Analysis**: `GET /api/stock/{ticker}/sentiment`
- **Stock Charts**: `GET /api/stock/{ticker}/graph`
- **Market Data**: `GET /api/sp500-realtime`

### **Example API Call**
```bash
curl -X 'GET' \
  'http://localhost:8080/api/stock/AAPL/sentiment' \
  -H 'accept: application/json'
```

## 📚 API Documentation

The FastAPI backend automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

These interfaces allow you to:
- Explore all available endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specifications

## 📁 Project Structure

```
Stock_PulseAI/
├── src/                          # Core application logic
│   ├── api_handler.py           # API route handlers
│   ├── sentiment/               # Sentiment analysis modules
│   ├── technical/               # Technical analysis tools
│   └── database/                # Database operations
├── fastapi_service/             # FastAPI application
│   ├── main.py                  # FastAPI app configuration
│   └── routes.py                # API route definitions
├── frontend/                    # React frontend application
│   ├── src/                     # React source code
│   ├── public/                  # Static assets
│   └── package.json             # Frontend dependencies
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md                    # Project documentation
```

## 🗺 Development Roadmap

### **✅ Completed**
- [x] FastAPI backend with sentiment analysis
- [x] React frontend foundation
- [x] Technical analysis (9-factor scoring)
- [x] News and Reddit sentiment analysis
- [x] Real-time market data integration
- [x] Interactive API documentation

### **🚧 In Progress**
- [ ] Enhanced FinBERT model integration (PyTorch 2.6+ compatibility)
- [ ] Advanced technical indicators
- [ ] User authentication and portfolios

### **📋 Planned Features**
- [ ] Macroeconomic data integration (FRED API)
- [ ] AI-powered price predictions
- [ ] Portfolio optimization tools
- [ ] Mobile-responsive enhancements
- [ ] Real-time notifications and alerts
- [ ] Advanced charting and analytics

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you have any questions or run into issues, please [open an issue](https://github.com/smundhra-git/Stock_PulseAI/issues) on GitHub.

---

**Made with ❤️ for smarter financial analysis**
