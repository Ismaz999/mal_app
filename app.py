import streamlit as st
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
import pandas as pd

from fichier_def_mult import request_anime,extract_id_and_title,get_anime_reviews

from fonction_streamlit import render_main_tab,render_analysis_tab, sanitize_filename

from nlp_processing import analyze_sentiment_and_emotions, split_text

from connexion_post import insert_anime, check_anime_exists

try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

DEBUG = True

### STREAMLIT ###

st.set_page_config(layout="wide", page_title="Anime Sentiment Analysis")
st.markdown('<h1 align="center">Anime Reviews Analysis</h1>', unsafe_allow_html=True)

# Initialisation des variables dans st.session_state
if 'reset_search' not in st.session_state:
    st.session_state.reset_search = False

# Si une réinitialisation est demandée, on supprime la clé anime_selection pour forcer sa recréation
if st.session_state.reset_search and 'anime_selection' in st.session_state:
    # On ne peut pas modifier directement anime_selection, mais on peut le supprimer
    del st.session_state['anime_selection']
    st.session_state.reset_search = False

# Utilisation de session_state pour stocker la valeur de l'input
if 'input_value' not in st.session_state:
    st.session_state.input_value = ""
if 'search_performed' not in st.session_state:
    st.session_state.search_performed = False

# Initialisation des variables dans st.session_state
if 'df_anime' not in st.session_state:
    st.session_state.df_anime = None
if 'anime_name' not in st.session_state:
    st.session_state.anime_name = None
if 'anime_id' not in st.session_state:
    st.session_state.anime_id = None
if 'selected_anime_index' not in st.session_state:
    st.session_state.selected_anime_index = 0

def perform_analysis(selected_anime, selected_url, anime_info, image_url):
    try:
        with st.spinner("Retrieving and analyzing reviews..."):
            # Récupérer le titre et l'URL
            anime_title = selected_anime
            anime_url = selected_url 
            
            st.write(f"Anime Title: {anime_title}, Anime URL: {anime_url}")  # Debug

            if not anime_url:
                st.error("Unable to retrieve anime information.")
                return

            # Extraire l'ID et le titre de l'anime
            anime_id, anime_title_mal = extract_id_and_title(anime_url)
            st.write(f"Anime ID: {anime_id}, MAL Anime Title: {anime_title_mal}")  # Debug

            if check_anime_exists(anime_id):
                st.warning("Cet anime est déjà dans la base de données !")
                if not st.button("Mettre à jour quand même ?"):
                    return

            if not anime_id or not anime_title_mal:
                st.error("Anime ID or title not found.")
                return

            # Récupérer les reviews depuis MyAnimeList
            df_anime = get_anime_reviews(anime_id, anime_title_mal)
            if df_anime is None or df_anime.empty:
                st.warning("No reviews found or retrieval failed.")
                # print("Debug: df_anime is empty or None after calling get_anime_reviews.")

            st.write(df_anime.head())  # Debug

            # Stocker les résultats dans st.session_state
            st.session_state.df_anime = df_anime
            st.session_state.anime_name = selected_anime
            st.session_state.anime_id = anime_id

            #remplissage des dictionnaires
            anime_dict['url'] = anime_url
            anime_dict['title'] = anime_title
            anime_dict['mal_id'] = anime_id
            anime_dict['image_url'] = image_url 
            anime_dict['type'] = anime_info.get('Type')
            anime_dict['episodes'] = anime_info.get('Episodes')
            anime_dict['status'] = anime_info.get('Status')
            anime_dict['genres'] = anime_info.get('Genres')

            # print("print du dictionnaire", anime_dict)

            review_dict['review_text'] = df_anime['review']
            review_dict['rating'] = df_anime['rating']
            review_dict['review_date'] = df_anime['date']

            # print("print du dictionnaire", review_dict)

            st.success("Analysis complete! Check the 'Analysis' tab to see the results.")
    except Exception as e:
        st.error(f"Error retrieving reviews: {e}")

# Création des onglets
tabs1, tabs2 = st.tabs(["Main Menu", "Analysis"])

anime_dict = {
    'mal_id': None,
    'title': None,
    'type': None,
    'episodes': None,
    'status': None,
    'genres': None,
    'url': None,
    'image_url': None
}

review_dict = {
    'review_text': None,
    'rating': None,
    'review_date': None,
}

emotions_dict = {
    'sentiment': None,
    'neutral': 0.0,
    'joy': 0.0,
    'disgust': 0.0,
    'surprise': 0.0,
    'sadness': 0.0,
    'fear': 0.0,
    'anger': 0.0
}

with tabs1:
    # Ajout d'un bouton pour réinitialiser la recherche
    if st.button("🔄 New Search"):
        # Réinitialiser les variables de session liées à la recherche
        st.session_state.input_value = ""
        st.session_state.search_performed = False
        st.session_state.selected_anime_index = 0
        st.session_state.reset_search = True
        st.rerun()
        
    # Création d'un formulaire pour la recherche
    with st.form(key='search_form'):
        input_utilisateur = st.text_input("Search for an anime", value=st.session_state.input_value)
        submit_button = st.form_submit_button(label='Search')
        
        if submit_button:
            st.session_state.input_value = input_utilisateur
            st.session_state.search_performed = True
            # Réinitialiser les sélections précédentes
            st.session_state.selected_anime_index = 0
            # On ne modifie pas directement anime_selection

    mode_selection = st.radio("Choose selection mode", ("Selectbox", "Option Menu"))
    
    # Passer la valeur de l'input et l'état de la recherche à render_main_tab
    render_main_tab(mode_selection, st.session_state.input_value if st.session_state.search_performed else "", perform_analysis)


with tabs2:
    """Analysis tab to display results."""
    df_anime = st.session_state.df_anime
    anime_title = st.session_state.get('anime_name', 'anime')
    anime_id = st.session_state.get('anime_id', '0000')

    if df_anime is not None and not df_anime.empty:
        # Convertir les colonnes en types appropriés après la vérification
        df_anime['rating'] = pd.to_numeric(df_anime['rating'], errors='coerce')
        df_anime['date'] = pd.to_datetime(df_anime['date'], errors='coerce')

        # Appliquer l'analyse des sentiments et des émotions
        df_anime[['sentiment', 'emotions']] = df_anime['review'].apply(
            lambda x: pd.Series(analyze_sentiment_and_emotions(x))
        )

        df_emot = pd.json_normalize(df_anime['emotions'])
        
        # Vérifier et initialiser les colonnes d'émotions manquantes
        emotions_columns = ['neutral', 'joy', 'disgust', 'surprise', 'sadness', 'fear', 'anger']
        for emotion in emotions_columns:
            if emotion not in df_emot.columns:
                df_emot[emotion] = 0.0  # Valeur par défaut si l'émotion n'est pas présente

        df_anime = pd.concat([df_anime, df_emot], axis=1)

        # Remplir le dictionnaire d'émotions
        emotions_dict['sentiment'] = df_anime['sentiment'].tolist()
        emotions_dict['neutral'] = df_emot['neutral'].tolist()
        emotions_dict['joy'] = df_emot['joy'].tolist()
        emotions_dict['disgust'] = df_emot['disgust'].tolist()
        emotions_dict['surprise'] = df_emot['surprise'].tolist()
        emotions_dict['sadness'] = df_emot['sadness'].tolist()
        emotions_dict['fear'] = df_emot['fear'].tolist()
        emotions_dict['anger'] = df_emot['anger'].tolist()

        # print("Emotions dict rempli:", emotions_dict)

        # # Ajout du téléchargement CSV après l'analyse NLP
        # csv_analyse = df_anime.to_csv(index=False).encode('utf-8')
        # st.download_button(" Download data after sentiment analysis", data=csv_analyse, file_name='anime_reviews_analyse.csv', mime='text/csv')

        # # Convertir les listes/tuples d'émotions en chaîne de caractères
        # if 'emotions' in df_anime.columns:
        #     df_anime['emotions'] = df_anime['emotions'].apply(lambda x: ', '.join([f"{label}: {score:.2f}" for label, score in x]) if isinstance(x, list) else str(x))
        
        insert_anime(anime_dict, review_dict, emotions_dict)

        # if DEBUG:
        #     print("Debug: Sentiments and emotions added to df_anime")
        #     print(df_anime.head())
        #     print("Emotions:", df_anime['emotions'].head())
        #     for value in df_anime['emotions']:
        #         print(f"Value: {value} Type: {type(value)}")
        # Convertir les tuples en chaînes de caractères pour éviter les erreurs Arrow
        if 'emotions' in df_anime.columns:
            df_anime['emotions'] = df_anime['emotions'].apply(lambda x: str(x) if isinstance(x, list) else x)

        # Appel à la fonction de rendu de l'analyse
        render_analysis_tab(df_anime, anime_title, anime_id)
    else:
        st.warning("No analysis performed or invalid data.")
