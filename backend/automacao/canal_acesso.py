"""
Automação de consulta ao Canal de Acesso via Selenium.

URL interna: https://atendews.cemig.ad.corp/...
(Requer acesso à rede corporativa CEMIG)

Esta automação segue o mesmo padrão da consulta CREA-MG:
  - Logs detalhados por etapa
  - Validação de redirect/bloqueio
  - Waits explícitos
  - Mensagens de erro claras
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
)
from automacao.browser import criar_driver

# URL do sistema de Canal de Acesso (rede corporativa CEMIG)
URL_CANAL = "https://atendews.cemig.ad.corp"

# Seletores — ajustar conforme a página real do Canal de Acesso
SELETOR_CAMPO_EMAIL = "#email, input[name='email'], input[type='email']"
SELETOR_BTN_PESQUISAR = "#pesquisar, button[type='submit'], input[type='submit']"


def consultar_canal_acesso(email: str) -> dict:
    """
    Executa consulta real do Canal de Acesso para o e-mail informado.
    Retorna dict com canal, status, logs detalhados.
    
    NOTA: Esta automação requer acesso à rede corporativa (atendews.cemig.ad.corp).
    Fora da rede, retornará erro de conexão.
    """
    logs: list[str] = []
    etapa = "inicializacao"
    url_final = URL_CANAL
    driver = None

    try:
        # ── 1. Criar driver ──────────────────────────────────
        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        logs.append("✓ Driver criado.")

        # ── 2. Acessar página ────────────────────────────────
        etapa = "acessar_pagina"
        logs.append(f"URL inicial: {URL_CANAL}")
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
        titulo = driver.title or "(sem título)"
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título: {titulo}")

        # ── 3. Validar página ────────────────────────────────
        etapa = "validar_pagina"
        snippet = driver.page_source[:2000].lower()

        bloqueios = ["403 forbidden", "access denied", "blocked", "not found"]
        for termo in bloqueios:
            if termo in snippet or termo in url_final.lower():
                logs.append(f"⛔ Bloqueio: '{termo}'")
                return _erro(email, f"Página bloqueada ({termo}). URL: {url_final}", etapa, url_final, logs)

        logs.append("✓ Página carregada.")

        # ── 4. Localizar campo e-mail ────────────────────────
        etapa = "localizar_campo_email"
        logs.append("Procurando campo de e-mail...")
        campo_email = None
        for sel in SELETOR_CAMPO_EMAIL.split(", "):
            try:
                campo_email = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel.strip()))
                )
                logs.append(f"✓ Campo e-mail encontrado: {sel.strip()}")
                break
            except TimeoutException:
                continue

        if campo_email is None:
            logs.append("✗ Campo de e-mail não encontrado.")
            body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
            logs.append(f"Conteúdo da página: {body_text}")
            return _erro(email, "Campo de e-mail não encontrado na página.", etapa, url_final, logs)

        # ── 5. Preencher e-mail ──────────────────────────────
        etapa = "preencher_email"
        campo_email.clear()
        campo_email.send_keys(email)
        time.sleep(0.3)
        logs.append(f"✓ E-mail preenchido: {email}")

        # ── 6. Clicar Pesquisar ──────────────────────────────
        etapa = "clicar_pesquisar"
        logs.append("Procurando botão Pesquisar...")
        btn = None
        for sel in SELETOR_BTN_PESQUISAR.split(", "):
            try:
                btn = driver.find_element(By.CSS_SELECTOR, sel.strip())
                logs.append(f"✓ Botão encontrado: {sel.strip()}")
                break
            except NoSuchElementException:
                continue

        if btn is None:
            # XPath fallback
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(text(),'Pesquisar')] | //input[@value='Pesquisar']")
                logs.append("✓ Botão encontrado via XPath.")
            except NoSuchElementException:
                logs.append("✗ Botão Pesquisar não encontrado.")
                return _erro(email, "Botão Pesquisar não encontrado.", etapa, url_final, logs)

        try:
            btn.click()
            logs.append("✓ Click executado.")
        except Exception:
            driver.execute_script("arguments[0].click();", btn)
            logs.append("✓ Click via JS.")

        # ── 7. Aguardar resultado ────────────────────────────
        etapa = "aguardar_resultado"
        logs.append("Aguardando resultado...")
        time.sleep(3)

        # Procurar resultado — ajustar seletores conforme página real
        body_text = driver.find_element(By.TAG_NAME, "body").text.strip()
        logs.append(f"Texto pós-pesquisa: {len(body_text)} chars")

        if not body_text or len(body_text) < 10:
            return _nao_encontrado(email, "Resultado vazio.", etapa, url_final, logs)

        # ── 8. Extrair canal ─────────────────────────────────
        etapa = "extrair_dados"
        canal = ""

        # Tentar encontrar em tabelas
        tables = driver.find_elements(By.TAG_NAME, "table")
        logs.append(f"Tabelas encontradas: {len(tables)}")

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                texts = [c.text.strip() for c in cells]
                for i, txt in enumerate(texts):
                    if "canal" in txt.lower() and i + 1 < len(texts) and not canal:
                        canal = texts[i + 1]
                        logs.append(f"✓ Canal: {canal}")

        if canal:
            logs.append("✓ Consulta concluída.")
            return {
                "email": email, "canal": canal,
                "status": "sucesso", "error_message": "",
                "etapa": "concluido", "url_acessada": url_final, "logs": logs,
            }

        # Se não encontrou em tabela, tentar texto
        logs.append(f"Canal não extraído. Texto: {body_text[:500]}")
        return _nao_encontrado(email, "Canal não encontrado nos resultados.", etapa, url_final, logs)

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
