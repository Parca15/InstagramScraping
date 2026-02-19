from core.driver_manager import DriverManager
from core.auth_service import AuthService
from core.trend_service import TrendService
from core.scraper_service import ScraperService
from core.storage_service import StorageService
from config import Config

def main():
    """
    Función principal que orquesta todo el flujo del Scraper.
    """
    # 1. Crear el navegador (driver)
    driver = DriverManager.create_driver()
    
    try:
        # 2. Manejar la autenticación (login con credenciales o uso de cookies persistentes)
        auth = AuthService(driver, Config.INSTAGRAM_USERNAME, Config.INSTAGRAM_PASSWORD)
        auth.login()

        # 3. Determinar o reutilizar la palabra clave o hashtag a buscar
        trend_service = TrendService()
        trend = trend_service.get_or_create_trend(driver)
        
        # 4. Inicializar servicios de guardado y de extracción (scraper)
        scraper = ScraperService(driver)
        storage = StorageService()
        
        # 5. Guardado progresivo (Incremental):
        # A medida que el generador 'scrape_posts' arroja una publicación, se guarda en el CSV inmediatamente.
        # Se le pasa la cantidad máxima y los "existing_ids" (IDs de posts guardados previamente) para no duplicarlos.
        for post in scraper.scrape_posts(trend, Config.POSTS_LIMIT, existing_ids=storage.get_existing_ids()):
            storage.save([post])
            
    finally:
        # 6. Al terminal (o si ocurre una excepción como Ctrl+C), asegurar que se cierre el navegador
        driver.quit()

if __name__ == "__main__":
    main()
