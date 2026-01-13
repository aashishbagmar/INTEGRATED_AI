def make_final_decision(price_data: dict, sentiment_data: dict):
    """
    Combine AI price prediction and weighted sentiment
    into a final investment decision.
    """

    score = 0.0

    # -----------------------------------
    # PRICE SIGNAL CONTRIBUTION (AI)
    # -----------------------------------
    if price_data["signal"] == "Bullish":
        score += 1.2
    elif price_data["signal"] == "Bearish":
        score -= 1.2
    # Neutral → no change

    # -----------------------------------
    # SENTIMENT CONTRIBUTION (WEIGHTED)
    # -----------------------------------
    weighted_sentiment = sentiment_data.get("weighted_score", 0)

    if weighted_sentiment > 1.0:
        score += 1.3
    elif weighted_sentiment > 0.3:
        score += 0.6
    elif weighted_sentiment < -1.0:
        score -= 1.5
    elif weighted_sentiment < -0.3:
        score -= 0.6
    # Neutral zone → no change

    # -----------------------------------
    # FINAL DECISION LOGIC
    # -----------------------------------
    if score >= 2.0:
        decision = "BUY"
    elif score <= -2.0:
        decision = "SELL"
    else:
        decision = "HOLD"

    return {
        "decision": decision,
        "confidence_score": round(score, 2),
        "price_signal": price_data["signal"],
        "sentiment": sentiment_data["sentiment"],
        "weighted_sentiment": weighted_sentiment
    }
