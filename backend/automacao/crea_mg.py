import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from automacao.browser import criar_driver

SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def _screenshot(driver, nome, logs):
    try:
        path = os.path.join(SCREENSHOT_DIR, f"{nome}.png")
        driver.save_screenshot(path)
        logs.append(f"📸 Screenshot salvo: {path}")
    except Exception as e:
        logs.append(f"⚠ Falha ao salvar screenshot '{nome}': {e}")

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
        etapa = "normalizar_cpf"
        cpf_limpo = str(cpf).strip().replace(".", "").replace("-", "").replace(" ", "")
        cpf_limpo = cpf_limpo.zfill(11)
        logs.append(f"CPF normalizado: {cpf_limpo}")

        etapa = "criar_driver"
        logs.append("Criando Chrome SEM headless (depuração visual)...")
        driver = criar_driver(headless=False)
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        logs.append("Driver criado com sucesso.")

        etapa = "abrir_pagina"
        logs.append(f"Acessando {URL_CREA}")
        driver.get(URL_CREA)
        url_final = driver.current_url
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título da página: {driver.title}")
        _screenshot(driver, "01_pagina_aberta", logs)

        etapa = "preencher_cpf"
        campo_cpf = wait.until(EC.presence_of_element_located((By.ID, "CPF")))
        campo_cpf.clear()
        campo_cpf.send_keys(cpf_limpo)
        logs.append("Campo CPF preenchido com sucesso.")
        _screenshot(driver, "02_cpf_preenchido", logs)

        etapa = "clicar_pesquisar"
        botao_pesquisar = wait.until(EC.element_to_be_clickable((By.ID, "PESQUISAR")))
        try:
            botao_pesquisar.click()
            logs.append("Botão PESQUISAR clicado com click nativo.")
        except Exception:
            driver.execute_script("arguments[0].click();", botao_pesquisar)
            logs.append("Botão PESQUISAR clicado com JavaScript.")

        time.sleep(1)
        logs.append(f"URL após pesquisar: {driver.current_url}")
        logs.append(f"Título após pesquisar: {driver.title}")
        _screenshot(driver, "03_apos_pesquisar", logs)

        etapa = "aguardar_tabela"
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table_datatable")))
        logs.append("Tabela principal encontrada.")

        # Esperar a linha útil de resultado, não só a tabela vazia
        etapa = "aguardar_linhas"
        fim = time.time() + WAIT_TIMEOUT
        linhas_validas = []
        while time.time() < fim:
            linhas = driver.find_elements(By.CSS_SELECTOR, "table.table_datatable tbody tr")
            linhas_validas = []
            for linha in linhas:
                celulas = linha.find_elements(By.TAG_NAME, "td")
                textos = [c.text.strip() for c in celulas]
                if len(celulas) >= 3 and any(textos):
                    linhas_validas.append(celulas)
            if linhas_validas:
                break
            time.sleep(0.5)

        logs.append(f"Quantidade de linhas válidas encontradas: {len(linhas_validas)}")

        etapa = "extrair_dados"
        if not linhas_validas:
            try:
                html_tabela = driver.find_element(
                    By.CSS_SELECTOR, "table.table_datatable"
                ).get_attribute("outerHTML")[:2000]
                logs.append(f"HTML parcial da tabela: {html_tabela}")
            except Exception:
                pass
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:1200]
                logs.append(f"Texto parcial da página: {body_text}")
            except Exception:
                pass
            return _erro(
                cpf_limpo,
                "Tabela encontrada, mas nenhuma linha válida de resultado foi carregada.",
                etapa,
                driver.current_url,
                logs,
            )

        primeira_linha = linhas_validas[0]
        nome_crea = primeira_linha[0].text.strip() if len(primeira_linha) > 0 else ""
        situacao_crea = primeira_linha[1].text.strip() if len(primeira_linha) > 1 else ""
        titulo_crea = primeira_linha[2].text.strip() if len(primeira_linha) > 2 else ""

        logs.append(f"Nome extraído: {nome_crea}")
        logs.append(f"Situação extraída: {situacao_crea}")
        logs.append(f"Título extraído: {titulo_crea}")

        if not nome_crea and not situacao_crea and not titulo_crea:
            return _erro(
                cpf_limpo,
                "A linha de resultado foi encontrada, mas os dados vieram vazios.",
                etapa,
                driver.current_url,
                logs,
            )

        if "nenhum" in nome_crea.lower() or "não encontrad" in nome_crea.lower():
            return _nao_encontrado(
                cpf_limpo,
                nome_crea or "Nenhum registro encontrado.",
                etapa,
                driver.current_url,
                logs,
            )

        return {
            "cpf": cpf_limpo,
            "nome_crea": nome_crea,
            "situacao_crea": situacao_crea,
            "titulo_crea": titulo_crea,
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
            str(cpf).strip(),
            f"Timeout na etapa '{etapa}'.",
            etapa,
            driver.current_url if driver else url_final,
            logs,
        )
    except WebDriverException as e:
        logs.append(f"WebDriverException: {str(e)[:300]}")
        return _erro(
            str(cpf).strip(),
            f"Erro no navegador: {str(e)[:200]}",
            etapa,
            driver.current_url if driver else url_final,
            logs,
        )
    except Exception as e:
        logs.append(f"{type(e).__name__}: {str(e)[:300]}")
        return _erro(
            str(cpf).strip(),
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


def _erro(cpf, msg, etapa, url, logs):
    return {
        "cpf": cpf,
        "nome_crea": "",
        "situacao_crea": "",
        "titulo_crea": "",
        "status": "erro",
        "error_message": msg,
        "etapa": etapa,
        "url_acessada": url,
        "logs": logs,
    }


def _nao_encontrado(cpf, msg, etapa, url, logs):
    return {
        "cpf": cpf,
        "nome_crea": "",
        "situacao_crea": "",
        "titulo_crea": "",
        "status": "nao_encontrado",
        "error_message": msg,
        "etapa": etapa,
        "url_acessada": url,
        "logs": logs,
    }
