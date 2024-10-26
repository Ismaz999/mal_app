import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline
import re
import time 

DEBUG = True

def request_anime(anime_name):
    # URL = f"https://myanimelist.net/search/all?q={anime_name.replace(' ', '%20')}&cat=anime"
    URL = f"https://myanimelist.net/anime.php?q={anime_name.replace(' ', '%20')}&cat=anime"
    recup_page = requests.get(URL)
    recup_soup = BeautifulSoup(recup_page.content, "html.parser")
    tag_complet = recup_soup.find('a', class_='hoverinfo_trigger')
    if tag_complet:
        title = tag_complet.find('img')['alt']
        url = tag_complet['href']
        return title, url
    else:
        return None, None
    
def extract_id_and_title(anime_url):
    match = re.search(r'/anime/(\d+)/', anime_url)
    if match:
        anime_id = match.group(1)
        return anime_id, match.group(0)
    return None, None


def get_anime_reviews(anime_id, anime_titre, avis_par_page=20, max_pages=3):
    # URL = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews"
    # recup_page = requests.get(URL)
    # recup_soup = BeautifulSoup(recup_page.content, "html.parser")
    reviews, notes, dates = [], [], []
    page_num = 1

    while page_num <= max_pages:  # Limite à 2 pages
        url_dynamique = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews?p={page_num}"
        print(f"Scraping page {page_num}: {url_dynamique}")
        
        try:
            page = requests.get(url_dynamique, timeout=10)
            if page.status_code != 200:
                print(f"Erreur lors de la récupération de la page {page_num}: Status code {page.status_code}")
                break

            # page = requests.get(url_dynamique)
            soup = BeautifulSoup(page.content, "html.parser")
            test_review = soup.find_all('div', class_='text')
            test_rating = soup.find_all('div', class_='rating mt20 mb20 js-hidden')
            test_date = soup.find_all('div', class_='update_at')

            if not test_review:
                print(f"Aucune review trouvée sur la page {page_num}. Arrêt du scraping.")
                break

            if not (len(test_review) == len(test_rating) == len(test_date)):
                print(f"Mismatch dans le nombre d'éléments sur la page {page_num}.")
                break

            for rev, rat, jour in zip(test_review, test_rating, test_date):
                review_text = rev.get_text(strip=True)
                rat_span = rat.find('span', class_='num')
                rat_clean = rat_span.get_text(strip=True) if rat_span else None
                date_text = jour.get_text(strip=True) if jour else None
                reviews.append(review_text)
                notes.append(rat_clean)
                dates.append(date_text)

            if DEBUG:
                print(f"Page {page_num} - Nombre de reviews récupérées : {len(reviews)}")    

            print(f"Page {page_num} - Nombre de reviews récupérées : {len(reviews)}")

            page_num += 1
            time.sleep(1)    

        except requests.exceptions.RequestException as e:
            print(f"Exception lors de la récupération de la page {page_num}: {e}")
            break
        except Exception as e:
            print(f"Erreur inattendue sur la page {page_num}: {e}")
            break

    return pd.DataFrame({
        'review': reviews,
        'rating': notes,
        'date': dates
    })

# modèle NLP a configurer avant
# sentiment_classifier = pipeline("sentiment-analysis", truncation=True, max_length=512)
# emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", truncation=True, max_length=512, top_k=2)

# def split_text(text, max_tokens=512):
#     words = text.split()
#     return [' '.join(words[i:i + max_tokens]) for i in range(0, len(words), max_tokens)]

# def analyze_sentiment_and_emotions(text):
#     segments = split_text(text)
#     all_sentiments = []
#     emotion_totals = {}

#     for segment in segments:
#         sentiment_result = sentiment_classifier(segment)[0]['label']
#         all_sentiments.append(sentiment_result)
#         emotion_result = emotion_classifier(segment)
#         for emotion in emotion_result[0]:
#             label = emotion['label']
#             score = emotion['score']
#             if label in emotion_totals:
#                 emotion_totals[label] += score
#             else:
#                 emotion_totals[label] = score

#     total_segments = len(segments)
#     avg_emotions = {emotion: score / total_segments for emotion, score in emotion_totals.items()}
#     sorted_emotions = sorted(avg_emotions.items(), key=lambda x: x[1], reverse=True)
#     top_two_emotions = sorted_emotions[:2]
#     return ', '.join(all_sentiments), top_two_emotions