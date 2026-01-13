"""
Thin wrapper for sentiment analysis
Used by CLI / main.py (non-Flask usage)
"""

# import the function that already exists in multi_page_app.py
from .multi_page_app import analyze_sentiment_only


def get_sentiment(symbol):
    """
    Public API for sentiment analysis (CLI friendly)
    """
    # Use last 7 days by default
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    from_date = (now - timedelta(days=7)).isoformat()
    to_date = now.isoformat()

    results, overall_signal, total, error = analyze_sentiment_only(
        symbol,
        from_date,
        to_date
    )

    if error or not results:
        return {
            "label": "Neutral",
            "score": 0,
            "confidence": 0
        }

    # Convert signal to numeric score
    score_map = {
        "Positive": 1,
        "Neutral": 0,
        "Negative": -1
    }

    score = score_map.get(overall_signal, 0)
    confidence = min(90, max(40, total))  # simple heuristic

    return {
        "label": overall_signal.upper(),
        "score": score,
        "confidence": confidence
    }
