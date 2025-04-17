import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import re
from bs4 import BeautifulSoup
import requests
import nltk 
from fonction_analyse import plot_emotion_pie_chart,plot_line_chart,return_date,filtre_reviews,display_metrics,display_wordcloud,colonne_emotions,prepare_emotion_summary,heatmap_chart
from fichier_def_mult import get_anime_details, get_image
import time

DEBUG = True

def sanitize_filename(name):
    # Replace spaces with underscores and remove special characters
    name = name.replace(' ', '_')
    name = re.sub(r'[^\w\-_.]', '', name)
    return name

def render_main_tab(mode_selection, input_utilisateur, perform_analysis):
    if input_utilisateur:
        # Construction de l'URL de recherche
        URL = f"https://myanimelist.net/anime.php?q={input_utilisateur.replace(' ', '+')}"
        
        recup_page = requests.get(URL)
        recup_soup = BeautifulSoup(recup_page.content, "html.parser")
        
        # Extraction des liens des animes
        tags_a = recup_soup.find_all('a', class_='hoverinfo_trigger')

        if tags_a:
            anime_options = []
            anime_urls = []

            # Parcourir chaque lien trouvé
            for tag in tags_a:
                # Extraire l'image et l'URL
                img_tag = tag.find('img')
                
                if img_tag:
                    anime_name = img_tag['alt']  # Nom de l'anime
                    anime_url = tag['href']  # URL de l'anime

                    # Ajouter aux listes
                    anime_options.append(anime_name)
                    anime_urls.append(anime_url)

            # Initialisation de l'état de session si nécessaire
            if 'selected_anime_index' not in st.session_state:
                st.session_state.selected_anime_index = 0

            # Sélectionner un anime parmi les options
            selected_index = st.selectbox(
                "Select an anime:", 
                range(len(anime_options)),
                index=st.session_state.selected_anime_index,
                key='anime_selection'
            )

            # Mise à jour de l'index sélectionné
            st.session_state.selected_anime_index = selected_index

            selected_anime = anime_options[selected_index]
            selected_url = anime_urls[selected_index]

            anime_info, image_url = get_anime_details(selected_url)
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown(f"### {selected_anime}")
                st.markdown(f"[Link to anime]({selected_url})")
                for key, value in anime_info.items():
                    st.write(f"**{key}:** {value}")

            with col_right:
                if image_url:
                    st.image(image_url, caption=selected_anime, width=300)

            if st.button("Run analysis"):
                perform_analysis(selected_anime, selected_url, anime_info, image_url)
                
            # Ajouter un bouton pour effectuer une nouvelle recherche
            if st.button("🔍 New search from this page"):
                # Réinitialiser les variables de session liées à la recherche
                st.session_state.input_value = ""
                st.session_state.search_performed = False
                st.session_state.selected_anime_index = 0
                st.session_state.df_anime = None
                st.session_state.anime_name = None
                st.session_state.anime_id = None
                st.rerun()
        else:
            st.warning("No anime found. Please try another name.")
            
            # Ajouter un bouton pour effectuer une nouvelle recherche
            if st.button("🔍 Try another search"):
                # Réinitialiser les variables de session liées à la recherche
                st.session_state.input_value = ""
                st.session_state.search_performed = False
                st.session_state.selected_anime_index = 0
                st.session_state.df_anime = None
                st.session_state.anime_name = None
                st.session_state.anime_id = None
                st.rerun()
    else:
        st.info("Please enter an anime name in the search field above and click 'Search'.")

def render_analysis_tab(df_anime, anime_title, anime_id):
    if df_anime is not None and not df_anime.empty:
        # if DEBUG:
        #     print("Debug: Content of 'emotions' column after cleaning")
        #     print(df_anime['emotions'].head())

        st.header("Analysis Results")

        # Télécharger les stopwords si nécessaire
        if 'stopword_dl' not in st.session_state:
            nltk.download('stopwords')
            st.session_state.stopword_dl = True

        # Obtenir les dates limites
        start_date, end_date, start, end = return_date(df_anime)

        # Initialiser les colonnes pour les KPI
        st1, st2, st3, st4 = st.columns(4)

        # Filtrer les reviews en fonction des interactions utilisateur
        df_filtered, negative_button, positive_button, all_button = filtre_reviews(df_anime, st4, start, end)

        # Appliquer les filtres de sentiments sur les reviews
        if positive_button:
            df_filtered = df_filtered[df_filtered['sentiment'] == 'POSITIVE']
        if negative_button:
            df_filtered = df_filtered[df_filtered['sentiment'] == 'NEGATIVE']
        if all_button:
            df_filtered = df_anime[(df_anime['date'] >= start_date) & (df_anime['date'] <= end_date)]


        # # Ajout du téléchargement CSV après application des filtres
        # csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
        # st.download_button("📥 Download filtered data", data=csv_filtered, file_name='anime_reviews_filtered.csv', mime='text/csv')

        # Afficher les métriques
        display_metrics(df_filtered, st1, st2, st3)

        # Redéfinir les colonnes pour les graphiques
        col_left, col_right = st.columns(2)

        # Graphiques
        fig_line = plot_line_chart(df_filtered)  # Utiliser df_filtered au lieu de df_anime
        col_left.plotly_chart(fig_line, use_container_width=True)

        # Préparation et affichage des émotions
        emotions_columns = colonne_emotions(df_filtered)
        df_emotions_sums = prepare_emotion_summary(df_filtered, emotions_columns)

        # Afficher le Pie Chart des émotions
        fig_pie = plot_emotion_pie_chart(df_emotions_sums)
        col_right.plotly_chart(fig_pie, use_container_width=True)

        # Afficher le WordCloud
        display_wordcloud(df_filtered)

        # Afficher la Heatmap des émotions par rating
        fig_heatmap = heatmap_chart(df_filtered, emotions_columns)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Création du nom de fichier dynamique et bouton de téléchargement
        file_name = f'anime_reviews_{sanitize_filename(anime_title)}_{anime_id}.csv'
        csv = df_anime.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Save data as CSV", data=csv, file_name=file_name, mime='text/csv')
    else:
        st.warning("No analysis performed or invalid data.")

