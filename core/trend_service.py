import os
import time
import random
from selenium.webdriver.common.by import By
from config import Config

class TrendService:
    """Clase encargada de detectar una palabra clave de tendencia en la página de Explorar."""

    def get_or_create_trend(self, driver):
        """
        Retorna la última tendencia guardada en disco. Si no existe un archivo,
        navega, extrae una nueva tendencia, y la guarda.
        """
        if os.path.exists(Config.TREND_FILE):
            return self._read_trend()

        trend = self._detect_trend(driver)
        self._save_trend(trend)
        return trend

    def _detect_trend(self, driver):
        """
        Lógica heurística para encontrar una palabra de tendencia en la página /explore/.
        Estrategia: Busca el primer post válido, entra a la página,
        e inspecciona el título meta ('og:title') para extraer la primera palabra del tema central.
        """
        print("Detectando tendencia automática (Nivel Post Meta)...")
        driver.get(Config.EXPLORE_URL)
        
        # Pausa aleatoria para permitir que carguen las imágenes y scripts de React de IG
        time.sleep(random.uniform(8, 12))

        try:
            # 1. Seleccionar la primera miniatura (post real o reel) de la cuadrícula
            post_candidates = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/') or contains(@href, '/reels/')]")
            target_url = None
            
            # Filtramos links válidos (que la URL no esté incompleta)
            for candidate in post_candidates:
                href = candidate.get_attribute("href")
                if href and len(href.split('/')[-2]) > 5:
                    target_url = href
                    break
            
            if target_url:
                print(f"  Analizando primer post para tema: {target_url}")
                driver.get(target_url)
                time.sleep(5)
                
                # 2. Utilizar JavaScript para leer el título desde los metatags (sin requerir selectores inestables)
                meta_title = driver.execute_script("""
                    var m = document.querySelector('meta[property="og:title"]');
                    return m ? m.getAttribute('content') : "";
                """)
                
                if meta_title:
                    # 3. Limpieza: El estándar de IG suele ser "Motivo del Tema | Instagram"
                    # Eliminamos sufijos de marca
                    raw_theme = meta_title.replace(" | Instagram", "").replace(" - Instagram", "").split('|')[0].split('-')[0].strip()
                    
                    # REQUISITO DEL CLIENTE: Extraer solo la primera palabra clave principal del sujeto
                    # Evitamos saltos de línea y fragmentos envueltos en comillas.
                    first_word = raw_theme.split(' ')[0].split("'")[0].split('"')[0].strip()
                    
                    # Validamos longitud y algunas palabras clave inútiles comunes
                    if first_word and len(first_word) > 2 and first_word.lower() not in ["post", "reel", "video"]:
                        print(f"  Tendencia de palabra única detectada: {first_word}")
                        return first_word.lower()
        except Exception as e:
            print(f"  Error en detección semántica: {e}")

        # 4. Fallback si algo falló para poder continuar la ejecución de cualquier forma
        # Se fijó la palabra 'ingenieria' acorde a la decisión anterior.
        print("  Fallback: Usando tendencia por defecto 'ingenieria'")
        return "ingenieria"

    def _save_trend(self, trend):
        """Persiste la palabra calculada en archivo para ser reutilizada en futuras corridas."""
        with open(Config.TREND_FILE, "w", encoding="utf-8") as f:
            f.write(trend)

    def _read_trend(self):
        """Lee la palabra de tendencia calculada en el pasado."""
        with open(Config.TREND_FILE, "r", encoding="utf-8") as f:
            trend = f.read().strip()
            print(f"Tendencia reutilizada: {trend}")
            return trend

