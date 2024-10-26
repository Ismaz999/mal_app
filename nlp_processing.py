from transformers import pipeline

DEBUG = True

sentiment_classifier = pipeline(
    "sentiment-analysis", 
    model="distilbert-base-uncased-finetuned-sst-2-english", 
    truncation=True, 
    max_length=512 # Utilise le GPU si disponible
)

emotion_classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base", 
    truncation=True, 
    max_length=512, 
    top_k=2 # Utilise le GPU si disponible
)


def split_text(text, max_tokens=512):
    words = text.split()
    return [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

def analyze_sentiment_and_emotions(text):

    segments = split_text(text)
    all_sentiments = []
    emotions_list = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
    emotion_totals = {emotion: 0 for emotion in emotions_list}

    # Parcourir chaque segment pour analyser les sentiments et les émotions
    for segment in segments:
        # Analyse des sentiments
        sentiment_result = sentiment_classifier(segment)[0]['label']
        all_sentiments.append(sentiment_result)

        # Analyse des émotions
        emotion_result = emotion_classifier(segment)
        for emotion in emotion_result[0]:
            label = emotion['label']
            score = emotion['score']
            emotion_totals[label] += score

    # Moyenne des émotions sur tous les segments
    total_segments = len(segments)
    avg_emotions = {emotion: score / total_segments for emotion, score in emotion_totals.items()}
    
    # Trier les émotions par score décroissant et sélectionner les deux principales
    sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
    top_two_emotions = {sorted_emotions[0][0]: sorted_emotions[0][1], sorted_emotions[1][0]: sorted_emotions[1][1]} # dans [0][0] le premier cest le nom de l'émotion comme dans le dict, le deuxieme cest

    majority_sentiment = max(set(all_sentiments), key=all_sentiments.count)

    return majority_sentiment, top_two_emotions
