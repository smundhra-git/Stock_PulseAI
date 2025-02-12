"""
Things to do here 
- Make a Database for the particular ticker if it does not exist already
- Delete Database Operation
- Get all relevant data from yfinance
- Use this data to do the particular things (technicals):
    - 1. Moving Averages
        1.  a) SMA
            b) EMA

            Buy: When the short-term moving average (e.g., 50-day) crosses above the long-term moving average (e.g., 200-day) → "Golden Cross."
            Sell: When the short-term moving average crosses below the long-term moving average → "Death Cross."
        
        2. MACD (need to calculate signal line)
            Buy: When the MACD crosses above the signal line.
            Sell: When the MACD crosses below the signal line.
        3. RSI
            Buy: When RSI is below 30 (oversold).
            Sell: When RSI is above 70 (overbought).
        4. Stochastic Oscillator
            Buy: When %K crosses above %D (3-day moving average of %K) below 20.
            Sell: When %K crosses below %D above 80.
        5. Bollinger Bands
            Buy: When price touches the lower band (oversold).
            Sell: When price touches the upper band (overbought).     
        6. VWAP
            Buy: When price is below VWAP and moving up.
            Sell: When price is above VWAP and moving down.

        7. On-Balance Volume (OBV)
            Buy: When OBV is rising with price.
            Sell: When OBV is falling with price.
            
        8. Donchian Channel Breakout
            Buy: When price breaks above the upper channel.
            Sell: When price breaks below the lower channel.

- For all these 9 strategies combined, we will give a +1 for Buy and a -1 for Sell
- If it is in above 2, we have buy, above 5 is a streong buy
- between 2 and -2 is a hold
- -2 to -5 is a sell, below -5 is a strong sell

How to do this -
-> Make a folder database with a database.py - it shall handle all database connections, deletions, and creations  --> DONE
-> Make a file to fetch_data -> using yfinance? explore other options --> Done and working
-> Make a file calculate_indicators -> use the data we have got from yfinance to do calculations
-> Make a file which will be linked to FastAPI, it shall fetch data, calculate indicators and then give out a buy/sell/etc only
->  if we run the ML models then shall give a price too
IDEA : RUN A LOGISTIC REGRESSION ON THE MACD, RSI indicators and see if it way work
-> Train an ARIMA model, if predicted_price > current_price by 10%, buy, else hold if < then sell



""" 
