import undetected_chromedriver as uc

class DriverManager:
    """Clase responsable de inicializar y configurar el navegador Chrome."""

    @staticmethod
    def create_driver():
        """
        Crea y retorna una instancia de undetected_chromedriver (Chrome indetectable).
        Configura varias opciones para simular ser un navegador real y evitar bloqueos.
        """
        options = uc.ChromeOptions()
        options.add_argument("--start-maximized")         # Inicia el navegador maximizado
        options.add_argument("--no-sandbox")              # Desactiva el modo seguro, necesario en algunos servidores
        options.add_argument("--disable-dev-shm-usage")   # Previene problemas de memoria al compartir la RAM
        options.add_argument("--disable-notifications")   # Oculta las típicas peticiones de "Mostrar notificaciones"
        options.add_argument("--lang=es-ES")              # Fija el idioma en español para recibir HTML acorde al idioma
        
        # Perfil persistente en disco. Ayuda a Instagram a reconocer dispositivos recurrentes (más credibilidad)
        options.add_argument("--user-data-dir=/tmp/chrome_ig_profile")

        # Se inicializa el driver. Se forza la versión 144 debido a los requerimientos del entorno de Chrome
        driver = uc.Chrome(options=options, version_main=144)
        return driver