import sys
import os

# Fix import paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import pandas as pd
import joblib
from config import Config
from utils.data_processor import DataProcessor
from utils.model_builder import train_model


def train_single_stock(symbol):
    """
    Train a model for a single stock symbol
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n{'='*50}")
        print(f"Training model for {symbol}")
        print(f"{'='*50}")
        
        # Download data
        print(f"Downloading data for {symbol}...")
        df = yf.download(symbol, period='2y', progress=False)
        
        if df.empty or len(df) < 100:
            print(f"❌ Insufficient data for {symbol}")
            return False
        
        # Reset index to make sure we have a clean DataFrame
        df = df.reset_index()
        
        # Initialize processor
        processor = DataProcessor()
        
        # Create features
        print(f"Creating features for {symbol}...")
        df = processor.create_features(df)
        
        if len(df) < Config.LOOKBACK_DAYS + 10:
            print(f"❌ Not enough data after feature creation for {symbol}")
            return False
        
        # Prepare sequences
        print(f"Preparing sequences for {symbol}...")
        X, y = processor.prepare_sequences(df, lookback=Config.LOOKBACK_DAYS)
        
        # Split data
        split_idx = int(len(X) * Config.TRAIN_TEST_SPLIT)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"Training data shape: {X_train.shape}")
        print(f"Testing data shape: {X_test.shape}")
        
        # Build model
        print(f"Building LSTM model for {symbol}...")
        model_builder = ModelBuilder(lookback_days=Config.LOOKBACK_DAYS)
        model = model_builder.build_lstm_model(input_shape=(X_train.shape[1], X_train.shape[2]))
        
        # Train model
        print(f"Training model for {symbol}...")
        history = model_builder.train_model(
            X_train, y_train,
            X_test, y_test,
            epochs=Config.EPOCHS,
            batch_size=Config.BATCH_SIZE,
            model_save_path=f"{Config.MODEL_DIR}{symbol.replace('.', '_')}_model.h5"
        )
        
        # Evaluate
        print(f"Evaluating model for {symbol}...")
        results = model_builder.evaluate_model(X_test, y_test)
        
        print(f"✅ {symbol} - RMSE: {results['rmse']:.4f}, MAE: {results['mae']:.4f}")
        
        # Save scaler
        scaler_path = f"{Config.MODEL_DIR}{symbol.replace('.', '_')}_scaler.pkl"
        joblib.dump(processor.scaler, scaler_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error training {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Main training function - trains models for all stocks
    """
    print("\n" + "="*60)
    print("STOCK PREDICTION MODEL TRAINING")
    print("="*60)
    
    # Create directories if they don't exist
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    
    # Get stock symbols
    symbols = Config.STOCK_SYMBOLS
    print(f"\nTotal stocks to train: {len(symbols)}")
    
    # Train models
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        
        if train_single_stock(symbol):
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)
    print(f"Successfully trained: {successful}")
    print(f"Failed: {failed}")
    print(f"Models saved in: {Config.MODEL_DIR}")
    print("Ready for predictions!")
    print("="*60)


if __name__ == "__main__":
    main()