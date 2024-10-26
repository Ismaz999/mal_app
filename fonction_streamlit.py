import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import re
from bs4 import BeautifulSoup
import requests

DEBUG = True

def sanitize_filename(name):
    #remplace espaces par underscore et en supprimme les caractères spéciaux.
    name = name.replace(' ', '_')
    name = re.sub(r'[^\w\-_.]', '', name)
    return name

def render_main_tab(mode_selection, input_utilisateur, perform_analysis):
    if input_utilisateur:
        # Construction de l'URL de recherche
        URL = f"https://myanimelist.net/search/all?q={input_utilisateur.replace(' ', '%20')}&cat=anime"
        
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
                format_func=lambda x: anime_options[x]
            )

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
    else:
        st.image("https://i.gifer.com/Ptwe.gif", caption="En attente d'un anime")

def render_analysis_tab(df_anime, anime_title, anime_id):
    # if df_anime is not None and not df_anime.empty:
    #     # Nettoyage de la colonne 'emotions' pour éviter les erreurs de conversion
    #     df_anime['emotions'] = df_anime['emotions'].apply(lambda x: x if isinstance(x, list) else []) PLUS UTILE CAR JAI SEPARE MES EMOTIOSNS EN COLONNES DISTINCTE

    if DEBUG:
        print("Debug : Contenu de la colonne 'emotions' après nettoyage")
        print(df_anime['emotions'].head())

        st.header("Résultats de l'Analyse")
        # st.dataframe(df_anime) SINON JAI DES ERREURS A CAUSE DE PYARROW ET DES TUPLES

        # Graphique linéaire des notes moyennes par jour
        df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
        fig = px.line(df_grouped, x='date', y='rating', title="Évolution des notes moyennes par jour")
        st.plotly_chart(fig)

        emotions_columns = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']

        for col in emotions_columns:
            if col not in df_anime.columns:
                df_anime[col] = 0

        emotions_sums = df_anime[emotions_columns].sum()
        df_emotions_sums = emotions_sums.reset_index()
        df_emotions_sums.columns = ['emotion', 'count']

        # # Extraire les émotions et les visualiser
        # df_exploded = df_anime.explode('emotions')
        # df_exploded['emotion_name'] = df_exploded['emotions'].apply(
        #     lambda x: x[0] if isinstance(x, tuple) else None
        # )
        # # Compter les occurrences des émotions
        # df_emotion_counts = df_exploded['emotion_name'].value_counts().reset_index()
        # df_emotion_counts.columns = ['emotion', 'count']

        # Graphique en camembert des émotions
        print(emotions_sums)
        fig_emotions = px.pie(df_emotions_sums, values='count', names='emotion', title="Répartition des émotions")
        st.plotly_chart(fig_emotions)

        # Création du nom de fichier dynamique et bouton de téléchargement
        file_name = f'anime_reviews_{sanitize_filename(anime_title)}_{anime_id}.csv'
        csv = df_anime.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Sauvegarder les données au format CSV", data=csv, file_name=file_name, mime='text/csv')
    else:
        st.warning("Aucune analyse effectuée ou données invalides.")

