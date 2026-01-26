import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon")

sia = SentimentIntensityAnalyzer()

def detect_mood(text):
    score = sia.polarity_scores(text)["compound"]

    if score <= -0.6:
        return "sad"
    elif score < -0.2:
        return "stressed"
    elif score > 0.5:
        return "positive"
    else:
        return "neutral"

CRISIS_KEYWORDS = [
    "want to die",
    "end everything",
    "self harm",
    "kill myself",
    "can't go on",
    "suicide"
]

def is_crisis(text):
    text = text.lower()
    return any(k in text for k in CRISIS_KEYWORDS)
