"""
Configuração do Selenium WebDriver — versão simples e previsível.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def criar_driver(headless: bool = True) -> webdriver.Chrome:
    """Cria e retorna uma instância do Chrome com configuração simples."""
    options = Options()

    if headless:
        options.add_argument("--headless")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--log-level=3")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver
