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

## 2. Installer les dépendances

``` bash
python -m pip install -r requirements.txt
```

## 3. Configurer la base de données

Créer un fichier `.env` à la racine du projet :

``` env
POSTGRES_HOST = ""
POSTGRES_PORT = 
POSTGRES_DATABASE = ""
POSTGRES_USER = ""
POSTGRES_PASSWORD = ""
```

## 4. Lancer les tests

### Avec couverture

- **Dans le terminal**

``` bash
PYTHONPATH=src pytest src/tests/ --cov=src/tests
```

- **Avec un rapport html**

``` bash
PYTHONPATH=src pytest src/tests/ --cov=src/tests --cov-report=html
```

### Sans couverture

``` bash
PYTHONPATH=src pytest src/tests/ -v
```

## 5. Lancer l'application 

``` bash
python main.py
```

- **Création automatique de l’utilisateur administrateur**

Lors du premier lancement du programme (`python main.py`), un utilisateur administrateur est automatiquement créé dans la base de données s’il n’existe pas déjà.

Cet administrateur par défaut dispose des identifiants suivants :

- Nom d’utilisateur : admin
- Mot de passe : Admin123@

Ce compte permet d’accéder aux fonctionnalités réservées à l’administrateur dès la première exécution du projet étant donné qu'il n'y a pas de superusers.

**NB** : Vous ne devez jamais supprimer les comptes de tous les admins (il faut au moins en avoir un).

# Commande supplémentaire utile (si soucis de package)

``` bash
python -m pip install -e .
```




# Auteurs

Projet réalisé par :

- COTTEROT Hippolyte
- MALAHEL Olivier
- PELLOT Louis
