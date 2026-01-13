"""
Stock Prediction Script - FINAL FIXED VERSION
Run from backend folder: python scripts/predict.py
"""

import sys
import os

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Now import everything
import joblib
import pandas as pd
import numpy as np
import yfinance as yf

# Import from utils
from utils.data_processor import DataProcessor

# Import from same scripts folder
from news_analyzer import NewsAnalyzer

# Import config
from config import Config


def fetch_stock_data(symbol, period='6mo'):
    """
    Fetch stock data directly using yfinance
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        return df if not df.empty else None
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def predict_stock(symbol, company_name=''):
    """
    Make BUY/SELL prediction for a stock
    
    Combines:
    - ML model prediction (70% weight)
    - News sentiment (30% weight)
    
    Args:
        symbol: Stock ticker
        company_name: Company name for news search
    
    Returns:
        Dictionary with prediction results
    """
    
    try:
        # 1. Check if model exists
        model_path = os.path.join(parent_dir, Config.MODEL_DIR, f"{symbol}.pkl")
        
        if not os.path.exists(model_path):
            return {
                'symbol': symbol,
                'error': f'Model not found. Please train {symbol} first.\nRun: python scripts/train_models.py'
            }
        
        print(f"✓ Loading model...")
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        trained_accuracy = model_data.get('accuracy', 0)
        
        # 2. Fetch latest stock data
        print(f"✓ Fetching latest data for {symbol}...")
        df = fetch_stock_data(symbol, period='6mo')
        
        if df is None or len(df) < Config.LOOKBACK_DAYS:
            return {
                'symbol': symbol,
                'error': 'Could not fetch enough recent data'
            }
        
        # 3. Process data
        print("✓ Processing data...")
        processor = DataProcessor()
        processor.scaler = scaler  # Use saved scaler
        df = processor.create_features(df)
        
        # 4. Get latest sequence for prediction
        features = df.drop(['Target'], axis=1).select_dtypes(include=[np.number])
        scaled_features = scaler.transform(features)
        
        # Take last 60 days
        X_latest = scaled_features[-Config.LOOKBACK_DAYS:].reshape(
            1, Config.LOOKBACK_DAYS, -1
        )
        
        # 5. Model prediction
        print("✓ Running ML prediction...")
        model_prediction = float(model.predict(X_latest, verbose=0)[0][0])
        
        # 6. Fetch and analyze news
        print("✓ Analyzing news sentiment...")
        news_analyzer = NewsAnalyzer()
        articles = news_analyzer.fetch_stock_news(symbol, company_name)
        news_sentiment = news_analyzer.analyze_sentiment(articles)
        sentiment_label = news_analyzer.get_sentiment_label(news_sentiment)
        
        # 7. Combine predictions (70% model, 30% news)
        final_score = (model_prediction * 0.7) + ((news_sentiment + 1) / 2 * 0.3)
        
        # 8. Make decision
        action = "BUY 🟢" if final_score > 0.5 else "SELL 🔴"
        confidence = abs(final_score - 0.5) * 200  # Convert to percentage
        
        # 9. Get current price
        current_price = float(df['Close'].iloc[-1])
        
        # Return results
        return {
            'symbol': symbol,
            'action': action,
            'confidence': round(confidence, 1),
            'final_score': round(final_score, 3),
            'model_prediction': round(model_prediction, 3),
            'news_sentiment': round(news_sentiment, 3),
            'sentiment_label': sentiment_label,
            'current_price': round(current_price, 2),
            'news_count': len(articles),
            'trained_accuracy': round(trained_accuracy * 100, 1)
        }
        
    except Exception as e:
        import traceback
        return {
            'symbol': symbol,
            'error': str(e),
            'details': traceback.format_exc()
        }


if __name__ == "__main__":
    # Test prediction
    print("\n" + "="*70)
    print("  🔮 AI STOCK PREDICTION TEST")
    print("="*70 + "\n")
    
    symbol = input("Enter stock symbol (e.g., AAPL): ").upper().strip()
    
    if not symbol:
        print("❌ No symbol entered. Exiting.")
        sys.exit(1)
    
    company = input("Enter company name (optional): ").strip()
    
    print("\n" + "-"*70)
    result = predict_stock(symbol, company)
    print("-"*70 + "\n")
    
    print("="*70)
    print("  📊 PREDICTION RESULT")
    print("="*70)
    
    if 'error' in result:
        print(f"\n  ❌ Error: {result['error']}\n")
        if 'details' in result:
            print("Full error details:")
            print(result['details'])
    else:
        print(f"\n  📈 Stock: {result['symbol']}")
        print(f"  💰 Current Price: ${result['current_price']}")
        print(f"  🎯 Recommendation: {result['action']}")
        print(f"  📊 Confidence: {result['confidence']}%")
        print(f"  🤖 Model Score: {result['model_prediction']}")
        print(f"  📰 News Sentiment: {result['sentiment_label']} ({result['news_sentiment']})")
        print(f"  📄 News Articles: {result['news_count']}")
        print(f"  🎯 Model Accuracy: {result['trained_accuracy']}%")
    
    print("\n" + "="*70 + "\n")