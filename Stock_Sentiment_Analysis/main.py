
# from .services.price_service import get_price_forecast
# from .services.sentiment_service import get_sentiment
# from .decision.decision_engine import make_final_decision


# def main():
#     symbol = input("Enter Stock Symbol (e.g., TCS, RELIANCE): ").strip().upper()

#     price_result = get_price_forecast(symbol)
#     if not price_result:
#         print("❌ Price model failed")
#         return

#     sentiment_result = get_sentiment(symbol)

#     final = make_final_decision(price_result, sentiment_result)

#     print("\n📰 SENTIMENT DETAILS")
#     print("-" * 40)

#     counts = sentiment_result["counts"]
#     news = sentiment_result["news"]

#     print(f"Total News: {sum(counts.values())}")
#     print(f"Positive: {counts['positive']}")
#     print(f"Negative: {counts['negative']}")
#     print(f"Neutral : {counts['neutral']}")

#     def print_news(label, items):
#         if not items:
#             return
#         print(f"\n🔹 {label.upper()} NEWS:")
#         for i, title in enumerate(items, 1):
#             print(f"  {i}. {title}")

#     print_news("Positive", news["positive"])
#     print_news("Negative", news["negative"])
#     print_news("Neutral", news["neutral"])



#     print("\n📊 FINAL DECISION REPORT")
#     print("-" * 40)
#     print(f"Stock: {price_result['symbol']}")
#     print(f"Current Price: {price_result['current_price']}")
#     print(f"Volatility: {price_result['volatility']}")
#     print(f"Sentiment: {sentiment_result['sentiment']}")
#     print(f"Decision: {final['decision']}")
#     print("-" * 40)


# if __name__ == "__main__":
#     main()





# main.py

from .services.price_service import get_price_forecast
from .services.sentiment_service import get_sentiment
from .decision.decision_engine import make_final_decision


def main():
    symbol = input("Enter Stock Symbol (e.g., TCS, RELIANCE, AAPL): ").strip().upper()

    # =================================================
    # 1️⃣ AI PRICE PREDICTION (ONLY AI)
    # =================================================
    price_result = get_price_forecast(symbol)
    if not price_result:
        print("❌ AI price prediction failed")
        return

    print("\n📊 AI PRICE PREDICTION")
    print("=" * 45)
    print(f"Stock              : {price_result['symbol']}")
    print(f"Current Price      : {price_result['current_price']}")
    print(f"Predicted Price(30d)    : {price_result['predicted_price']}")
    print(f"Trend (%)          : {price_result['trend_pct']}")
    print(f"Volatility         : {price_result['volatility']}")
    print(f"AI Signal          : {price_result['signal']}")
    print("=" * 45)

    # =================================================
    # 2️⃣ SENTIMENT ANALYSIS (ONLY NEWS)
    # =================================================
    sentiment_result = get_sentiment(symbol)

    print("\n📰 SENTIMENT ANALYSIS")
    print("=" * 45)
    print(f"Total News         : {sentiment_result['total']}")
    print(f"Positive News      : {sentiment_result['counts']['positive']}")
    print(f"Negative News      : {sentiment_result['counts']['negative']}")
    print(f"Neutral News       : {sentiment_result['counts']['neutral']}")
    print(f"Overall Sentiment  : {sentiment_result['sentiment']}")
    print("=" * 45)

    # Optional: print actual headlines
    for category in ["positive", "negative", "neutral"]:
        news_list = sentiment_result["news"][category]
        if news_list:
            print(f"\n🔹 {category.upper()} NEWS:")
            for i, title in enumerate(news_list, 1):
                print(f"  {i}. {title}")

    # =================================================
    # 3️⃣ FINAL INTEGRATED DECISION (AI + SENTIMENT)
    # =================================================
    final = make_final_decision(price_result, sentiment_result)

    print("\n🤝 FINAL INTEGRATED DECISION")
    print("=" * 45)
    print(f"AI Signal          : {price_result['signal']}")
    print(f"Sentiment          : {sentiment_result['sentiment']}")
    print("-" * 45)
    print(f"📌 FINAL DECISION  : {final['decision']}")
    print("=" * 45)


if __name__ == "__main__":
    main()
