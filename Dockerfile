FROM python:3.11-slim

WORKDIR /app

# Dépendances système utiles
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code (dossiers + fichiers nécessaires)
COPY dao ./dao
COPY service ./service
COPY business_object ./business_object
COPY utils ./utils
COPY views ./views

COPY main.py .
COPY import_tmdb.py .
COPY demo_add_from_csv.py .
COPY README.md .

# Lancer l'application
CMD ["python", "main.py"]
