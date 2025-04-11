import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import sqlalchemy_utils
from sqlalchemy_utils import database_exists, create_database

from local_settings import postgresql as settings

def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

engine = get_engine(settings['user'], settings['passwd'], settings['host'], settings['port'], settings['db'])

def insert_anime(anime_dict, review_dict, emotions_dict):
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
            print("Données insérées avec succès")

        except Exception as e:
            transaction.rollback()
            print(f"Erreur lors de l'insertion: {e}")
            raise e
