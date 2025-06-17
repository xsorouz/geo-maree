import requests
import argparse
import logging
import os
import time
from datetime import datetime

# Configuration du logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constantes
STATION_ID = 3  # Brest
BASE_URL = "https://services.data.shom.fr/refmar/api/v1/dl/observations"
DOSSIER_SORTIE = "data/public"
POLLING_INTERVAL = 10  # secondes
MAX_RETRIES = 30       # ~5 minutes

def demander_telechargement(station_id, debut_iso, fin_iso):
    """Envoie une requête POST à l'API asynchrone pour lancer le traitement"""
    payload = {
        "station": str(station_id),
        "start": debut_iso,
        "end": fin_iso,
        "format": "csv"
    }

    logger.info("📨 Envoi de la requête asynchrone...")
    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()

        if response.status_code != 202:
            logger.error(f"❌ Requête refusée : {response.status_code} - {response.text}")
            return None, None

        job_info = response.json()
        logger.info("✅ Requête acceptée. Tâche en cours de traitement.")
        return job_info.get("status_url"), job_info.get("download_url")

    except requests.RequestException as e:
        logger.error(f"❌ Erreur lors de la requête : {e}")
        return None, None

def attendre_et_telecharger(status_url, download_url, chemin_fichier):
    """Attend la fin du traitement, puis télécharge le fichier"""
    logger.info("🕒 Attente de la fin du traitement...")

    for tentative in range(MAX_RETRIES):
        try:
            r = requests.get(status_url)
            r.raise_for_status()
            status = r.json()
            etat = status.get("status")

            if etat == "completed":
                logger.info("✅ Tâche terminée. Téléchargement du fichier...")
                fichier = requests.get(download_url)
                fichier.raise_for_status()

                os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
                with open(chemin_fichier, "wb") as f:
                    f.write(fichier.content)

                logger.info(f"📁 Fichier téléchargé avec succès : {chemin_fichier}")
                return True

            elif etat == "failed":
                logger.error("❌ Échec du traitement côté serveur.")
                return False

            logger.debug(f"Statut actuel : {etat} (tentative {tentative + 1}/{MAX_RETRIES})")
            time.sleep(POLLING_INTERVAL)

        except Exception as e:
            logger.warning(f"⚠️ Erreur pendant le polling : {e}")
            time.sleep(POLLING_INTERVAL)

    logger.error("⏳ Timeout dépassé. Le fichier n'a pas été généré.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Téléchargement asynchrone des données marégraphiques de Brest (station 3)")
    parser.add_argument("--debut", help="Date de début (YYYY-MM-DD), défaut = 2024-01-01")
    parser.add_argument("--fin", help="Date de fin (YYYY-MM-DD), défaut = aujourd'hui")
    parser.add_argument("--debug", action="store_true", help="Active le mode debug")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("🔍 Mode debug activé")

    date_debut = args.debut if args.debut else "2024-01-01"
    date_fin = args.fin if args.fin else datetime.now().strftime("%Y-%m-%d")

    try:
        debut_iso = datetime.strptime(date_debut, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00Z")
        fin_iso = datetime.strptime(date_fin, "%Y-%m-%d").strftime("%Y-%m-%dT23:59:59Z")
    except ValueError:
        logger.error("❌ Format de date invalide. Utiliser YYYY-MM-DD.")
        return

    nom_fichier = f"brest_async_{date_debut}_au_{date_fin}.csv"
    chemin_fichier = os.path.join(DOSSIER_SORTIE, nom_fichier)

    logger.info(f"🗓️ Période demandée : {date_debut} → {date_fin}")
    logger.info(f"📍 Fichier cible : {chemin_fichier}")

    status_url, download_url = demander_telechargement(STATION_ID, debut_iso, fin_iso)

    if status_url and download_url:
        attendre_et_telecharger(status_url, download_url, chemin_fichier)
    else:
        logger.error("🚫 Impossible de lancer la tâche asynchrone.")

if __name__ == "__main__":
    main()
