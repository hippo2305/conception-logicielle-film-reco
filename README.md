Ce projet, développé dans le cadre du cours de conception logicielle de 2e année à
l'ENSAI, consiste à :

- Récupérer des données sur les films via l'API TMDB
- Gérer une base de donnée des films préférés des utilisateurs
- Fournir des fonctionnalités de recherche de film à partir de l'API

# Installation et Mise en route

## 1. Cloner le dépôt

```bash
git clone https://github.com/hippo2305/conception-logicielle-film-reco.git
cd conception-logicielle-film-reco
```

## 2. Installer l'environnement

```bash
uv sync
```

## 3. Configurer la base de données

Deux solutions pour mettre en place la base de données

- **Base de données locale**

Créer un fichier `.env` à la racine du projet :

```env
POSTGRES = False
```

L'application va automatiquement créer une base de données en local, avec SQLite.

- **Base de données hébergée avec PostgreSQL**

Lancer une instance PostgreSQL sur le datalab de votre choix (exemple : https://datalab.sspcloud.fr/)

Copier les informations de connection et les ajouter dans le `.env` :

```env
POSTGRES = True
POSTGRES_HOST =
POSTGRES_PORT =
POSTGRES_DATABASE =
POSTGRES_USER =
POSTGRES_PASSWORD =
```

- **Mettre en place la connexion à l'API TMDB**

Créer un compte sur https://www.themoviedb.org/

Une fois connecté, vous avez votre clé et votre token ici : https://www.themoviedb.org/settings/api

Ajouter ces informations dans le `.env` :

```env
TMDB_BASE_URL = https://api.themoviedb.org/3
TMDB_API_KEY =
TMDB_API_TOKEN =
```

## 4. Lancer les tests

- **Dans le terminal**

```bash
uv run pytest
```

## 5. Lancer l'application

```bash
uv run uvicorn api:app --reload
```

## Auteurs

Projet réalisé par :

- COTTEROT Hippolyte
- MALAHEL Olivier
- PELLOT Louis
