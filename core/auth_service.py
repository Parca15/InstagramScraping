import os
import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from config import Config

class AuthService:
    """Clase encargada de la autenticación del usuario en Instagram (Login y manejo de Cookies)."""

    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        """
        Punto de entrada para el inicio de sesión. 
        Intenta cargar cookies previas para evitar iniciar sesión repetidamente;
        si falla, realiza un inicio de sesión manual.
        """
        print("Accediendo a la página de login...")
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        # 1. Intento de inicio de sesión con Cookies
        if os.path.exists(Config.COOKIES_FILE):
            self._load_cookies()
            self.driver.refresh()
            time.sleep(7)

        # 2. Si la URL sigue siendo la de login, significa que las cookies expiraron o fallaron.
        if "login" in self.driver.current_url:
            self._perform_login()
        else:
            print(f"Sesión activa con cookies reutilizadas.")

    def _perform_login(self):
        """Ejecuta el login manual ingresando credenciales y simulando un comportamiento humano."""
        try:
            # Limpiar popups de bloqueo (ej. "Aceptar cookies")
            self.driver.execute_script("""
                document.querySelectorAll('button._a9--._ap32, button[innerHTML*="cookies"], button[innerHTML*="Aceptar"]').forEach(el => el.click());
            """)
            time.sleep(2)

            # Encontrar los campos de usuario y contraseña
            user_field = self.driver.find_element(By.NAME, "username")
            pass_field = self.driver.find_element(By.NAME, "password")

            # Escribir con pequeñas pausas intermedias
            user_field.send_keys(self.username)
            time.sleep(random.uniform(1, 2))
            pass_field.send_keys(self.password)
            time.sleep(random.uniform(1, 2))

            # Enviar el formulario
            pass_field.submit()
            time.sleep(10)

            # Verificar si el login fue exitoso 
            if "login" not in self.driver.current_url.lower():
                print("Login exitoso.")
                self._save_cookies()  # Guardar las nuevas cookies
            else:
                print("El login puede haber fallado o requiere autenticación de dos pasos (OTP).")
                
        except Exception as e:
            print(f"Error en login: {e}")

    def _save_cookies(self):
        """Guarda la sesión actual (cookies) en un archivo JSON en disco."""
        with open(Config.COOKIES_FILE, "w") as f:
            json.dump(self.driver.get_cookies(), f)

    def _load_cookies(self):
        """Carga las cookies del archivo JSON a la sesión activa del navegador."""
        with open(Config.COOKIES_FILE, "r") as f:
            for cookie in json.load(f):
                try:
                    self.driver.add_cookie(cookie)
                except:
                    pass