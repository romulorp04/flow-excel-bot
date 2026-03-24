import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from automacao.browser import criar_driver

URL_CANAL = "http://atendews.cemig.ad.corp/PesquisaUsuario"

WAIT_TIMEOUT = 20


def consultar_canal_acesso(email: str) -> dict:
    logs: list[str] = []
    etapa = "inicializacao"
    url_final = URL_CANAL
    driver = None

    try:
        etapa = "normalizar_email"
        email_limpo = str(email).strip().lower()
        logs.append(f"E-mail normalizado: {email_limpo}")

        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        logs.append("Driver criado com sucesso.")

        etapa = "abrir_pagina"
        logs.append(f"Acessando {URL_CANAL}")
        driver.get(URL_CANAL)
        url_final = driver.current_url
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título da página: {driver.title}")

        etapa = "preencher_email"
        campo_busca = wait.until(EC.presence_of_element_located((By.ID, "txtPesquisa")))
        campo_busca.clear()
        campo_busca.send_keys(email_limpo)
        logs.append("Campo txtPesquisa preenchido com sucesso.")

        etapa = "enviar_pesquisa"
        campo_busca.send_keys(Keys.RETURN)
        logs.append("Pesquisa enviada com Keys.RETURN.")

        etapa = "aguardar_resultado"
        fim = time.time() + WAIT_TIMEOUT
        canal = ""
        while time.time() < fim:
            try:
                elemento = driver.find_element(By.XPATH, "(//table//tr[1]/td)[5]")
                texto = elemento.text.strip()
                if texto:
                    canal = texto
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not canal:
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:1200]
                logs.append(f"Texto parcial da página: {body_text}")
            except Exception:
                pass
            return _erro(
                email_limpo,
                "Resultado do canal de acesso não foi encontrado no XPath esperado.",
                etapa,
                driver.current_url,
                logs,
            )

        logs.append(f"Canal extraído: {canal}")

        if canal.lower() in ["não encontrado", "nao encontrado", ""]:
            return _nao_encontrado(
                email_limpo,
                "Canal de acesso não encontrado.",
                etapa,
                driver.current_url,
                logs,
            )

        return {
            "email": email_limpo,
            "canal": canal,
            "status": "sucesso",
            "error_message": "",
            "etapa": "concluido",
            "url_acessada": driver.current_url,
            "logs": logs,
        }

    except TimeoutException as e:
        logs.append(f"TimeoutException na etapa '{etapa}': {str(e)[:300]}")
        try:
            if driver:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:1200]
                logs.append(f"Texto parcial da página: {body_text}")
        except Exception:
            pass
        return _erro(
            str(email).strip(),
            f"Timeout na etapa '{etapa}'.",
            etapa,
            driver.current_url if driver else url_final,
            logs,
        )
    except WebDriverException as e:
        logs.append(f"WebDriverException: {str(e)[:300]}")
        return _erro(
            str(email).strip(),
            f"Erro no navegador: {str(e)[:200]}",
            etapa,
            driver.current_url if driver else url_final,
            logs,
        )
    except Exception as e:
        logs.append(f"{type(e).__name__}: {str(e)[:300]}")
        return _erro(
            str(email).strip(),
            f"{type(e).__name__}: {str(e)[:200]}",
            etapa,
            driver.current_url if driver else url_final,
            logs,
        )
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _erro(email, msg, etapa, url, logs):
    return {
        "email": email,
        "canal": "",
        "status": "erro",
        "error_message": msg,
        "etapa": etapa,
        "url_acessada": url,
        "logs": logs,
    }


def _nao_encontrado(email, msg, etapa, url, logs):
    return {
        "email": email,
        "canal": "",
        "status": "nao_encontrado",
        "error_message": msg,
        "etapa": etapa,
        "url_acessada": url,
        "logs": logs,
    }
