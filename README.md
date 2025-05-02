## App available here : [Review analysis](https://malapp-analyse.streamlit.app/)

#  Anime Sentiment Analysis

Analysez les avis d’animes grâce au NLP, à la data engineering et à la data science.

---

## Présentation

Cette application Streamlit permet d’analyser les sentiments et émotions présents dans les avis d’animes publiés sur MyAnimeList.  

> **Objectif** : Proposer un outil interactif  tout en illustrant un workflow complet de data project.

---

## Fonctionnalités principales

- 🔎 Recherche d’animes sur MyAnimeList
- 🕸️ Scraping automatisé des avis utilisateurs
- 🤗 Analyse des sentiments et émotions (BERT, Transformers)
- 📊 Visualisations interactives (courbes, camemberts, heatmaps, wordclouds)
- 🗂️ Filtrage par date, score, émotion
- 💾 Stockage des données en base PostgreSQL (Supabase)

---

## Aperçu de l’application

![Aperçu de l’app](https://i.imgur.com/yCRMKXw.png)

---

## Architecture du projet

- **Frontend** : Streamlit
- **Backend** : Python, BeautifulSoup, Transformers, NLTK
- **Base de données** : PostgreSQL (Supabase)
- **Visualisation** : Plotly, Matplotlib, WordCloud

---

## Rôles et compétences mobilisées

### 🛠️ Data Engineer

- Scraping robuste des avis sur MyAnimeList (gestion des erreurs, parsing HTML)
- Automatisation de la collecte et du stockage (SQLAlchemy, Supabase)
- Gestion des environnements et des secrets (Streamlit Cloud, .gitignore)

### 📊 Data Analyst

- Nettoyage et structuration des données textuelles
- Exploration des tendances (scores, dates, volumes d’avis)
- Visualisation interactive (courbes, pie charts, heatmaps, wordclouds)

### 🤖 Data Scientist

- Application de modèles NLP pré-entraînés (BERT, DistilBERT, Roberta)
- Classification des sentiments et détection des émotions
- Interprétation des résultats et restitution visuelle

---

## Comment utiliser l’application

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Lancer l’application

```bash
streamlit run app.py
```

### 3. Utilisation

1. Saisir le nom d’un anime
2. Sélectionner dans la liste proposée
3. Lancer l’analyse
4. Explorer les résultats dans l’onglet “Analysis”

---

## Technologies utilisées

- **Python** (3.12)
- **Streamlit**
- **Transformers** (HuggingFace)
- **NLTK**
- **Plotly**
- **Matplotlib**
- **BeautifulSoup**
- **SQLAlchemy**
- **Supabase (PostgreSQL)**

---

## Exemples de résultats
![aperçu des résultats 1](https://i.imgur.com/NQ3PTf1.png)
![aperçu des résultats 2](https://i.imgur.com/JQww72S.png)
---
