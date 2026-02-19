import pandas as pd
import os
from config import Config

class StorageService:
    """Clase encargada de manejar la persistencia de datos y lectura/escritura del CSV."""

    def get_existing_ids(self):
        """
        Lee el archivo CSV (si existe) y extrae todos los IDs de las publicaciones.
        Esto sirve para evitar descargar y procesar duplicados en futuras ejecuciones.
        """
        if not os.path.exists(Config.CSV_FILE):
            return set()
        
        try:
            # Leemos el archivo asegurando que los IDs se traten como texto completo
            df = pd.read_csv(Config.CSV_FILE, dtype=str, encoding="utf-8")
            return set(df["id"].tolist())
        except:
            # Si ocurre algún error en la lectura (ej. archivo corrupto), asumimos vacío
            return set()

    def save(self, posts):
        """
        Recibe una lista de diccionarios de post, filtra los duplicados usando id,
        y luego anexa (o crea) los resultados en posts.csv
        """
        if not posts:
            print("No hay nuevos posts por procesar.")
            return

        # 1. Obtenemos los IDs que ya tenemos guardados
        existing_ids = self.get_existing_ids()
        
        # 2. Filtramos la lista entrante para dejar solo aquellos IDs que son nuevos
        new_posts = [p for p in posts if p["id"] not in existing_ids]

        if not new_posts:
            # print("No hay nuevos posts por guardar.")  # (Silenciado opcionalmente para evitar log repetitivo)
            return

        # 3. Convertimos la lista de diccionarios filtrados en un DataFrame de Pandas
        df_new = pd.DataFrame(new_posts)
        
        if os.path.exists(Config.CSV_FILE):
            # 4a. Si el archivo ya existía, lo leemos y anexamos las filas nuevas usando concat
            existing_df = pd.read_csv(Config.CSV_FILE, dtype=str, encoding="utf-8")
            df_final = pd.concat([existing_df, df_new], ignore_index=True).drop_duplicates(subset=["id"])
        else:
            # 4b. Caso contrario, el resultado final es simplemente los nuevos datos
            df_final = df_new

        # 5. Escribimos al archivo CSV, ignorando la columna de índices automático
        df_final.to_csv(Config.CSV_FILE, index=False, encoding="utf-8")
        print(f"{len(new_posts)} nuevos posts guardados.")

