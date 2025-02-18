from fastapi import APIRouter, HTTPException, Query
from src.api_handler import *
from fastapi.responses import JSONResponse
import json
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from src.database.auth import signup_user, verify_token, authenticate_user
import yfinance as yf


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



# User models
class UserSignup(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/signup")
async def register_user(user: UserSignup):
    """
    Registers a new user by calling the `signup_user` function from db_operations.
    """
    result = signup_user(user.username, user.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result, status_code=201)


@router.post("/login")
async def login_user(user: UserLogin):
    """
    Authenticates a user and returns a JWT token.
    Calls `authenticate_user` function from db_operations.
    """
    result = authenticate_user(user.username, user.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return JSONResponse(content=result, status_code=200)


@router.get("/protected")
async def protected_route(token: str):
    """
    Example protected route that requires authentication.
    Calls `verify_token` from db_operations.
    """
    result = verify_token(token)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return JSONResponse(content={"message": f"Welcome {result['username']}!"}, status_code=200)




@router.get("/sp500-realtime")
def get_sp500_realtime(interval: str = Query("1m", description="Time interval: 1m, 2m, 5m, 15m, 1h, 1d, etc.")):
    result = get_market_data(market="^GSPC", period='1d')
    return JSONResponse(content=result)