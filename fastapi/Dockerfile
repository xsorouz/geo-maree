# ============================================================================
# 📦 Dockerfile — Service shom-fastapi
# Objectif : API REST FastAPI simple (Python 3.10) connectée à PostGIS
# ============================================================================

# 🌍 Image de base légère avec Python 3.10
FROM python:3.10-slim

# 📁 Répertoire de travail (dans le conteneur)
WORKDIR /app

# 📄 Copie des fichiers de dépendances
COPY requirements.txt .

# 🐍 Installation des dépendances
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 📄 Copie du code source FastAPI dans l’image
COPY . .

# 🚀 Commande de démarrage de l’API (à surcharger dans docker-compose si besoin)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
