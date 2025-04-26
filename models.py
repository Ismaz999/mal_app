from datetime import datetime

ANIME_DICT = {
    'mal_id': None,
    'title': None,
    'type': None,
    'episodes': None,
    'status': None,
    'genres': None,
    'url': None,
    'image_url': None
}

REVIEW_DICT = {
    'anime_id': None,
    'review_text': None,
    'rating': None,
    'review_date': None,
    'sentiment': None
}

EMOTIONS_DICT = {
    'anger': 0.0,
    'disgust': 0.0,
    'fear': 0.0,
    'joy': 0.0,
    'neutral': 0.0,
    'sadness': 0.0,
    'surprise': 0.0
}

def create_anime_dict():
    return ANIME_DICT.copy()

def create_review_dict():
    return REVIEW_DICT.copy()

def create_emotions_dict():
    return EMOTIONS_DICT.copy()
