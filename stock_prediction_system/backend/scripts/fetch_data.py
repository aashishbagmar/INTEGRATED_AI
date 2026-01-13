import sys
import os

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import yfinance as yf
import pandas as pd
from config import Config


def fetch_stock_data(symbol, period='2y'):
    """
    Fetch historical stock data using yfinance
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        period: Time period ('1y', '2y', '5y', etc.)
    
    Returns:
        DataFrame with stock data or None if failed
    """
    try:
        print(f"   Downloading {symbol}...", end=" ")
        
        # Download stock data
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            print(f" No data available")
            return None
        
        # Create data directory if it doesn't exist
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # Save to CSV
        file_path = os.path.join(Config.DATA_DIR, f"{symbol}.csv")
        df.to_csv(file_path)
        
        print(f"✅ ({len(df)} days)")
        return df
        
    except Exception as e:
        print(f" Error: {str(e)}")
        return None

def fetch_all_stocks():
    """
    Fetch historical data for all stocks in Config.STOCK_SYMBOLS
    """
    total_stocks = len(Config.STOCK_SYMBOLS)
    print(f"\n{'='*60}")
    print(f"   STOCK DATA DOWNLOAD")
    print(f"{'='*60}")
    print(f"  Total stocks to download: {total_stocks}")
    print(f"  Period: Last 2 years")
    print(f"{'='*60}\n")
    
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(Config.STOCK_SYMBOLS, 1):
        print(f"[{i}/{total_stocks}]", end=" ")
        
        result = fetch_stock_data(symbol)
        
        if result is not None:
            successful += 1
        else:
            failed += 1
        
        # Small delay to avoid rate limiting
        if i % 10 == 0:
            print(f"\n    Short pause (avoiding rate limits)...\n")
            time.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"   DOWNLOAD COMPLETE")
    print(f"{'='*60}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {failed}")
    print(f"   Files saved in: {Config.DATA_DIR}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    print("\n Starting data download process...")
    fetch_all_stocks()
    print(" All done! You can now train the models.\n")