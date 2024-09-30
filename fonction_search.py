import pandas as pd
import requests
from bs4 import BeautifulSoup


def request_anime(anime_name):
    URL = f"https://myanimelist.net/search/all?q={anime_name.replace(' ', '%20')}"

    recup_page = requests.get(URL)

    recup_soup = BeautifulSoup(recup_page.content, "html.parser")

    tag_complet = recup_soup.find('a', class_='hoverinfo_trigger fw-b fl-l')
    if tag_complet:
        url_anime = tag_complet['href']
        titre_anime = tag_complet.get_text(strip=True)
        print(url_anime)
        return titre_anime, url_anime
    else :
        return None, None

def extract_id_and_title(anime_url):

    parts = anime_url.split('/')
    anime_id = parts[4]  
    anime_title_format= parts[5] 
    return anime_id, anime_title_format


titre, url = request_anime("Naruto")
extract_id_and_title(url)