import streamlit as st


from io import BytesIO
from PIL import Image
import rembg
from rembg import remove
from streamlit_option_menu import option_menu
from bs4 import BeautifulSoup
import requests

#partie analyse des sentiments
import pandas as pd
import plotly.express as px

from fichier_def_mult import request_anime, extract_id_and_title, get_anime_reviews, analyze_sentiment_and_emotions

st.set_page_config(layout="wide", page_title="Sentiment Analysis") 
st.markdown('<h1 align="center">Analyse des avis d\'anime</h1>', unsafe_allow_html=True)

mode_selection = st.radio("Choisissez le mode de sélection d'anime", ("Selectbox", "Option Menu"))
input_utilisateur = st.text_input("Analyse des émotions d'une oeuvre")

tabs1, tabs2 = st.tabs(["Menu principal", "Analyse"])

df_anime = None  

with tabs1:
    if input_utilisateur:
        URL = f"https://myanimelist.net/search/all?q={input_utilisateur.replace(' ', '%20')}&cat=anime"
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
                    anime_image = name_tag['data-src']  # Lien vers l'image
                    anime_url = tag_a['href']
                    
                    # Ajouter l'anime à la liste d'options et stocker ses infos
                    anime_options.append(anime_name)
                    anime_info[anime_name] = anime_image
                    anime_urls[anime_name] = anime_url

            if mode_selection == "Selectbox":
                selected_anime = st.selectbox("Sélectionnez un anime :", anime_options)
            else:
                selected_anime = option_menu(
                    "Sélectionnez un anime :", 
                    options=anime_options,
                    menu_icon="cast", 
                    default_index=0,
                    orientation="horizontal"
                )

            # Afficher l'anime sélectionné
            if selected_anime:
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.write(f"Vous avez sélectionné : {selected_anime}")
                    st.write(f"Lien vers l'anime : {anime_urls[selected_anime]}")
                with col2:
                    st.image(anime_info[selected_anime], caption=selected_anime)
                
                # Bouton pour lancer l'analyse des reviews
                if st.button("ANALYSE MOI CA"):
                    selected_url = anime_urls[selected_anime]
                    st.write(f"Analyse des reviews pour : {selected_anime} ({selected_url})")

                    # Appeler tes fonctions pour récupérer les reviews
                    try:
                        titre_anime, lien_anime = request_anime(selected_anime)  # Récupérer le titre et l'URL
                        anime_id, anime_title = extract_id_and_title(lien_anime)  # Extraire l'ID de l'anime
                        df_anime = get_anime_reviews(anime_id, anime_title)  # Récupérer les reviews depuis MyAnimeList

                        st.success("Analyse terminée ! Allez voir les résultats dans l'onglet 'Analyse'.")
                    except Exception as e:
                        st.error(f"Erreur lors de la récupération des reviews : {e}")
        else:
            st.write("Aucun anime trouvé. Veuillez essayer un autre nom.")

    else:
        st.image("https://i.gifer.com/Ptwe.gif", caption="En attente d'un anime")

with tabs2:
    if df_anime is not None and not df_anime.empty:
        # Analyser les sentiments et les émotions
        df_anime[['sentiment', 'emotions']] = df_anime['review'].apply(lambda x: pd.Series(analyze_sentiment_and_emotions(x)))

        # Nettoyer les données
        df_anime['rating'] = pd.to_numeric(df_anime['rating'], errors='coerce')
        df_anime['date'] = pd.to_datetime(df_anime['date'], errors='coerce')

        # Graphique linéaire des notes moyennes par jour
        df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
        fig = px.line(df_grouped, x='date', y='rating', title="Évolution des notes moyennes par jour")
        fig.update_yaxes(range=[0, 11])
        st.plotly_chart(fig)

        # Extraire les émotions et les visualiser
        df_exploded = df_anime.explode('emotions')
        df_exploded['emotion_name'] = df_exploded['emotions'].apply(lambda x: x[0] if isinstance(x, tuple) else None)

        df_emotion_counts = df_exploded['emotion_name'].value_counts().reset_index()
        df_emotion_counts.columns = ['emotion', 'count']

        # Graphique en camembert des émotions
        fig_emotions = px.pie(df_emotion_counts, values='count', names='emotion', title="Répartition des émotions dans les avis")
        st.plotly_chart(fig_emotions)
    else:
        st.write("Aucune analyse effectuée ou données invalides. Sélectionnez un anime pour commencer l'analyse.")