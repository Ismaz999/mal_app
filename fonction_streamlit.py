import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import re

def sanitize_filename(name):
    """Nettoie le nom du fichier en remplaçant les espaces par des underscores et en supprimant les caractères spéciaux."""
    name = name.replace(' ', '_')
    name = re.sub(r'[^\w\-_.]', '', name)
    return name

def render_main_tab(mode_selection, input_utilisateur, anime_options, anime_info, anime_urls, perform_analysis):
    """Rend l'onglet principal pour la sélection et l'analyse de l'anime."""
    if input_utilisateur:
        if anime_options:
            # Sélection de l'anime via Selectbox ou Radio selon le mode choisi
            if mode_selection == "Selectbox":
                selected_anime = st.selectbox("Sélectionnez un anime :", anime_options)
            else:
                selected_anime = st.radio(
                    "Sélectionnez un anime :", 
                    options=anime_options,
                    horizontal=True
                )
            if selected_anime:
                # Affichage des informations de l'anime sélectionné
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**Vous avez sélectionné :** {selected_anime}")
                    st.markdown(f"[Lien vers l'anime]({anime_urls[selected_anime]})")
                with col2:
                    st.image(anime_info[selected_anime], caption=selected_anime)
                
                # Bouton pour lancer l'analyse
                if st.button("ANALYSE MOI CA"):
                    selected_url = anime_urls[selected_anime]
                    st.markdown(f"**Analyse des reviews pour :** {selected_anime} ({selected_url})")
                    perform_analysis(selected_anime, selected_url)
                    st.write("lanime et", selected_anime)
        else:
            st.warning("Aucun anime trouvé. Veuillez essayer un autre nom.")
    else:
        st.image("https://i.gifer.com/Ptwe.gif", caption="En attente d'un anime")

def render_analysis_tab(df_anime, anime_title, anime_id):
    """Rend l'onglet d'analyse avec les graphiques et le bouton de téléchargement."""
    if df_anime is not None and not df_anime.empty:
        st.header("Résultats de l'Analyse")

        # Afficher les noms des colonnes
        st.subheader("Noms des Colonnes")
        st.write(df_anime.columns.tolist())

        # Afficher un aperçu des données
        st.subheader("Aperçu des Données")
        st.write(df_anime.head())

        # Graphique linéaire des notes moyennes par jour
        df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
        fig = px.line(df_grouped, x='date', y='rating', title="Évolution des notes moyennes par jour")
        fig.update_yaxes(range=[0, 11])
        st.plotly_chart(fig, use_container_width=True)

        # Extraire les émotions et les visualiser
        df_exploded = df_anime.explode('emotions')
        df_exploded['emotion_name'] = df_exploded['emotions'].apply(lambda x: x[0] if isinstance(x, tuple) else None)

        df_emotion_counts = df_exploded['emotion_name'].value_counts().reset_index()
        df_emotion_counts.columns = ['emotion', 'count']

        # Graphique en camembert des émotions
        fig_emotions = px.pie(df_emotion_counts, values='count', names='emotion', title="Répartition des émotions dans les avis")
        st.plotly_chart(fig_emotions, use_container_width=True)

        # Optionnel : Nuage de mots des termes les plus fréquents
        def generate_wordcloud(text):
            # Remplacez 'english' par 'french' si les avis sont en français
            stop_words = set(stopwords.words('english'))
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                stopwords=stop_words,
                colormap='viridis',
                collocations=False
            ).generate(text)
            return wordcloud

        all_reviews_text = ' '.join(df_anime['review'].dropna().tolist())
        wordcloud = generate_wordcloud(all_reviews_text)

        st.subheader("Nuage de Mots des Termes les Plus Fréquents")
        fig_wc, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)

        # Afficher le DataFrame complet
        st.subheader("Données des Avis d'Anime")
        st.dataframe(df_anime)

        # Création du nom de fichier dynamique en utilisant les paramètres
        sanitized_title = sanitize_filename(anime_title)
        file_name = f'anime_reviews_{sanitized_title}_{anime_id}.csv'

        # Bouton pour télécharger le CSV
        csv = df_anime.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Sauvegarder les données au format CSV :arrow_down:",
            data=csv,
            file_name=file_name,
            mime='text/csv',
        )
    else:
        st.warning("Aucune analyse effectuée ou données invalides. Sélectionnez un anime pour commencer l'analyse.")
