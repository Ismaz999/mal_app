import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import re
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import datetime
import plotly.express as px

def plot_line_chart(df_anime):
    df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
    fig_line = px.line(df_grouped, x='date', y='rating', title="Évolution des notes moyennes par jour")
    return fig_line

def return_date(df_anime):  
    start_date = df_anime['date'].min()
    end_date = df_anime['date'].max()
    start = datetime.datetime(start_date.year, start_date.month, start_date.day)
    end = datetime.datetime(end_date.year, end_date.month, end_date.day)
    return start_date, end_date, start, end


def filtre_reviews(df_anime, st4, start, end):
    with st4:
        col1, col2 = st.columns(2)
        with col1:
            bouton_positif = st.button("Afficher les reviews positives")

        with col2:
            bouton_negatif = st.button("Afficher les reviews négatives")
            
        start_date, end_date = st4.slider("Sélecionnez votre date", 
            min_value=start, 
            max_value=end,
            value=(start,end),
            format="YYYY-MM-DD")

    bouton_tous = st4.button("Tous les Reviews")
    df_filtered =  df_anime[(df_anime['date'] >= start_date) & (df_anime['date'] <= end_date)]

    return df_filtered, bouton_negatif, bouton_positif, bouton_tous

def display_metrics(df_filtered, st1, st2, st3):
    moyenne_rating = df_filtered['rating'].mean()
    nombre_reviews = len(df_filtered)
    nombre_positifs = (df_filtered['sentiment'] == 'POSITIVE').sum()
    pourcentage_positif = (nombre_positifs / nombre_reviews) * 100

    st1.metric(label="Note Moyenne", value=round(moyenne_rating, 2))
    st2.metric(label="Nombre de Reviews", value=nombre_reviews)
    st3.metric(label="Pourcentage de Sentiments Positifs", value=f"{pourcentage_positif:.2f}%")

def colonne_emotions(df_filtered):
    emotions_columns = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
    for col in emotions_columns:
        if col not in df_filtered.columns:
            df_filtered[col] = 0
    return emotions_columns

def prepare_emotion_summary(df_filtered, emotions_columns):
    emotions_sums = df_filtered[emotions_columns].sum()
    df_emotions_sums = emotions_sums.reset_index()
    df_emotions_sums.columns = ['emotion', 'count']
    return df_emotions_sums

def plot_emotion_pie_chart(df_emotions_sums):
    fig_pie = px.pie(df_emotions_sums, values='count', names='emotion', title="Répartition des émotions")
    return fig_pie

def display_wordcloud(df_filtered):
    if 'stopword_dl' not in st.session_state:
        nltk.download('stopwords')
        st.session_state.stopword_dl = True

    with st.expander("Nuage de mots des Reviews"):
        text_reviews = " ".join(df_filtered['review'].dropna().tolist())  # Concaténer les reviews

        text_reviews_clean = re.sub(r'[^\w\s]', '', text_reviews) # enlever la ponctuation
        
        stop_words = set(stopwords.words('english'))  # Supprimer les stop words
        text_reviews_clean = " ".join([word for word in text_reviews_clean.split() if word.lower() not in stop_words])
        
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_reviews_clean)
        
        fig, ax = plt.subplots(figsize=(5, 3)) 
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

def heatmap_chart(df_filtered, emotions_columns):        
    df_hm = df_filtered.pivot_table(values=emotions_columns,index='rating', aggfunc='sum')

    fig_heatmap = px.imshow(df_hm.T,
                            labels=dict(x="Rating", y="Emotion", color="Score"),
                            title="Emotion en fonction du rating",
                            aspect='auto',
                            color_continuous_scale='RdYlBu_r')
    return fig_heatmap