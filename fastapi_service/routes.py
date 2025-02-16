from fastapi import APIRouter, HTTPException, Query
from src.api_handler import *
from fastapi.responses import JSONResponse
import json
router = APIRouter()


@router.get("/stock/{ticker}/technical")
async def get_stock_signal(ticker: str):
    """
    API endpoint to fetch stock data and return buy/sell/hold recommendation.
    """
    try:
        # Calculate score and recommendation
        signal, final_score = function(ticker)

        return {
            "ticker": ticker,
            "recommendation": signal,
            "score": final_score
        }

    except Exception as e:
        return {"error": str(e)}

@router.get("/stock/{ticker}/graph")
async def get_stock_line_graph(ticker: str, period: str = Query("1y", description="Time period: 1w, 1month, 3months, 6months, 1y, 5y, or max")):
    """
    Returns a JSON representation of a Plotly line chart for the given ticker and period.
    """
    try:
        fig = get_stock_graph(ticker, period)
        # Convert the figure to JSON
        fig_json = json.loads(fig.to_json())
        return JSONResponse(content=fig_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{ticker}/candlestick")
async def get_candlestick(ticker: str,
                          period: str = Query("1y", description="Time period: 1w, 1month, 3months, 6months, 1y, 5y, or max"),
                          interval: str = Query("1d", description="Aggregation interval: e.g. 1d, 2d, 5d, 1y")):
    """
    Returns a JSON representation of a Plotly candlestick chart for the given ticker, period, and interval.
    """
    try:
        fig = get_candlestick_chart(ticker, period, interval)
        # Convert the figure to JSON
        fig_json = json.loads(fig.to_json())
        return JSONResponse(content=fig_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
