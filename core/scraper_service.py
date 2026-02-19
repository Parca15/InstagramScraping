import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.cleaner import Cleaner

class ScraperService:
    """Clase principal para extraer información de los posts e interactuar con la página."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def scrape_posts(self, hashtag, limit=50, existing_ids=None):
        """
        Inicia la búsqueda en Instagram, hace scroll para cargar posts y navega por cada uno.
        Al ser un generador (`yield`), devuelve un post a la vez de forma progresiva.
        """
        if existing_ids is None:
            existing_ids = set()
            
        # Determinar si vamos a una página de hashtag directo o a una búsqueda por palabra clave
        if hashtag.startswith("#"):
            tag_name = hashtag.replace("#", "").strip()
            url = f"https://www.instagram.com/explore/tags/{tag_name}/"
        else:
            query = hashtag.replace(" ", "+")
            url = f"https://www.instagram.com/explore/search/keyword/?q={query}"

        print(f"Buscando tendencia: {hashtag}")
        self.driver.get(url)
        
        # Simular una pausa de lectura humana
        time.sleep(random.uniform(6, 8))
        self._scroll()
        
        count = 0
        # Iterar progresivamente sobre cada post hallado
        for post in self._extract(limit, existing_ids):
            yield post
            count += 1
            if count >= limit:
                break

    def _scroll(self):
        """Hace scroll hacia abajo múltiples veces para cargar miniaturas en la vista de Explorar."""
        for _ in range(10):
            self.driver.execute_script("window.scrollBy(0, 3000);")
            time.sleep(random.uniform(2, 4))

    def _extract(self, limit, existing_ids):
        """Busca todas las URLs de post visibles y las visita individualmente."""
        hrefs = []
        links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        
        seen = set()
        for link in links:
            url = link.get_attribute("href")
            # Evitar enlaces repetidos encontrados en la misma visualización
            if url and url not in seen:
                seen.add(url)
                hrefs.append(url)
        
        print(f"Enlaces encontrados: {len(hrefs)}")
        for url in hrefs:
            try:
                # Extraer el código único de la URL (ej. /p/ABCDEFG/ -> ABCDEFG)
                post_id = url.split("/p/")[1].split("/")[0]
                
                # Omitir si ya fue guardado en disco en una ejecución pasada
                if post_id in existing_ids:
                    continue

                self.driver.get(url)
                time.sleep(5)  # Esperar a que la página del post singular se renderice

                # Extraer metadata de la publicación
                post_data = self._extract_post_data(url, post_id)
                if post_data:
                    print(f"Post extraído: {post_data['author']} ({post_data['likes']} likes, {post_data['comments']} comments)")
                    yield post_data

            except Exception as e:
                print(f"Error en post {url}: {e}")
                continue


    def _extract_post_data(self, url, post_id):
        """Construye un diccionario con la estructura de la publicación recolectando datos del HTML y Metatags."""
        try:
            # Estructura base
            post_data = {
                "id": post_id,
                "text": "Post de Instagram",
                "author": "unknown",
                "likes": "0",
                "comments": "0",
                "url": url,
                "post_date": Cleaner.scraping_date(),
                "scraping_date": Cleaner.scraping_date()
            }

            # Autor
            try:
                el = self.driver.find_element(By.XPATH, "//header//a[@role='link'] | //a[contains(@class, 'notranslate')]")
                post_data["author"] = Cleaner.clean_text(el.text)
            except: pass

            # Fecha original del post
            try:
                time_el = self.driver.find_element(By.TAG_NAME, "time")
                dt = time_el.get_attribute("datetime") or time_el.get_attribute("title")
                if dt: post_data["post_date"] = Cleaner.normalize_date(dt[:10])
            except: pass

            # Métricas y Texto de Descripción (JS Extractor robusto leyendo de los Metatags <head>)
            stats = self.driver.execute_script(r"""
                var res = {likes: "0", comments: "0", author_fallback: "", full_text: ""};
                
                function clean(v) {
                    if(!v) return "0";
                    // Obtiene solo la parte numérica usando regex global soportando K/M
                    var m = v.match(/[\d,.]+([KkMm])?/);
                    return m ? m[0].replace(/[.,]$/, '') : "0";
                }
                
                // Buscar el metatag descriptivo que siempre contiene la sintaxis precisa: '10 Likes, 2 Comments...'
                var meta = document.querySelector('meta[name="description"]') || document.querySelector('meta[property="og:description"]');
                if (meta) {
                    var d = meta.getAttribute('content');
                    var lMatch = d.match(/([\d,.]+[KkMm]?)\s*(?:likes|me gusta)/i);
                    var cMatch = d.match(/([\d,.]+[KkMm]?)\s*(?:comments|comentarios|comment)/i);
                    
                    if (lMatch) res.likes = clean(lMatch[1]);
                    if (cMatch) res.comments = clean(cMatch[1]);
                    
                    var parts = d.split(' - ');
                    if (parts.length > 1) res.author_fallback = parts[1].split(' el ')[0].split(' on ')[0].trim();
                    
                    // Extraer descripción completa y limpia (lo que está entre comillas después de los dos puntos)
                    var tMatch = d.match(/:\s*"(.*)"/s);
                    if (tMatch) {
                        res.full_text = tMatch[1];
                    } else if (d.includes('"')) {
                        res.full_text = d.split('"')[1].trim();
                        // remover comillas al final si existen
                        if(res.full_text.endsWith('"')) {
                            res.full_text = res.full_text.slice(0, -1);
                        } else if(res.full_text.endsWith('. "')) {
                             res.full_text = res.full_text.slice(0, -3);
                        }
                    }
                }
                return res;
            """)

            # Asignar a nuestro diccionario resultante los datos hallados en JS
            if stats:
                post_data["likes"] = stats.get("likes", "0")
                post_data["comments"] = stats.get("comments", "0")
                if stats.get("full_text"):
                    post_data["text"] = Cleaner.clean_text(stats["full_text"])
                # Fallback de autor asegurado
                if post_data["author"] == "unknown" and stats.get("author_fallback"):
                    post_data["author"] = Cleaner.clean_text(stats["author_fallback"])

            return post_data
        except:
            return None

