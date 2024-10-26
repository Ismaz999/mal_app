import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

from fonction_search import request_anime, extract_id_and_title

avis_par_page = 20

def get_anime_reviews(anime_id, anime_titre, avis_par_page, folder="anime_reviews"):

    if not os.path.exists(folder):
        os.makedirs(folder)

    URL = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews"

    recup_page = requests.get(URL)
    recup_soup = BeautifulSoup(recup_page.content, "html.parser")

    tag_page = recup_soup.find('div', class_='filtered-results-box')
    nombre_davis = int(tag_page.find('strong').get_text(strip=True))

    div_avispage = nombre_davis/avis_par_page
    if nombre_davis%avis_par_page != 0:
        nombre_page = int(div_avispage)+1
    else:
        nombre_page = int(div_avispage)

    ############################
    ##recupération des reviews##
    ############################

    reviews = []
    note = []
    date = []

    for page_num in range(1, nombre_page + 1):

        url_dynamique = f"https://myanimelist.net/anime/{anime_id}/{anime_titre}/reviews?p={page_num}"
        page = requests.get(url_dynamique)
        soup = BeautifulSoup(page.content, "html.parser")

        test_review = soup.find_all('div', class_='text')  #permet de recupérer la review complete
        test_rating = soup.find_all('div', class_='rating mt20 mb20 js-hidden') #permet de recupérer la review complete
        test_date = soup.find_all('div', class_='update_at')  

        for rev, rat, jour in zip(test_review, test_rating, test_date):
            rat_clean = rat.find('span', class_='num')

            review_text = rev.get_text(strip=True)
            note_text = rat_clean.get_text(strip=True)
            date_text = jour.get_text(strip=True)

            reviews.append(review_text)
            note.append(note_text)
            date.append(date_text)

    review_df = pd.DataFrame({
        'review': reviews,
        'rating': note,
        'date': date
    })

    print(review_df)

    review_df.to_csv(f'{folder}/anime_reviews_{anime_id}_{anime_titre}.csv', index=False)
    return review_df

anime_name = input("Entrez le nom de l'anime : ")

titre, url_anime = request_anime(anime_name)
id_anime, anime_title = extract_id_and_title(url_anime)
get_anime_reviews(id_anime, anime_title,avis_par_page)