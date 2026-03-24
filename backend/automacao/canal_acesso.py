"""
Automação de consulta ao Canal de Acesso via Selenium.

URL: http://atendews.cemig.ad.corp/PesquisaUsuario
(Requer acesso à rede corporativa CEMIG)

Fluxo:
  1. Abre URL
  2. Localiza campo By.ID, "txtPesquisa"
  3. Preenche com e-mail
  4. Envia Keys.RETURN
  5. Aguarda resultado
  6. Extrai canal via XPath: (//table//tr[1]/td)[5]
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from automacao.browser import criar_driver

URL_CANAL = "http://atendews.cemig.ad.corp/PesquisaUsuario"
WAIT_TIMEOUT = 20


def consultar_canal_acesso(email: str) -> dict:
    logs: list[str] = []
    etapa = "inicializacao"
    url_final = URL_CANAL
    driver = None

    try:
        # ── 1. Criar driver ──────────────────────────────────
        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        logs.append("✓ Driver criado.")

        # ── 2. Acessar página ────────────────────────────────
        etapa = "acessar_pagina"
        logs.append(f"Acessando {URL_CANAL}")
        try:
            driver.set_page_load_timeout(20)
            driver.get(URL_CANAL)
        except WebDriverException as e:
            err_msg = str(e)[:200]
            if "ERR_NAME_NOT_RESOLVED" in err_msg or "net::ERR" in err_msg:
                logs.append(f"⛔ URL não acessível: {err_msg}")
                return _erro(
                    email,
                    f"URL do Canal de Acesso não acessível ({URL_CANAL}). "
                    "Verifique se está na rede corporativa CEMIG.",
                    etapa, url_final, logs,
                )
            raise

        url_final = driver.current_url
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título: {driver.title}")

        # ── 3. Validar página ────────────────────────────────
        etapa = "validar_pagina"
        snippet = driver.page_source[:2000].lower()
        bloqueios = ["403 forbidden", "access denied", "blocked", "not found"]
        for termo in bloqueios:
            if termo in snippet or termo in url_final.lower():
                logs.append(f"⛔ Bloqueio: '{termo}'")
                return _erro(email, f"Página bloqueada ({termo}). URL: {url_final}", etapa, url_final, logs)
        logs.append("✓ Página carregada.")

        # ── 4. Localizar campo txtPesquisa ───────────────────
        etapa = "localizar_campo"
        logs.append("Aguardando campo (By.ID, 'txtPesquisa')...")
        campo = wait.until(EC.presence_of_element_located((By.ID, "txtPesquisa")))
        logs.append("✓ Campo txtPesquisa encontrado.")

        # ── 5. Preencher e-mail e enviar ─────────────────────
        etapa = "preencher_email"
        campo.clear()
        campo.send_keys(email)
        time.sleep(0.3)
        logs.append(f"✓ E-mail preenchido: {email}")

        campo.send_keys(Keys.RETURN)
        logs.append("✓ Keys.RETURN enviado.")

        # ── 6. Aguardar resultado ────────────────────────────
        etapa = "aguardar_resultado"
        logs.append("Aguardando resultado (tabela)...")
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//table//tr[1]/td")))
            logs.append("✓ Tabela de resultado encontrada.")
        except TimeoutException:
            logs.append("Timeout aguardando tabela de resultado.")
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:800]
                logs.append(f"Texto da página: {body_text}")
            except Exception:
                pass
            return _erro(email, "Timeout aguardando resultado.", etapa, url_final, logs)

        time.sleep(0.5)

        # ── 7. Extrair canal via XPath ───────────────────────
        etapa = "extrair_dados"
        url_final = driver.current_url
        try:
            celula_canal = driver.find_element(By.XPATH, "(//table//tr[1]/td)[5]")
            canal = celula_canal.text.strip()
            logs.append(f"✓ Canal extraído: {canal}")
        except NoSuchElementException:
            logs.append("✗ Célula (//table//tr[1]/td)[5] não encontrada.")
            try:
                html_tabela = driver.find_element(By.TAG_NAME, "table").get_attribute("outerHTML")[:1500]
                logs.append(f"HTML parcial da tabela: {html_tabela}")
            except Exception:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:800]
                logs.append(f"Texto da página: {body_text}")
            return _erro(email, "Célula do canal não encontrada na tabela.", etapa, url_final, logs)

        if not canal:
            return _nao_encontrado(email, "Canal vazio na célula extraída.", etapa, url_final, logs)

        logs.append("✓ Consulta concluída com sucesso.")
        return {
            "email": email, "canal": canal,
            "status": "sucesso", "error_message": "",
            "etapa": "concluido", "url_acessada": url_final, "logs": logs,
        }

    except TimeoutException as e:
        logs.append(f"TimeoutException na etapa '{etapa}': {str(e)[:300]}")
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text[:800] if driver else ""
            logs.append(f"Texto da página: {body_text}")
        except Exception:
            pass
        return _erro(email, f"Timeout na etapa '{etapa}'.", etapa, url_final, logs)
    except WebDriverException as e:
        logs.append(f"WebDriverException: {str(e)[:300]}")
        return _erro(email, f"Erro no navegador: {str(e)[:200]}", etapa, url_final, logs)
    except Exception as e:
        logs.append(f"{type(e).__name__}: {str(e)[:300]}")
        return _erro(email, f"{type(e).__name__}: {str(e)[:200]}", etapa, url_final, logs)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _erro(email, msg, etapa, url, logs):
    return {
        "email": email, "canal": "",
        "status": "erro", "error_message": msg,
        "etapa": etapa, "url_acessada": url, "logs": logs,
    }


def _nao_encontrado(email, msg, etapa, url, logs):
    return {
        "email": email, "canal": "",
        "status": "nao_encontrado", "error_message": msg,
        "etapa": etapa, "url_acessada": url, "logs": logs,
    }
