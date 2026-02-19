import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    """Clase de configuración central para el Scraper de Instagram."""

    # Credenciales de Instagram obtenidas de las variables de entorno
    INSTAGRAM_USERNAME = os.getenv("IG_USERNAME")
    INSTAGRAM_PASSWORD = os.getenv("IG_PASSWORD")

    # Definición de rutas y directorios para guardar datos
    DATA_FOLDER = "data"
    COOKIES_FILE = f"{DATA_FOLDER}/cookies.json"  # Archivo para guardar la sesión y evitar inicios de sesión constantes
    TREND_FILE = f"{DATA_FOLDER}/trend.txt"        # Archivo que guarda la última tendencia buscada para reutilizarla
    CSV_FILE = f"{DATA_FOLDER}/posts.csv"          # Archivo de salida final con los datos estructurados

    # Parámetros y límites del proceso de scraping
    POSTS_LIMIT = 40       # Número máximo de publicaciones a extraer
    SCROLL_TIMES = 10      # Veces que se hará scroll para cargar más publicaciones

    # URLs base de Instagram utilizadas para la navegación
    BASE_URL = "https://www.instagram.com"
    EXPLORE_URL = f"{BASE_URL}/explore/"
