from transformers import pipeline
import pandas as pd


df_anime = pd.read_csv("anime_reviews/anime_reviews_2001_Tengen_Toppa_Gurren_Lagann.csv")

classifier = pipeline("sentiment-analysis",truncation=True) 

def analyze_anime(text, classifier):
    resultat = classifier(text)
    return resultat[0]['label']

df_anime['sentiment'] = df_anime['review'].apply(lambda x: analyze_anime(x, classifier))

print(df_anime.head())

# classifier = pipeline("sentiment-analysis")
# avis = "J'adore cet anime, les combats sont incroyables !"
# resultat = classifier(avis)
# print(resultat)
# print("label",resultat[0]['label'])