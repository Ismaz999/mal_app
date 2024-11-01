import requests
from bs4 import BeautifulSoup
import pandas as pd
from transformers import pipeline
import re
import time 
import streamlit as st

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


def get_anime_reviews(anime_id, anime_titre, avis_par_page=20, max_pages=10):

    if 'df_anime_reviews' in st.session_state and st.session_state['anime_id'] == anime_id:
        return st.session_state['df_anime_reviews']

    URL = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews"
    recup_page = requests.get(URL)
    recup_soup = BeautifulSoup(recup_page.content, "html.parser")

    reviews, notes, dates = [], [], []
    page_num = 1

    tag_page = recup_soup.find('div', class_='filtered-results-box')
    nombre_davis = int(tag_page.find('strong').get_text(strip=True))
    div_avispage = nombre_davis / avis_par_page
    if nombre_davis % avis_par_page != 0:
        nombre_page = int(div_avispage) + 1
    else:
        nombre_page = int(div_avispage)
    
    try:
        while page_num <= nombre_page and page_num <= max_pages:            
            url_dynamique = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews?p={page_num}"
            print(f"Scraping page {page_num}: {url_dynamique}")

            page = requests.get(url_dynamique, timeout=10)
            if page.status_code != 200:
                print(f"Erreur lors de la récupération de la page {page_num}: Status code {page.status_code}")
                break

            soup = BeautifulSoup(page.content, "html.parser")
            test_review = soup.find_all('div', class_='text')
            test_rating = soup.find_all('div', class_='rating mt20 mb20 js-hidden')
            test_date = soup.find_all('div', class_='update_at')

            if not test_review:
                print(f"Aucune review trouvée sur la page {page_num}. Arrêt du scraping.")
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

            page_num += 1
            time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"Exception lors de la récupération de la page {page_num}: {e}")
    except Exception as e:
        print(f"Erreur inattendue sur la page {page_num}: {e}")

    df_reviews = pd.DataFrame({
        'review': reviews,
        'rating': notes,
        'date': dates
    })

    # csv_scraping = df_reviews.to_csv(index=False).encode('utf-8')
    # st.download_button("📥 Télécharger les données brutes (après scraping)", data=csv_scraping, file_name='anime_reviews_brutes.csv', mime='text/csv')
    
    st.session_state['df_anime_reviews'] = df_reviews
    st.session_state['anime_id'] = anime_id
    return df_reviews

def get_image(anime_url):
    pics_url = f"{anime_url}/pics"

    page_pics = requests.get(pics_url)
    soup = BeautifulSoup(page_pics.content, "html.parser")
    tag_a = soup.find('a', class_='js-picture-gallery')

    if tag_a and 'href' in tag_a.attrs:
        high_quality_image_url = tag_a['href']
        return high_quality_image_url
    else:
        return None