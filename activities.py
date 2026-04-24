# activities.py

import requests
from transformers import pipeline
import numpy as np
from temporalio import activity

HEADERS = {"User-Agent": "Mozilla/5.0"}

@activity.defn
def scrape_reviews(app_id: str):
    url = f"https://store.steampowered.com/appreviews/{app_id}"
    params = {
        "json": 1,
        "num_per_page": 100,
        "filter": "recent",
        "language": "english",
        "purchase_type": "all",
    }
    res = requests.get(url, params=params, headers=HEADERS)
    res.raise_for_status()
    data = res.json()

    reviews = [r["review"].strip() for r in data.get("reviews", []) if r.get("review")]

    if not reviews:
        raise RuntimeError(f"No reviews returned for app_id {app_id!r}")

    return reviews


# load once (important for performance)
sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    revision="714eb0f",
)

@activity.defn
def analyze_sentiment(texts):
    scores = []

    for t in texts:
        result = sentiment_model(t[:512])[0]
        label = result["label"]
        score = result["score"]

        scores.append(score if label == "POSITIVE" else -score)

    return scores


@activity.defn
def aggregate_scores(scores):
    return float(np.mean(scores)) if scores else 0.0
