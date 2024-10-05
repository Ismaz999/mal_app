from transformers import pipeline
import pandas as pd


df_anime = pd.read_csv("anime_reviews/anime_reviews_2001_Tengen_Toppa_Gurren_Lagann.csv")

sentiment_classifier = pipeline("sentiment-analysis", truncation=True, max_length=512)
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", truncation=True, max_length=512, top_k=2)

def split_text(text, max_tokens=512):
    words = text.split()  
    return [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

def analyze_sentiment_and_emotions(text):

    segments = split_text(text)  
    all_sentiments = []
    all_emotions = []

    for segment in segments:
        sentiment_result = sentiment_classifier(segment)[0]['label']
        all_sentiments.append(sentiment_result)
        
        emotion_result = emotion_classifier(segment)
        top_emotions = {emotion['label']: emotion['score'] for emotion in emotion_result[0]}
        all_emotions.append(top_emotions)

    return ', '.join(all_sentiments), all_emotions     

    # sentiment_result = sentiment_classifier(text)[0]['label']
    
    # emotion_result = emotion_classifier(text)
    # top_emotions = {emotion['label']: emotion['score'] for emotion in emotion_result}
    
    # return sentiment_result, top_emotions

df_anime[['sentiment', 'emotions']] = df_anime['review'].apply(lambda x: pd.Series(analyze_sentiment_and_emotions(x)))

print(df_anime[['review', 'sentiment', 'emotions']].head())

df_anime.to_csv("anime_reviews_with_sentiments_and_emotions.csv", sep=';', index=False)

# classifier = pipeline("sentiment-analysis")
# avis = "J'adore cet anime, les combats sont incroyables !"
# resultat = classifier(avis)
# print(resultat)
# print("label",resultat[0]['label'])