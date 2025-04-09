from fichier_def_mult import request_anime,extract_id_and_title,get_anime_reviews, get_anime_details
from connexion_post import insert_anime

import requests
from bs4 import BeautifulSoup


anime_entry = input("Entrez le nom de l'anime : ")

animes_dict = {
    'mal_id': None,
    'title': None,
    'type': None,
    'episodes': None,
    'status': None,
    'genres': None,
    'url': None,
    'image_url': None
}

title, url = request_anime(anime_entry)

if title and url:

    anime_info, image_url = get_anime_details(url)

    animes_dict['mal_id'] = url.split('/')[4]
    animes_dict['title'] = title
    animes_dict['type'] = anime_info['Type']
    animes_dict['episodes'] = anime_info['Episodes']
    animes_dict['status'] = anime_info['Status']
    animes_dict['genres'] = anime_info['Genres']
    animes_dict['url'] = url
    animes_dict['image_url'] = image_url

    genres = animes_dict['genres']
    genres_clean = []
    for genre in genres.split(','):
        genre = genre.strip()
        genre_length = len(genre) // 2
        clean_genre = genre[:genre_length].strip()
        genres_clean.append(clean_genre)

    animes_dict['genres'] = ', '.join(genres_clean)

    insert_anime(animes_dict)
