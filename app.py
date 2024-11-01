import streamlit as st
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
import pandas as pd

from fichier_def_mult import request_anime,extract_id_and_title,get_anime_reviews

from fonction_streamlit import render_main_tab,render_analysis_tab, sanitize_filename

from nlp_processing import analyze_sentiment_and_emotions, split_text


try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

DEBUG = True

### STREAMLIT ###

st.set_page_config(layout="wide", page_title="Sentiment Analysis")
st.markdown('<h1 align="center">Analyse des avis d\'anime</h1>', unsafe_allow_html=True)


input_utilisateur = st.text_input("Analyse des émotions d'une oeuvre")
mode_selection = st.radio("Choisissez le mode de sélection d'anime", ("Selectbox", "Option Menu"))



tabs1, tabs2 = st.tabs(["Menu principal", "Analyse"])

# Initialisation des variables dans st.session_state
if 'df_anime' not in st.session_state:
    st.session_state.df_anime = None
if 'anime_name' not in st.session_state:
    st.session_state.anime_name = None
if 'anime_id' not in st.session_state:
    st.session_state.anime_id = None
if 'selected_anime_index' not in st.session_state:
    st.session_state.selected_anime_index = 0

def perform_analysis(selected_anime, selected_url):
    
    try:
        with st.spinner("Récupération et analyse des avis en cours..."):
            # Récupérer le titre et l'URL

            titre_anime = selected_anime
            lien_anime = selected_url 
            # titre_anime, lien_anime = request_anime(selected_anime)
            st.write(f"Titre Anime: {titre_anime}, Lien Anime: {lien_anime}")  # Debug

            if not lien_anime:
                st.error("Impossible de récupérer les informations de l'anime.")
                return

            # Extraire l'ID et le titre de l'anime
            anime_id, anime_title = extract_id_and_title(lien_anime)
            st.write(f"Anime ID: {anime_id}, Anime Title: {anime_title}")  # Debug

            if not anime_id or not anime_title:
                st.error("ID ou titre de l'anime introuvable.")
                return

            # Récupérer les reviews depuis MyAnimeList
            df_anime = get_anime_reviews(anime_id, anime_title)
            if df_anime is None or df_anime.empty:
                st.warning("Aucun avis trouvé ou récupération échouée.")
                if DEBUG:
                    print("Debug : df_anime est vide ou None après l'appel à get_anime_reviews.")

            st.write(df_anime.head())  # Debug

            # Stocker les résultats dans st.session_state
            st.session_state.df_anime = df_anime
            st.session_state.anime_name = selected_anime
            st.session_state.anime_id = anime_id

            st.success("Analyse terminée ! Allez voir les résultats dans l'onglet 'Analyse'.")
    except Exception as e:
        st.error(f"Erreur lors de la récupération des reviews : {e}")

with tabs1:
    render_main_tab(mode_selection, input_utilisateur, perform_analysis)


with tabs2:
    """Onglet Analyse pour afficher les résultats."""
    df_anime = st.session_state.df_anime
    anime_title = st.session_state.get('anime_name', 'anime')
    anime_id = st.session_state.get('anime_id', '0000')

    if df_anime is not None and not df_anime.empty:
        # Convertir les colonnes en types appropriés après la vérification
        df_anime['rating'] = pd.to_numeric(df_anime['rating'], errors='coerce')
        df_anime['date'] = pd.to_datetime(df_anime['date'], errors='coerce')

        # Appliquer l'analyse des sentiments et des émotions
# Appliquer l'analyse des sentiments et des émotions
        df_anime[['sentiment', 'emotions']] = df_anime['review'].apply(
            lambda x: pd.Series(analyze_sentiment_and_emotions(x))
        )

        df_emot = pd.json_normalize(df_anime['emotions'])
        df_anime = pd.concat([df_anime, df_emot], axis=1)

        # # Ajout du téléchargement CSV après l'analyse NLP
        # csv_analyse = df_anime.to_csv(index=False).encode('utf-8')
        # st.download_button("📥 Télécharger les données après l'analyse des sentiments", data=csv_analyse, file_name='anime_reviews_analyse.csv', mime='text/csv')



        # # Convertir les listes/tuples d'émotions en chaîne de caractères
        # if 'emotions' in df_anime.columns:
        #     df_anime['emotions'] = df_anime['emotions'].apply(lambda x: ', '.join([f"{label}: {score:.2f}" for label, score in x]) if isinstance(x, list) else str(x))
        
        if DEBUG:
            print("Debug : Sentiments et émotions ajoutés à df_anime")
            print(df_anime.head())
            print("emotio etionn :", df_anime['emotions'].head())
            for value in df_anime['emotions']:
                print(f"Valeur : {value} Type : {type(value)}")
        # Convertir les tuples en chaînes de caractères pour éviter les erreurs Arrow
        if 'emotions' in df_anime.columns:
            df_anime['emotions'] = df_anime['emotions'].apply(lambda x: str(x) if isinstance(x, list) else x)

        # Appel à la fonction de rendu de l'analyse
        render_analysis_tab(df_anime, anime_title, anime_id)
    else:
        st.warning("Aucune analyse effectuée ou données invalides.")
