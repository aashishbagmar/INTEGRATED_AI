import pandas as pd
import numpy as np
from ta import add_all_ta_features
from sklearn.preprocessing import MinMaxScaler

class DataProcessor:
    """
    Process raw stock data and create features for ML model
    """
    
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
    
    def clean_data(self, df):
        """
        Clean data by removing infinities and NaN values
        """
        # Replace infinities with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Forward fill then backward fill NaN values
        df = df.ffill().bfill()
        
        # If still NaN, drop those rows
        df = df.dropna()
        
        return df
    
    def add_technical_indicators(self, df):
        """
        Add technical analysis indicators using TA library
        
        Includes: RSI, MACD, Bollinger Bands, Stochastic, etc.
        """
        try:
            df = add_all_ta_features(
                df, 
                open="Open", 
                high="High", 
                low="Low", 
                close="Close", 
                volume="Volume",
                fillna=True
            )
        except Exception as e:
            print(f"Warning: Could not add all TA features: {e}")
        
        return df
    
    def create_features(self, df):
        """
        Create additional features for the model
        
        Features include:
        - Price changes (1d, 2d, 5d)
        - Moving averages (7, 21, 50 days)
        - Volume indicators
        - Technical indicators
        """
        
        # Make a copy to avoid fragmentation warning
        df = df.copy()
        
        # Add technical indicators
        df = self.add_technical_indicators(df)
        
        # Price change percentages
        df['Price_Change_1d'] = df['Close'].pct_change()
        df['Price_Change_2d'] = df['Close'].pct_change(periods=2)
        df['Price_Change_5d'] = df['Close'].pct_change(periods=5)
        
        # Moving averages
        df['MA_7'] = df['Close'].rolling(window=7).mean()
        df['MA_21'] = df['Close'].rolling(window=21).mean()
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        
        # Volume indicators
        df['Volume_Change'] = df['Volume'].pct_change()
        df['Volume_MA_7'] = df['Volume'].rolling(window=7).mean()
        
        # Price momentum
        df['Momentum_5'] = df['Close'] - df['Close'].shift(5)
        df['Momentum_10'] = df['Close'] - df['Close'].shift(10)
        
        # Volatility (standard deviation of returns)
        df['Volatility_7'] = df['Price_Change_1d'].rolling(window=7).std()
        df['Volatility_21'] = df['Price_Change_1d'].rolling(window=21).std()
        
        # Target variable: 1 if price goes up tomorrow, 0 if down
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # Clean data - remove infinities and NaN values
        df = self.clean_data(df)
        
        return df
    
    def prepare_sequences(self, df, lookback=60):
        """
        Prepare data sequences for LSTM model
        
        Args:
            df: DataFrame with features
            lookback: Number of days to look back
        
        Returns:
            X: Input sequences (3D array)
            y: Target values (1D array)
        """
        
        # Separate features and target
        features = df.drop(['Target'], axis=1).select_dtypes(include=[np.number])
        target = df['Target'].values
        
        # Scale features to 0-1 range
        scaled_features = self.scaler.fit_transform(features)
        
        # Create sequences
        X, y = [], []
        
        for i in range(lookback, len(scaled_features)):
            # Take 'lookback' days of data as input
            X.append(scaled_features[i-lookback:i])
            # Predict next day's direction
            y.append(target[i])
        
        return np.array(X), np.array(y)
    
    def get_latest_sequence(self, df, lookback=60):
        """
        Get the most recent sequence for prediction
        
        Used during live prediction
        """
        features = df.select_dtypes(include=[np.number])
        scaled_features = self.scaler.transform(features)
        
        # Get last 'lookback' days
        latest_sequence = scaled_features[-lookback:]
        
        return latest_sequence.reshape(1, lookback, -1)