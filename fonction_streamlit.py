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
import time

DEBUG = True

def sanitize_filename(name):
    #remplace espaces par underscore et en supprimme les caractères spéciaux.
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

            # Sélectionner un anime parmi les options
            selected_index = st.selectbox(
                "Sélectionnez un anime :", 
                range(len(anime_options)),
                index=st.session_state.get('selected_anime_index', 0),
                key='anime_selection',
                on_change=lambda: st.session_state.update({"selected_anime_index": st.session_state.anime_selection}),
                format_func=lambda x: anime_options[x]            
                )

            st.session_state.selected_anime_index = st.session_state.anime_selection
            selected_index = st.session_state.selected_anime_index

            # time.sleep(2)

            # Problème rencontré : À chaque changement de sélection dans la selectbox, Streamlit rafraîchissait tout le script,
            # causant une ré-exécution de l'analyse et des incohérences dans les données. Pour résoudre ce problème :
            # 1. Une clé (`key="anime_select"`) a été attribuée à la `selectbox` pour garder l'état de la sélection stable.
            # 2. La fonction `on_change` a été utilisée pour ne lancer `perform_analysis_callback` que lorsque l'utilisateur change réellement sa sélection.
            # Cela garantit que l'analyse n'est lancée qu'une seule fois pour chaque nouvel anime, évitant des appels redondants et des résultats incohérents.

            if selected_index is not None:
                selected_anime = anime_options[selected_index]
                selected_url = anime_urls[selected_index]

                # Afficher les informations de l'anime sélectionné
                st.markdown(f"**Vous avez sélectionné :** {selected_anime}")
                st.markdown(f"[Lien vers l'anime]({selected_url})")

                if st.button("ANALYSE MOI CA"):
                    perform_analysis(selected_anime, selected_url)
        else:
            st.warning("Aucun anime trouvé. Veuillez essayer un autre nom.")

def render_analysis_tab(df_anime, anime_title, anime_id):
    if df_anime is not None and not df_anime.empty:
        if DEBUG:
            print("Debug : Contenu de la colonne 'emotions' après nettoyage")
            print(df_anime['emotions'].head())

        st.header("Résultats de l'Analyse")

        # Télécharger les stopwords si nécessaire
        if 'stopword_dl' not in st.session_state:
            nltk.download('stopwords')
            st.session_state.stopword_dl = True

        # Obtenir les dates limites
        start_date, end_date, start, end = return_date(df_anime)

        # Initialiser les colonnes pour les KPI
        st1, st2, st3, st4 = st.columns(4)

        # Filtrer les reviews en fonction des interactions utilisateur
        df_filtered, bouton_negatif, bouton_positif, bouton_tous = filtre_reviews(df_anime, st4, start, end)

        # Appliquer les filtres de sentiments sur les reviews
        if bouton_positif:
            df_filtered = df_filtered[df_filtered['sentiment'] == 'POSITIVE']
        if bouton_negatif:
            df_filtered = df_filtered[df_filtered['sentiment'] == 'NEGATIVE']
        if bouton_tous:
            df_filtered = df_anime[(df_anime['date'] >= start_date) & (df_anime['date'] <= end_date)]


        # # Ajout du téléchargement CSV après application des filtres
        # csv_filtered = df_filtered.to_csv(index=False).encode('utf-8')
        # st.download_button("📥 Télécharger les données après filtrage", data=csv_filtered, file_name='anime_reviews_filtre.csv', mime='text/csv')

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
        st.download_button("📥 Sauvegarder les données au format CSV", data=csv, file_name=file_name, mime='text/csv')
    else:
        st.warning("Aucune analyse effectuée ou données invalides.")

