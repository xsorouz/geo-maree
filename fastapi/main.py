# =============================================================================
# 🎯 API Marées — SHOM
# Microservice FastAPI pour test de connectivité dans une stack Docker
# =============================================================================

from fastapi import FastAPI
import os
import dotenv

# 🔄 Chargement des variables d'environnement depuis le fichier .env
dotenv.load_dotenv()

# 🔧 Lecture de quelques variables (non obligatoires ici mais utile pour debug)
ENV = os.getenv("ENV", "dev")
API_PORT = os.getenv("API_PORT", "8000")
DB_HOST = os.getenv("DB_HOST", "non défini")

# 🚀 Initialisation de l'application FastAPI
app = FastAPI(
    title="API Marées - SHOM",
    description="Microservice FastAPI de démonstration dans la stack géospatiale SHOM",
    version="0.1.0"
)

# ============================================================================
# ✅ Endpoint racine — simple message de bienvenue
# ============================================================================
@app.get("/")
def home():
    return {
        "message": "Bienvenue sur l'API Marées - SHOM 🌊",
        "env": ENV,
        "port": API_PORT,
        "db_host": DB_HOST
    }

# ============================================================================
# ✅ Endpoint de test — ping
# ============================================================================
@app.get("/ping")
def ping():
    return {"pong": True}

# ============================================================================
# 🧪 Endpoint de statut pour monitoring / test nginx
# ============================================================================
@app.get("/status")
def status():
    return {
        "status": "ok",
        "service": "api-marees",
        "stack": "SHOM",
        "message": "Statut API valide ✅"
    }
