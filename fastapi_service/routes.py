from fastapi import APIRouter
from src.technical.api_handler import *
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
