Ce projet, développé dans le cadre du cours de conception logicielle de 2e année à
l'ENSAI, consiste à : 
- Récupérer des données sur les films via l'API TMDB
- Gérer une base de donnée des films préférés des utilisateurs
- Fournir des fonctionnalités de recherche de film à partir de l'API

# Installation et Mise en route

## 1. Cloner le dépôt

Le dépôt étant publique, il faut avoir les accès nécessaires.

``` bash
git clone https://github.com/hippo2305/conception-logicielle-film-reco.git
cd conception-logicielle-film-reco
```

## 2. Installer l'environnement

``` bash
uv sync
```

## 3. Configurer la base de données

Créer un fichier `.env` à la racine du projet :

``` env
PPOSTGRES = False
POSTGRES_HOST =
POSTGRES_PORT =
POSTGRES_DATABASE =
POSTGRES_USER =
POSTGRES_PASSWORD =
TMDB_BASE_URL =
TMDB_API_KEY =
TMDB_API_TOKEN =
```

## 4. Lancer les tests

- **Dans le terminal**

``` bash
uv run pytest
```
## 5. Lancer l'application 

``` bash
uv run python main.py
```

- **Création automatique de l’utilisateur administrateur**

Lors du premier lancement du programme (`python main.py`), un utilisateur administrateur est automatiquement créé dans la base de données s’il n’existe pas déjà.


Ce compte permet d’accéder aux fonctionnalités réservées à l’administrateur dès la première exécution du projet étant donné qu'il n'y a pas de superusers.

**NB** : Vous ne devez jamais supprimer les comptes de tous les admins (il faut au moins en avoir un).

## Auteurs

Projet réalisé par :

- COTTEROT Hippolyte
- MALAHEL Olivier
- PELLOT Louis
