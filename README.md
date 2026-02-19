# Instagram Scraper

Este es un scraper automatizado para Instagram construido en Python. Permite extraer publicaciones, likes, comentarios, descripciones y fechas de una tendencia específica de forma progresiva, evitando duplicados y gestionando inteligentemente las cookies para no requerir inicios de sesión continuos.

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:
- **Python 3.10** o superior.
- **Google Chrome** instalado en el sistema.

## ⚙️ Instalación y Configuración

1. **Clonar/Abrir el Proyecto**
   Abre una terminal en la carpeta principal del proyecto (`/PruebaTecnica`).

2. **Crear e inicializar un Entorno Virtual**
   Es recomendable usar un entorno virtual para las dependencias.
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # En macOS/Linux
   # En Windows usa: .venv\Scripts\activate
   ```

3. **Instalar Dependencias**
   Instala las bibliotecas necesarias. Si no tienes un `requirements.txt`, las dependencias clave son `undetected-chromedriver`, `selenium`, `pandas` y `python-dotenv`.
   ```bash
   pip install -r requirements.txt
   ```
   *(Si el archivo `requirements.txt` no existe, ejecuta: `pip install undetected-chromedriver selenium pandas python-dotenv`)*

4. **Configurar Credenciales (.env)**
   Debes crear un archivo llamado `.env` en la raíz del proyecto y agregar tus credenciales de Instagram reales para el primer login:
   ```env
   IG_USERNAME=tu_usuario_de_instagram
   IG_PASSWORD=tu_contraseña_de_instagram
   ```
   *Nota: Nunca subas el archivo `.env` a un repositorio público.*

## 🚀 Ejecución del Scraper

Una vez configurado el entorno y el archivo `.env`, puedes iniciar la extracción simplemente ejecutando el archivo principal:

```bash
python main.py
```

### ¿Qué hace el script al ejecutarse?
1. **Autenticación**: Abre Chrome de manera indetectable e inicia sesión. Si ya habías iniciado sesión antes, reutilizará tus `cookies.json` para evitar el cuadro de login.
2. **Detección de Tendencia**: Busca una tendencia del momento capturando la primera palabra clave del tema de un post real en la pestaña "Explorar".
3. **Extracción y Guardado Progresivo**: Navega por los enlaces detectados bajo esa tendencia, extrae likes, comentarios, fecha y texto completo, y **guarda cada post inmediatamente** en el archivo `data/posts.csv`.

## 📂 Archivos de Salida (`data/`)

Toda la información generada se guarda automáticamente en la carpeta `data/`:
- `posts.csv`: Archivo principal con los resultados del scraping.
- `cookies.json`: Archivo de sesión que permite guardar tu sesión iniciada de Instagram.
- `trend.txt`: Almacena la última palabra clave buscada para re-utilizarla en la siguiente ejecución para consistencia.

## 🛑 Detener el Proceso
Si deseas detener el scraping en cualquier momento, simplemente presiona `Ctrl + C` en tu terminal. Gracias al guardado progresivo introducido, **no perderás** la información que se haya extraído hasta ese punto.
