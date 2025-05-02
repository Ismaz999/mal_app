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

## Architecture & Technologies

- **Frontend & Déploiement** : Streamlit (web app, cloud)
- **Scraping web** : BeautifulSoup, Requests
- **Traitement du texte** : NLTK, Regex
- **Analyse de sentiments & émotions** : Transformers (BERT, Roberta), HuggingFace
- **Stockage & gestion de données** : PostgreSQL (Supabase), SQLAlchemy
- **Visualisation** : Plotly, Matplotlib, WordCloud

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

## Exemples de résultats
![aperçu des résultats 1](https://i.imgur.com/NQ3PTf1.png)
![aperçu des résultats 2](https://i.imgur.com/JQww72S.png)
---
