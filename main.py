from stock_prediction_system.backend.scripts import get_price_forecast
from Market_Sentiment_Analysis import get_sentiment
from decision_engine import make_final_decision

def main():
    symbol = input("Enter Stock Symbol (e.g., TCS, RELIANCE): ").strip().upper()

    print("\n🔹 Running Price Forecast Model...")
    price_data = get_price_forecast(symbol)

    if not price_data:
        print("❌ Price forecast failed")
        return

    print("\n🔹 Running News Sentiment Analysis...")
    sentiment_data = get_sentiment(symbol)

    print("\n🔹 Integrating Models...")
    final = make_final_decision(price_data, sentiment_data)

    print("\n" + "=" * 60)
    print("📊 FINAL AI DECISION REPORT")
    print("=" * 60)

    print(f"Stock: {symbol}")
    print(f"Current Price: ₹{price_data['current_price']:.2f}")
    print(f"Volatility: {price_data['volatility']:.2f}%")

    print("\nNews Sentiment:")
    print(f"• Sentiment: {sentiment_data['label']}")
    print(f"• Confidence: {sentiment_data['confidence']}%")

    print("\n🎯 FINAL DECISION:")
    print(f"→ {final['decision']}")
    print(f"→ Final Score: {final['final_score']}")

    print("\nDisclaimer: AI-based prediction. Not financial advice.")

if __name__ == "__main__":
    main()
