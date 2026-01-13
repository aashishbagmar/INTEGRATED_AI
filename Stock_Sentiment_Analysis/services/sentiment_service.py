# services/sentiment_service.py

from transformers import pipeline

# --------------------------------------------------
# Load sentiment model ONCE (VERY IMPORTANT)
# --------------------------------------------------
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# --------------------------------------------------
# News Fetcher (replace with NewsAPI / Google News later)
# --------------------------------------------------
def get_news(symbol: str, limit: int = 20):
    """
    Fetch latest news headlines for a stock symbol.
    TEMP fallback headlines (replace with API later).
    Order matters: index 0 = most recent.
    """
    return [
        f"{symbol} stock shows strong quarterly performance",
        f"{symbol} faces regulatory pressure from authorities",
        f"Analysts remain cautious on {symbol} valuation",
        f"{symbol} reports stable earnings amid market volatility",
        f"Market sentiment mixed for {symbol} investors"
    ][:limit]


# --------------------------------------------------
# Sentiment Analysis Service (WEIGHTED)
# --------------------------------------------------
def get_sentiment(symbol: str):
    print("\n📰 Running sentiment analysis...")

    headlines = get_news(symbol)

    # Safety check
    if not headlines:
        return {
            "sentiment": "Neutral",
            "counts": {"positive": 0, "negative": 0, "neutral": 0},
            "news": {"positive": [], "negative": [], "neutral": []},
            "total": 0,
            "score": 0.0,
            "weighted_score": 0.0
        }

    # Run transformer model
    results = sentiment_pipeline(headlines)

    positive_news = []
    negative_news = []
    neutral_news = []

    weighted_score = 0.0

    # --------------------------------------------------
    # Classify + WEIGHT each headline
    # --------------------------------------------------
    for idx, (headline, result) in enumerate(zip(headlines, results)):
        label = result["label"]
        confidence = result["score"]

        # -------- Recency Weight --------
        # Latest news has more impact
        if idx == 0:
            recency_weight = 1.4
        elif idx <= 2:
            recency_weight = 1.2
        else:
            recency_weight = 1.0

        # -------- Sentiment Logic --------
        if label == "POSITIVE" and confidence >= 0.6:
            positive_news.append(headline)
            weighted_score += 1.0 * recency_weight

        elif label == "NEGATIVE" and confidence >= 0.6:
            negative_news.append(headline)
            weighted_score -= 1.3 * recency_weight  # negatives hurt more

        else:
            neutral_news.append(headline)

    positive = len(positive_news)
    negative = len(negative_news)
    neutral = len(neutral_news)
    total = positive + negative + neutral

    # --------------------------------------------------
    # Overall sentiment (WEIGHT-AWARE)
    # --------------------------------------------------
    if weighted_score > 0.5:
        overall = "Positive"
    elif weighted_score < -0.5:
        overall = "Negative"
    else:
        overall = "Neutral"

    # Normalized score (-1 to +1)
    score = round((positive - negative) / total, 2) if total > 0 else 0.0

    print("✅ Sentiment analysis completed")

    # --------------------------------------------------
    # FINAL RETURN (used by main.py & decision_engine.py)
    # --------------------------------------------------
    return {
        "sentiment": overall,
        "counts": {
            "positive": positive,
            "negative": negative,
            "neutral": neutral
        },
        "news": {
            "positive": positive_news,
            "negative": negative_news,
            "neutral": neutral_news
        },
        "total": total,
        "score": score,                     # simple ratio
        "weighted_score": round(weighted_score, 2)  # IMPORTANT for decision engine
    }
