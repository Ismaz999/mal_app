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

def insert_anime(animes_dict):
    with engine.connect() as connection:
        # Insertion test dans la table animes
        query = text("""
            INSERT INTO animes (mal_id, title, type, episodes, status, genres, url, image_url)
            VALUES (:mal_id, :title, :type, :episodes, :status, :genres, :url, :image_url)
        """)
        
        connection.execute(query, animes_dict)
        connection.commit()
        print("Données insérées")
