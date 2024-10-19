import streamlit as st
from io import BytesIO
from PIL import Image
import rembg
from rembg import remove
import pandas as pd
import csv
import plotly.express as px
import ast 

st.set_page_config(layout='wide',page_title="Analyse des reviews d'anime") # On configure la forme de la page en wide 

st.title('Analyse des sentiments des avis d\'anime')

st.sidebar.title("Upload du fichier csv")
csv_upload = st.sidebar.file_uploader("Joindre votre fichier : ", type=["csv"])

####### partie code####

df_anime = pd.read_csv("anime_reviews_with_sentiments_and_emotions.csv", sep=';')

df_anime['rating'] = pd.to_numeric(df_anime['rating'], errors='coerce')
df_anime = df_anime.dropna(subset=['rating'])
df_anime['date'] = pd.to_datetime(df_anime['date'], errors='coerce')

df_grouped = df_anime.groupby('date')['rating'].mean().reset_index()
fig = px.line(df_grouped, x='date', y='rating', title="Évolution des notes moyennes par jour")
fig.update_yaxes(range=[0, 11])  # Limiter les notes entre 0 et 11
st.plotly_chart(fig)

df_anime['emotions'] = df_anime['emotions'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df_exploded = df_anime.explode('emotions')

df_exploded['emotion_name'] = df_exploded['emotions'].apply(lambda x: x[0] if isinstance(x, tuple) else None)

df_emotion_counts = df_exploded['emotion_name'].value_counts().reset_index()
df_emotion_counts.columns = ['emotion', 'count']

fig_emotions = px.pie(df_emotion_counts, values='count', names='emotion', title="Répartition des émotions dans les avis")
st.plotly_chart(fig_emotions)

fig_scatter = px.scatter(df_exploded, x='date', y='rating', color='emotion_name', title="Notes en fonction des émotions")
st.plotly_chart(fig_scatter)

# print(df_anime)

# st.write("DataFrame nettoyé :", df_anime)

# st.dataframe(df_anime.head(10))