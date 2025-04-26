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
import numpy as np

DEBUG = True

def plot_line_chart(df_anime):
    df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
    fig_line = px.line(df_grouped, x='date', y='rating', 
                      title="Average Rating Over Time",
                      labels={"rating": "Average Rating", "date": "Date"})
    return fig_line

def return_date(df):
    min_date = df['date'].min()
    max_date = df['date'].max()
    
    # Convertir en datetime Python si c'est un Timestamp pandas
    if hasattr(min_date, 'to_pydatetime'):
        min_date = min_date.to_pydatetime()
        max_date = max_date.to_pydatetime()
    
    if min_date == max_date:
        # Cas où toutes les reviews ont la même date
        st.info(f"Toutes les reviews datent du {min_date.strftime('%Y-%m-%d')}")
        return min_date, max_date, min_date, max_date
    else:
        start, end = st.slider(
            "Select date range:",
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            format="YYYY-MM-DD"
        )
        return min_date, max_date, start, end

def filtre_reviews(df_anime, st4, start, end):
    df_filtered = df_anime[(df_anime['date'] >= start) & (df_anime['date'] <= end)]
    
    with st4:
        st.write("Filter by sentiment:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            negative_button = st.button("Negative")
        with col2:
            positive_button = st.button("Positive")
        with col3:
            all_button = st.button("All")
    
    return df_filtered, negative_button, positive_button, all_button

def display_metrics(df_filtered, st1, st2, st3):
    avg_rating = df_filtered['rating'].mean()
    review_count = len(df_filtered)
    positive_count = (df_filtered['sentiment'] == 'POSITIVE').sum()
    positive_percentage = (positive_count / review_count) * 100 if review_count > 0 else 0

    st1.metric(
        label="Average Rating", 
        value=f"{round(avg_rating, 2)}/10" if not pd.isna(avg_rating) else "N/A"
    )
    
    st2.metric(
        label="Number of Reviews", 
        value=review_count
    )
    
    st3.metric(
        label="Positive Sentiment", 
        value=f"{positive_percentage:.1f}%"
    )

def colonne_emotions(df_filtered):
    emotions_columns = [col for col in df_filtered.columns if col in ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']]
    return emotions_columns

def prepare_emotion_summary(df_filtered, emotions_columns):
    df_emotions_sums = pd.DataFrame({
        'emotion': emotions_columns,
        'score': [df_filtered[col].sum() for col in emotions_columns]
    })
    return df_emotions_sums

def plot_emotion_pie_chart(df_emotions_sums):
    fig_pie = px.pie(df_emotions_sums, values='score', names='emotion', 
                    title="Emotion Distribution",
                    color_discrete_sequence=px.colors.qualitative.Pastel)
    return fig_pie

def display_wordcloud(df_filtered):
    if df_filtered['review'].dropna().empty:
        st.warning("Aucune review disponible pour générer le nuage de mots.")
        return
    
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
    df_heatmap = df_filtered.groupby('rating')[emotions_columns].mean().reset_index()
    
    df_heatmap_pivot = df_heatmap.melt(id_vars=['rating'], 
                                      value_vars=emotions_columns,
                                      var_name='emotion', 
                                      value_name='score')
    
    fig_heatmap = px.density_heatmap(df_heatmap_pivot, 
                                    x='rating', 
                                    y='emotion', 
                                    z='score',
                                    title="Emotion Intensity by Rating",
                                    labels={"rating": "Rating", "emotion": "Emotion", "score": "Intensity"})
    
    return fig_heatmap

# Nettoyer les genres rapidement
# genres = animes_dict['genres']
# genres_clean = []
# for genre in genres.split(','):
#     genre = genre.strip()  # enlève les espaces
#     genre_length = len(genre) // 2
#     clean_genre = genre[:genre_length].strip()
#     genres_clean.append(clean_genre)

# # Mettre à jour le dictionnaire
# animes_dict['genres'] = ', '.join(genres_clean)

# print("Après nettoyage :", animes_dict)
