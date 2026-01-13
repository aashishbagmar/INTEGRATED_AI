import yfinance as yf
import requests

# Force a clean Yahoo session (CRITICAL)
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})
yf.utils.get_yahoo_session = lambda: session

"""
Stock Price Forecaster - Predict Future Prices with Confidence (Indian Market)
Run: python scripts/price_forecast.py
"""

import sys
import os

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
sys.path.insert(0, backend_dir)

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')


class PriceForecaster:
    """Forecast future stock prices for Indian market"""
    
    def __init__(self, symbol):
        # Add .NS suffix for NSE stocks if not present
        self.symbol = symbol.upper()
        if not (self.symbol.endswith('.NS') or self.symbol.endswith('.BO')):
            self.symbol = f"{self.symbol}.NS"
        
        self.current_price = None
        self.historical_data = None
        self.models = {}
        self.volatility = None
    
    def fetch_live_data(self, period='5y'):
        """Fetch live stock data from Indian exchanges with fallback support"""
        try:
            print(f"\n📡 Fetching live data for {self.symbol}...")

            df = None
            used_period = None

            # Use yf.download instead of Ticker().history (CRITICAL FIX)
            for p in ["5y", "2y", "1y", "6mo"]:
                temp_df = yf.download(
                    self.symbol,
                    period=p,
                    interval="1d",
                    auto_adjust=False,
                    progress=False,
                    threads=False
                )

                if not temp_df.empty:
                    df = temp_df
                    used_period = p
                    break

            if df is None or df.empty:
                print(f"❌ No data available for {self.symbol}")
                print("💡 Tip: For NSE stocks use symbol (e.g., RELIANCE), for BSE add .BO (e.g., RELIANCE.BO)")
                return False

            # Store historical data
            self.historical_data = df
            self.current_price = float(df["Close"].iloc[-1])

            # Calculate volatility
            self.volatility = df["Close"].pct_change().std() * 100

            # Get company info (safe, optional)
            try:
                stock = yf.Ticker(self.symbol)
                info = stock.info
                company_name = info.get("longName", self.symbol)
                market_cap = info.get("marketCap", 0)
            except Exception:
                company_name = self.symbol
                market_cap = 0

            # Display results
            print("✅ Live Data Retrieved!")
            print(f"   Company: {company_name}")
            print(f"   Current Price: ₹{self.current_price:.2f}")
            print(f"   Data Points: {len(df)} days")
            print(f"   Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
            print(f"   Data Period Used: {used_period}")

            if market_cap > 0:
                market_cap_crores = market_cap / 1e7
                if market_cap_crores > 1000:
                    print(f"   Market Cap: ₹{market_cap_crores / 100:.2f} Lakh Crores")
                else:
                    print(f"   Market Cap: ₹{market_cap_crores:.2f} Crores")

            return True

        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return False


    def calculate_growth_rate(self):
        """Calculate historical growth rate"""
        if self.historical_data is None:
            return None
        
        # Calculate CAGR (Compound Annual Growth Rate)
        start_price = float(self.historical_data['Close'].iloc[0])
        end_price = self.current_price
        years = len(self.historical_data) / 252  # Trading days per year
        
        if start_price > 0 and years > 0:
            cagr = ((end_price / start_price) ** (1/years) - 1) * 100
            return cagr
        return 0
    
    def calculate_confidence(self, days_ahead):
        """
        Calculate confidence score for a prediction
        Based on: volatility, prediction horizon, and model agreement
        Returns: confidence score (0-100%) and label
        """
        # Factor 1: Time horizon (confidence decreases with time)
        if days_ahead <= 30:
            time_factor = 1.0
        elif days_ahead <= 180:
            time_factor = 0.85
        elif days_ahead <= 365:
            time_factor = 0.70
        elif days_ahead <= 730:
            time_factor = 0.55
        else:
            time_factor = 0.40
        
        # Factor 2: Volatility (lower volatility = higher confidence)
        # Indian stocks tend to be more volatile, so adjusted thresholds
        if self.volatility < 2.0:
            vol_factor = 1.0
        elif self.volatility < 3.0:
            vol_factor = 0.8
        elif self.volatility < 4.5:
            vol_factor = 0.6
        else:
            vol_factor = 0.4
        
        # Factor 3: Data quality (more historical data = higher confidence)
        data_years = len(self.historical_data) / 252
        if data_years >= 5:
            data_factor = 1.0
        elif data_years >= 3:
            data_factor = 0.9
        elif data_years >= 1:
            data_factor = 0.75
        else:
            data_factor = 0.6
        
        # Calculate overall confidence score
        confidence_score = (time_factor * 0.5 + vol_factor * 0.35 + data_factor * 0.15) * 100
        
        # Determine confidence label
        if confidence_score >= 75:
            label = "High"
        elif confidence_score >= 60:
            label = "Medium-High"
        elif confidence_score >= 45:
            label = "Medium"
        elif confidence_score >= 30:
            label = "Medium-Low"
        else:
            label = "Low"
        
        return confidence_score, label
    
    def train_models(self):
        """Train prediction models"""
        print("\n🤖 Training AI models...")
        
        df = self.historical_data.copy()
        
        # Prepare features
        df['Days'] = np.arange(len(df))
        df['MA_50'] = df['Close'].rolling(window=50).mean()
        df['MA_200'] = df['Close'].rolling(window=200).mean()
        df['Volatility'] = df['Close'].rolling(window=30).std()
        df = df.dropna()
        
        X = df[['Days', 'MA_50', 'MA_200', 'Volatility']].values
        y = df['Close'].values
        
        # Train Linear Regression (for trend)
        self.models['linear'] = LinearRegression()
        self.models['linear'].fit(X, y)
        
        # Train Random Forest (for complex patterns)
        self.models['rf'] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models['rf'].fit(X, y)
        
        print("✅ Models trained successfully!")
        
        return True
    
    def predict_future_price(self, days_ahead):
        """Predict price N days in the future"""
        
        df = self.historical_data.copy()
        
        # Get latest features
        last_day = len(df)
        future_day = last_day + days_ahead
        
        last_ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        last_ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        last_vol = df['Close'].rolling(window=30).std().iloc[-1]
        
        # Create future feature vector
        future_features = np.array([[
            future_day,
            last_ma50,
            last_ma200,
            last_vol
        ]])
        
        # Get predictions from both models
        linear_pred = self.models['linear'].predict(future_features)[0]
        rf_pred = self.models['rf'].predict(future_features)[0]
        
        # Ensemble: Average of both models
        ensemble_pred = (linear_pred * 0.5) + (rf_pred * 0.5)
        
        # Apply growth rate adjustment
        cagr = self.calculate_growth_rate()
        years = days_ahead / 365.25
        growth_factor = (1 + cagr/100) ** years
        
        # Final prediction (blend ensemble with growth projection)
        final_pred = (ensemble_pred * 0.6) + (self.current_price * growth_factor * 0.4)
        
        return final_pred


    def forecast_multiple_periods(self):
        """Forecast prices for multiple time periods"""
        
        if not self.train_models():
            return None
        
        print("\n" + "="*85)
        print("  📈 PRICE FORECAST - INDIAN STOCK MARKET")
        print("="*85)
        
        periods = {
            '1 Month': 30,
            '3 Months': 90,
            '6 Months': 180,
            '1 Year': 365,
            '2 Years': 730,
            '5 Years': 1825,
            '10 Years': 3650
        }
        
        results = {}
        cagr = self.calculate_growth_rate()
        
        print(f"\n📊 Current Price: ₹{self.current_price:.2f}")
        print(f"📈 Historical Growth Rate (CAGR): {cagr:.2f}%")
        print(f"📉 Volatility: {self.volatility:.2f}%")
        print("\n" + "-"*85)
        print(f"{'Period':<12} {'Predicted':<12} {'Change':<15} {'ROI':<12} {'Confidence'}")
        print("-"*85)
        
        for period_name, days in periods.items():
            predicted_price = self.predict_future_price(days)
            change = predicted_price - self.current_price
            change_pct = (change / self.current_price) * 100
            
            # Calculate confidence for this time period
            conf_score, conf_label = self.calculate_confidence(days)
            
            results[period_name] = {
                'price': predicted_price,
                'change': change,
                'change_pct': change_pct,
                'confidence_score': conf_score,
                'confidence_label': conf_label
            }
            
            # Color coding
            arrow = "🟢" if change > 0 else "🔴"
            sign = "+" if change > 0 else ""
            
            print(f"{period_name:<12} ₹{predicted_price:>8.2f}  {arrow} {sign}₹{change:>7.2f}  {sign}{change_pct:>6.1f}%    {conf_score:>5.1f}% ({conf_label})")
        
        print("-"*85)
        
        # Investment simulation
        print("\n💰 INVESTMENT SIMULATION (₹1,00,000 Initial Investment)")
        print("-"*85)
        investment = 100000
        
        for period_name, data in results.items():
            future_value = investment * (1 + data['change_pct']/100)
            profit = future_value - investment
            conf_label = data['confidence_label']
            
            print(f"{period_name:<12} ₹{investment:>8,.0f} → ₹{future_value:>10,.0f}  (Profit: ₹{profit:>8,.0f})  [{conf_label}]")
        
        print("="*85)
        
        # Overall confidence analysis
        print("\n🎯 CONFIDENCE INTERPRETATION")
        print("-"*85)
        print("High (75%+):        Strong confidence based on low volatility & short horizon")
        print("Medium-High (60%+): Good confidence with moderate uncertainty")
        print("Medium (45%+):      Fair confidence with notable uncertainty")
        print("Medium-Low (30%+):  Limited confidence due to long horizon/volatility")
        print("Low (<30%):         Minimal confidence - very speculative")
        
        print("\n⚠️  DISCLAIMER")
        print("-"*85)
        print("This is an AI-based prediction and NOT financial advice.")
        print("Stock prices are influenced by many unpredictable factors.")
        print("Indian markets are subject to regulatory, economic, and global factors.")
        print("Past performance does not guarantee future results.")
        print("Confidence scores indicate prediction reliability, not certainty.")
        print("Always consult a SEBI-registered financial advisor before investing.")
        print("="*85 + "\n")
        
        return results


def main():
    """Main function"""
    
    print("\n" + "="*85)
    print("  🚀 AI STOCK PRICE FORECASTER - INDIAN MARKET (With Confidence Scores)")
    print("="*85)
    print("\n  Predict future stock prices using AI & historical data")
    print("  Supports NSE and BSE listed stocks")
    print("="*85 + "\n")
    
    symbol = input("Enter stock symbol (e.g., RELIANCE, TCS, INFY): ").strip().upper()
    
    if not symbol:
        print("\n❌ No symbol entered. Exiting.\n")
        return
    
    # Ask for exchange if not specified
    if not (symbol.endswith('.NS') or symbol.endswith('.BO')):
        print("\n📍 Select Exchange:")
        print("   1. NSE (National Stock Exchange) - Default")
        print("   2. BSE (Bombay Stock Exchange)")
        choice = input("Enter choice (1 or 2, press Enter for NSE): ").strip()
        
        if choice == '2':
            symbol = f"{symbol}.BO"
        else:
            symbol = f"{symbol}.NS"
    
    # Create forecaster
    forecaster = PriceForecaster(symbol)
    
    # Fetch live data
    if not forecaster.fetch_live_data():
        return
    
    # Generate forecast
    print("\n⏳ Generating predictions...")
    forecaster.forecast_multiple_periods()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted. Exiting...\n")
    except Exception as e:

        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()



# ===============================
# Data interface for integration
# ===============================
def get_price_forecast(symbol):
    forecaster = PriceForecaster(symbol)

    if not forecaster.fetch_live_data():
        return None

    results = forecaster.forecast_multiple_periods()

    return {
        "symbol": symbol,
        "current_price": forecaster.current_price,
        "volatility": forecaster.volatility,
        "forecast": results
    }