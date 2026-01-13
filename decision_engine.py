def make_final_decision(price_data, sentiment_data):
    """
    Fuse price forecast + sentiment into final decision
    """

    # ---- Price signal (1Y horizon) ----
    one_year = price_data["forecast"].get("1 Year")
    price_signal = 1 if one_year and one_year["change_pct"] > 0 else -1

    # ---- Sentiment signal ----
    sentiment_signal = sentiment_data["score"]  # already -1 to +1

    # ---- Weighted fusion ----
    final_score = (0.65 * price_signal) + (0.35 * sentiment_signal)

    if final_score >= 0.7:
        decision = "STRONG BUY"
    elif final_score >= 0.3:
        decision = "BUY"
    elif final_score > -0.3:
        decision = "HOLD"
    elif final_score > -0.7:
        decision = "SELL"
    else:
        decision = "STRONG SELL"

    return {
        "final_score": round(final_score, 2),
        "decision": decision
    }
