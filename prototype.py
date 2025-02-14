import pandas as pd
import yfinance as yf
# from yahoofinancials import YahooFinancials

tesla_df = yf.download('TSLA', start = '2019-01-01', end = '2019-12-21')
print(tesla_df.head())
