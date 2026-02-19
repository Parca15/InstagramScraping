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
                
                # 2. Utilizar JavaScript para extraer la mejor palabra clave de los metadatos de la publicación
                trend_word = driver.execute_script("""
                    // Primera estrategia: Extraer el primer hashtag de la descripción (más preciso para categorías)
                    var metaDesc = document.querySelector('meta[property="og:description"]') || document.querySelector('meta[name="description"]');
                    if (metaDesc) {
                        var d = metaDesc.getAttribute('content');
                        // Buscar el primer hashtag con al menos 3 letras
                        var hashtags = d.match(/#([a-zA-ZáéíóúñÁÉÍÓÚÑ0-9_]{3,})/g);
                        if (hashtags && hashtags.length > 0) {
                            return hashtags[0].replace('#', '');
                        }
                    }
                    
                    // Segunda estrategia fallback: Extraer una palabra representativa del título
                    var m = document.querySelector('meta[property="og:title"]');
                    if (m) {
                        var title = m.getAttribute('content');
                        var theme = title.replace(" | Instagram", "").split('|')[0].trim();
                        // Buscar la primera palabra sustancial (más de 3 letras estándar)
                        var words = theme.match(/[a-zA-ZáéíóúÁÉÍÓÚñÑ]{4,}/g);
                        if (words && words.length > 0) {
                            return words[0];
                        }
                    }
                    return "";
                """)
                
                if trend_word:
                    trend_word = trend_word.lower()
                    if trend_word not in ["post", "reel", "video", "instagram", "photo"]:
                        print(f"  Tendencia o categoría extraída automáticamente: {trend_word}")
                        return trend_word
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

