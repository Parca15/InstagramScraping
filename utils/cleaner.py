from datetime import datetime
import re

class Cleaner:

    @staticmethod
    def clean_text(text):
        if not text:
            return ""

        # REQUISITO 3.5: Eliminación de saltos de línea y espacios dobles
        text = text.replace("\n", " ").replace("\r", " ")
        # Eliminar espacios múltiples usando regex
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def normalize_date(date_str):
        """
        Garantiza formato DD-MM-YYYY (REQUISITO 3.5)
        """
        if not date_str:
            return ""
        try:
            # Intentar parsear ISO format YYYY-MM-DD
            if '-' in date_str and len(date_str) >= 10:
                date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                return date_obj.strftime("%d-%m-%Y")
            return date_str
        except:
            return date_str

    @staticmethod
    def scraping_date():
        return datetime.now().strftime("%d-%m-%Y")
