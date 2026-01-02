import os
from dotenv import load_dotenv
from pathlib import Path


# Charger le fichier .env depuis la racine du projet
ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """
    Configuration globale du projet.
    Toutes les variables d'environnement sont centralisées ici.
    """

    LUCCA_API_URL = os.getenv("LUCCA_API_URL")
    LUCCA_API_TOKEN = os.getenv("LUCCA_API_TOKEN")

    # Paramètres généraux du job
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
    LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "json").lower()


def validate_config():
    """
    Vérifie que les variables critiques sont bien définies.
    """
    missing_vars = []

    if not Config.LUCCA_API_URL:
        missing_vars.append("LUCCA_API_URL")
    if not Config.LUCCA_API_TOKEN:
        missing_vars.append("LUCCA_API_TOKEN")

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
