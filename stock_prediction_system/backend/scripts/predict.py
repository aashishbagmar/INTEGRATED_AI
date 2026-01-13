"""
Stock Prediction Script
Run from backend folder: python scripts/predict.py
"""

import sys
import os

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Standard imports
import joblib
import pandas as pd
import numpy as np
import yfinance as yf

# Local imports
from utils.data_processor import DataProcessor
from news_analyzer import NewsAnalyzer
from config import Config


def fetch_stock_data(symbol, period='6mo'):
    """Fetch stock data using yfinance"""
    try:
        print(f"  Downloading {symbol} data...")
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        if df.empty:
            return None
        print(f"  ✓ Got {len(df)} days of data")
        return df
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


def predict_stock(symbol, company_name=''):
    """
    Predict BUY/SELL for a stock
    
    Args:
        symbol: Stock ticker (e.g., 'AAPL')
        company_name: Company name for news
    
    Returns:
        Dictionary with prediction results
    """
    
    print(f"\n{'='*70}")
    print(f"  Analyzing {symbol}...")
    print('='*70 + "\n")
    
    try:
        # 1. Load model
        model_path = os.path.join(parent_dir, Config.MODEL_DIR, f"{symbol}.pkl")
        
        if not os.path.exists(model_path):
            return {
                'symbol': symbol,
                'error': f'Model not trained. Run: python scripts/train_models.py'
            }
        
        print("✓ Loading trained model...")
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        accuracy = model_data.get('accuracy', 0)
        
        # 2. Fetch data
        print("✓ Fetching latest stock data...")
        df = fetch_stock_data(symbol, period='6mo')
        
        if df is None or len(df) < Config.LOOKBACK_DAYS:
            return {
                'symbol': symbol,
                'error': 'Not enough data available'
            }
        
        # 3. Process
        print("✓ Processing features...")
        processor = DataProcessor()
        processor.scaler = scaler
        df = processor.create_features(df)
        
        # 4. Prepare input
        features = df.drop(['Target'], axis=1).select_dtypes(include=[np.number])
        scaled = scaler.transform(features)
        X = scaled[-Config.LOOKBACK_DAYS:].reshape(1, Config.LOOKBACK_DAYS, -1)
        
        # 5. Predict
        print("✓ Running ML prediction...")
        ml_score = float(model.predict(X, verbose=0)[0][0])
        
        # 6. News sentiment
        print("✓ Analyzing news...")
        try:
            news_analyzer = NewsAnalyzer()
            articles = news_analyzer.fetch_stock_news(symbol, company_name)
            sentiment = news_analyzer.analyze_sentiment(articles)
            sentiment_label = news_analyzer.get_sentiment_label(sentiment)
            news_count = len(articles)
        except Exception as e:
            print(f"  Warning: News analysis failed ({e})")
            sentiment = 0.0
            sentiment_label = "Neutral ➖"
            news_count = 0
        
        # 7. Combine (70% ML, 30% news)
        final_score = (ml_score * 0.7) + ((sentiment + 1) / 2 * 0.3)
        
        # 8. Decision
        action = "BUY 🟢" if final_score > 0.5 else "SELL 🔴"
        confidence = abs(final_score - 0.5) * 200
        
        # 9. Current price
        price = float(df['Close'].iloc[-1])
        
        return {
            'symbol': symbol,
            'action': action,
            'confidence': round(confidence, 1),
            'model_prediction': round(ml_score, 3),
            'news_sentiment': round(sentiment, 3),
            'sentiment_label': sentiment_label,
            'current_price': round(price, 2),
            'news_count': news_count,
            'trained_accuracy': round(accuracy * 100, 1)
        }
        
    except Exception as e:
        import traceback
        return {
            'symbol': symbol,
            'error': str(e),
            'trace': traceback.format_exc()
        }


def main():
    """Main function"""
    print("\n" + "="*70)
    print("  🔮 AI STOCK PREDICTOR")
    print("="*70 + "\n")
    
    symbol = input("Enter stock symbol (e.g., AAPL): ").upper().strip()
    
    if not symbol:
        print("No symbol entered. Exiting.\n")
        return
    
    company = input("Enter company name (optional): ").strip()
    
    result = predict_stock(symbol, company)
    
    print("\n" + "="*70)
    print("  📊 RESULT")
    print("="*70 + "\n")
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}\n")
        if 'trace' in result:
            print("Details:")
            print(result['trace'])
    else:
        print(f"Stock:        {result['symbol']}")
        print(f"Price:        ${result['current_price']}")
        print(f"Action:       {result['action']}")
        print(f"Confidence:   {result['confidence']}%")
        print(f"ML Score:     {result['model_prediction']}")
        print(f"Sentiment:    {result['sentiment_label']}")
        print(f"News Count:   {result['news_count']}")
        print(f"Accuracy:     {result['trained_accuracy']}%")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...\n")
    except Exception as e:
        print(f"\nUnexpected error: {e}\n")