import streamlit as st
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
import pandas as pd

from fichier_def_mult import (
    request_anime,
    extract_id_and_title,
    get_anime_reviews,
    analyze_sentiment_and_emotions
)

from fonction_streamlit import (
    render_main_tab,
    render_analysis_tab,
    sanitize_filename
)

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

###STREAMLIT###

st.set_page_config(layout="wide", page_title="Sentiment Analysis") 
st.markdown('<h1 align="center">Analyse des avis d\'anime</h1>', unsafe_allow_html=True)

mode_selection = st.radio("Choisissez le mode de sélection d'anime", ("Selectbox", "Option Menu"))
input_utilisateur = st.text_input("Analyse des émotions d'une oeuvre")

tabs1, tabs2 = st.tabs(["Menu principal", "Analyse"])

# Initialisation des variables dans st.session_state
if 'df_anime' not in st.session_state:
    st.session_state.df_anime = None
if 'anime_name' not in st.session_state:
    st.session_state.anime_name = None
if 'anime_id' not in st.session_state:
    st.session_state.anime_id = None

def perform_analysis(selected_anime, selected_url):
    try:
        with st.spinner("Récupération et analyse des avis en cours..."):
            titre_anime, lien_anime = request_anime(selected_anime)  # Récupérer le titre et l'URL
            st.write(f"Titre Anime: {titre_anime}, Lien Anime: {lien_anime}")  # Debug
            if not lien_anime:
                st.error("Impossible de récupérer les informations de l'anime.")
                return
            anime_id, anime_title = extract_id_and_title(lien_anime)  # Extraire l'ID et le titre de l'anime
            st.write(f"Anime ID: {anime_id}, Anime Title: {anime_title}")  # Debug
            if not anime_id or not anime_title:
                st.error("ID ou titre de l'anime introuvable.")
                return
            df_anime = get_anime_reviews(anime_id, anime_title)  # Récupérer les reviews depuis MyAnimeList
            st.write(df_anime.head())  # Debug

            if df_anime.empty:
                st.warning("Aucun avis trouvé pour cet anime.")
                return

            df_anime[['sentiment', 'emotions']] = df_anime['review'].apply(
                lambda x: pd.Series(analyze_sentiment_and_emotions(x))
            )

            df_anime['rating'] = pd.to_numeric(df_anime['rating'], errors='coerce')
            df_anime['date'] = pd.to_datetime(df_anime['date'], errors='coerce')

            # Stockage des résultats dans st.session_state
            st.session_state.df_anime = df_anime
            st.session_state.anime_name = selected_anime
            st.session_state.anime_id = anime_id

            st.success("Analyse terminée ! Allez voir les résultats dans l'onglet 'Analyse'.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des reviews : {e}")

with tabs1:
    if input_utilisateur:
        URL = f"https://myanimelist.net/anime.php?q={input_utilisateur.replace(' ', '%20')}&cat=anime"
        recup_page = requests.get(URL)
        recup_soup = BeautifulSoup(recup_page.content, "html.parser")
        
        tags_a = recup_soup.find_all('a', class_='hoverinfo_trigger')
        
        if tags_a:
            anime_options = []
            anime_info = {}
            anime_urls = {}
            
            for tag_a in tags_a:
                name_tag = tag_a.find('img')
                if name_tag:
                    anime_name = name_tag['alt']  # Nom de l'anime
                    anime_image = name_tag.get('data-src', '')  # Lien vers l'image
                    anime_url = tag_a['href']
                    
                    anime_options.append(anime_name)
                    anime_info[anime_name] = anime_image
                    anime_urls[anime_name] = anime_url

            render_main_tab(mode_selection, input_utilisateur, anime_options, anime_info, anime_urls, perform_analysis)
        else:
            st.write("Aucun anime trouvé. Veuillez essayer un autre nom.")
    else:
        st.image("https://i.gifer.com/Ptwe.gif", caption="En attente d'un anime")

with tabs2:
    """Onglet Analyse pour afficher les résultats."""
    df_anime = st.session_state.df_anime
    anime_title = st.session_state.get('anime_name', 'anime')
    anime_id = st.session_state.get('anime_id', '0000')

    # Appel à la fonction de rendu de l'analyse
    render_analysis_tab(df_anime, anime_title, anime_id)
