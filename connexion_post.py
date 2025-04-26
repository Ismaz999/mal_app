import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

DB_CONFIG = {
    'user': st.secrets["DB_USER"],
    'password': st.secrets["DB_PASSWORD"],
    'host': st.secrets["DB_HOST"],
    'port': st.secrets["DB_PORT"],
    'dbname': st.secrets["DB_NAME"]
}

def get_engine():
    DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}?sslmode=require"
    return create_engine(DATABASE_URL)

engine = get_engine()

def insert_anime(anime_dict, review_dict, emotions_dict):
    # print("Contenu de emotions_dict avant insertion:", emotions_dict)
    with engine.connect() as connection:
        try:
            transaction = connection.begin()

            anime_query = text("""
                INSERT INTO animes (mal_id, title, type, episodes, status, genres, url, image_url)
                VALUES (:mal_id, :title, :type, :episodes, :status, :genres, :url, :image_url)
                RETURNING anime_id
            """)
            result = connection.execute(anime_query, anime_dict)
            anime_id = result.scalar()

            for i in range(len(review_dict['review_text'])):
                current_review = review_dict.copy()
                current_review['review_text'] = review_dict['review_text'][i]
                current_review['rating'] = review_dict['rating'][i]
                current_review['review_date'] = review_dict['review_date'][i]
                current_review['anime_id'] = anime_id

                review_query = text("""
                    INSERT INTO reviews (review_text, rating, date, anime_id)
                    VALUES (:review_text, :rating, :review_date, :anime_id)
                    RETURNING review_id
                """)
                review_result = connection.execute(review_query, current_review)
                review_id = review_result.scalar()

                current_emotion = emotions_dict.copy()
                current_emotion['sentiment'] = emotions_dict['sentiment'][i]
                # print(f"Valeur de fear pour la review {i}:", emotions_dict['fear'][i])

                current_emotion['neutral'] = float(emotions_dict['neutral'][i]) if pd.notna(emotions_dict['neutral'][i]) else None
                current_emotion['joy'] = float(emotions_dict['joy'][i]) if pd.notna(emotions_dict['joy'][i]) else None
                current_emotion['disgust'] = float(emotions_dict['disgust'][i]) if pd.notna(emotions_dict['disgust'][i]) else None
                current_emotion['surprise'] = float(emotions_dict['surprise'][i]) if pd.notna(emotions_dict['surprise'][i]) else None
                current_emotion['sadness'] = float(emotions_dict['sadness'][i]) if pd.notna(emotions_dict['sadness'][i]) else None
                current_emotion['fear'] = float(emotions_dict['fear'][i]) if pd.notna(emotions_dict['fear'][i]) else None
                current_emotion['anger'] = float(emotions_dict['anger'][i]) if pd.notna(emotions_dict['anger'][i]) else None
                current_emotion['review_id'] = review_id

                emotions_query = text("""
                    INSERT INTO sentiment_analysis (sentiment, neutral, joy, disgust, surprise, sadness, fear, anger, review_id)
                    VALUES (:sentiment, :neutral, :joy, :disgust, :surprise, :sadness, :fear, :anger, :review_id)
                """)
                connection.execute(emotions_query, current_emotion)

            transaction.commit()
            # print("Données insérées avec succès")

        except Exception as e:
            transaction.rollback()
            print(f"Erreur lors de l'insertion: {e}")
            raise e

def check_anime_exists(mal_id):
    with engine.connect() as connection:
        query = text("SELECT anime_id FROM animes WHERE mal_id = :mal_id")
        result = connection.execute(query, {'mal_id': mal_id})
        return result.scalar() is not None

def get_existing_data_from_db(anime_id):
    with engine.connect() as connection:
        query = text("""
            SELECT r.review_text, r.rating, r.date, 
                   s.sentiment, s.neutral, s.joy, s.disgust, 
                   s.surprise, s.sadness, s.fear, s.anger
            FROM reviews r
            JOIN sentiment_analysis s ON r.review_id = s.review_id
            WHERE r.anime_id = (
                SELECT anime_id FROM animes WHERE mal_id = :mal_id
            )
        """)
        result = connection.execute(query, {'mal_id': anime_id})
        rows = result.fetchall()
        
        if not rows:
            return None
            
        df = pd.DataFrame(rows, columns=['review', 'rating', 'date', 
                                       'sentiment', 'neutral', 'joy', 
                                       'disgust', 'surprise', 'sadness', 
                                       'fear', 'anger'])
        return df