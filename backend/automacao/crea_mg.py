"""
Automação de consulta ao CREA-MG via Selenium.

URL: https://crea-mg.sitac.com.br/app/view/sight/externo.php?form=PesquisarProfissionalEmpresa

Fluxo:
  1. Abre URL
  2. Preenche campo CPF (By.ID, "CPF")
  3. Clica botão Pesquisar (By.ID, "PESQUISAR")
  4. Aguarda tabela de resultados (table.table_datatable)
  5. Lê primeira linha válida (tbody tr) e extrai por posição:
     - celulas[0] = nome_crea
     - celulas[1] = situacao_crea
     - celulas[2] = titulo_crea
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from automacao.browser import criar_driver

URL_CREA = (
    "https://crea-mg.sitac.com.br/app/view/sight/externo.php"
    "?form=PesquisarProfissionalEmpresa"
)

WAIT_TIMEOUT = 20


def consultar_crea_mg(cpf: str) -> dict:
    logs: list[str] = []
    etapa = "inicializacao"
    url_final = URL_CREA
    driver = None

    try:
        # ── 1. Criar driver ──────────────────────────────────
        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        logs.append("✓ Driver criado.")

        # ── 2. Abrir página ──────────────────────────────────
        etapa = "abrir_pagina"
        logs.append(f"Acessando {URL_CREA}")
        driver.get(URL_CREA)
        url_final = driver.current_url
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título: {driver.title}")

        # ── 3. Preencher CPF ─────────────────────────────────
        etapa = "preencher_cpf"
        cpf = cpf.zfill(11)
        logs.append(f"CPF normalizado: {cpf}")
        logs.append("Aguardando campo CPF (By.ID, 'CPF')...")
        campo_cpf = wait.until(EC.presence_of_element_located((By.ID, "CPF")))
        campo_cpf.clear()
        campo_cpf.send_keys(cpf)
        time.sleep(0.3)
        logs.append(f"✓ CPF preenchido: {campo_cpf.get_attribute('value')}")

        # ── 4. Clicar Pesquisar ──────────────────────────────
        etapa = "clicar_pesquisar"
        logs.append("Aguardando botão PESQUISAR (By.ID, 'PESQUISAR')...")
        btn = wait.until(EC.element_to_be_clickable((By.ID, "PESQUISAR")))
        logs.append(f"✓ Botão encontrado (<{btn.tag_name}>). Clicando...")
        try:
            btn.click()
            logs.append("✓ Click nativo executado.")
        except Exception:
            logs.append("Click nativo falhou, tentando JS...")
            driver.execute_script("arguments[0].click();", btn)
            logs.append("✓ Click via JS executado.")

        # ── 5. Aguardar tabela ───────────────────────────────
        etapa = "aguardar_tabela"
        logs.append("Aguardando tabela (table.table_datatable)...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_datatable")))
        logs.append("✓ Tabela encontrada.")
        time.sleep(1)

        # ── 6. Extrair dados ─────────────────────────────────
        etapa = "extrair_dados"
        url_final = driver.current_url
        linhas = driver.find_elements(By.CSS_SELECTOR, "table.table_datatable tbody tr")
        logs.append(f"Linhas encontradas: {len(linhas)}")

        nome = ""
        situacao = ""
        titulo = ""

        for i, linha in enumerate(linhas):
            celulas = linha.find_elements(By.TAG_NAME, "td")
            if len(celulas) >= 5:
                nome = celulas[0].text.strip()
                situacao = celulas[1].text.strip()
                titulo = celulas[2].text.strip()
                logs.append(f"✓ Linha {i}: nome={nome}, situação={situacao}, título={titulo}")
                break
            elif len(celulas) >= 3:
                nome = celulas[0].text.strip()
                situacao = celulas[1].text.strip()
                titulo = celulas[2].text.strip()
                logs.append(f"✓ Linha {i} (3 cols): nome={nome}, situação={situacao}, título={titulo}")
                break
            else:
                logs.append(f"Linha {i}: apenas {len(celulas)} célula(s), pulando.")

        if not nome and not situacao and not titulo:
            # Capturar HTML parcial para diagnóstico
            try:
                html_tabela = driver.find_element(By.CSS_SELECTOR, "table.table_datatable").get_attribute("outerHTML")[:1500]
                logs.append(f"HTML parcial da tabela: {html_tabela}")
            except Exception:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:800]
                logs.append(f"Texto da página: {body_text}")
            return _erro(cpf, "Tabela encontrada mas sem linha de dados válida.", etapa, url_final, logs)

        # Checar "não encontrado"
        if "nenhum" in nome.lower() or "não encontrad" in nome.lower():
            logs.append(f"Resultado indica não encontrado: {nome}")
            return _nao_encontrado(cpf, nome, etapa, url_final, logs)

        logs.append("✓ Consulta concluída com sucesso.")
        return {
            "cpf": cpf,
            "nome_crea": nome,
            "situacao_crea": situacao,
            "titulo_crea": titulo,
            "status": "sucesso",
            "error_message": "",
            "etapa": "concluido",
            "url_acessada": url_final,
            "logs": logs,
        }

    except TimeoutException as e:
        logs.append(f"TimeoutException na etapa '{etapa}': {str(e)[:300]}")
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text[:800] if driver else ""
            logs.append(f"Texto da página: {body_text}")
        except Exception:
            pass
        return _erro(cpf, f"Timeout na etapa '{etapa}'.", etapa, url_final, logs)
    except WebDriverException as e:
        logs.append(f"WebDriverException: {str(e)[:300]}")
        return _erro(cpf, f"Erro no navegador: {str(e)[:200]}", etapa, url_final, logs)
    except Exception as e:
        logs.append(f"{type(e).__name__}: {str(e)[:300]}")
        return _erro(cpf, f"{type(e).__name__}: {str(e)[:200]}", etapa, url_final, logs)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _erro(cpf, msg, etapa, url, logs):
    return {
        "cpf": cpf, "nome_crea": "", "situacao_crea": "", "titulo_crea": "",
        "status": "erro", "error_message": msg, "etapa": etapa,
        "url_acessada": url, "logs": logs,
    }


def _nao_encontrado(cpf, msg, etapa, url, logs):
    return {
        "cpf": cpf, "nome_crea": "", "situacao_crea": "", "titulo_crea": "",
        "status": "nao_encontrado", "error_message": msg, "etapa": etapa,
        "url_acessada": url, "logs": logs,
    }
