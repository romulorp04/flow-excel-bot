"""
Automação real de consulta ao CREA-MG via Selenium.

URL: https://crea-mg.sitac.com.br/app/view/sight/externo.php?form=PesquisarProfissionalEmpresa

Fluxo:
  1. Acessa a página de pesquisa
  2. Preenche o campo CPF
  3. Clica em "Pesquisar"
  4. Aguarda a tabela de resultados
  5. Extrai Nome, Situação e Título
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

URL_CREA = "https://crea-mg.sitac.com.br/app/view/sight/externo.php?form=PesquisarProfissionalEmpresa"

# Seletores CSS dos elementos da página
SELETOR_CAMPO_CPF = "#CPF"
SELETOR_BTN_PESQUISAR = "#PESQUISAR"
SELETOR_TABELA_RESULTADO = "table.resultado, table.grid, table.tabela, #resultado table, .resultado-pesquisa table"
SELETOR_MSG_NAO_ENCONTRADO = ".mensagem, .aviso, .alert, .nao-encontrado"


def consultar_crea_mg(cpf: str) -> dict:
    """
    Executa a consulta real no site do CREA-MG para o CPF informado.
    Retorna dict com nome_crea, situacao_crea, titulo_crea, status, logs etc.
    """
    logs: list[str] = []
    etapa = "inicializacao"
    url_acessada = URL_CREA
    driver = None

    try:
        # --- Etapa 1: Criar driver ---
        etapa = "criar_driver"
        logs.append("Criando instância do Chrome (headless)...")
        driver = criar_driver(headless=True)
        logs.append("Driver criado com sucesso.")

        # --- Etapa 2: Acessar página ---
        etapa = "acessar_pagina"
        logs.append(f"Acessando URL: {URL_CREA}")
        driver.get(URL_CREA)
        url_acessada = driver.current_url
        logs.append(f"Página carregada. URL atual: {url_acessada}")

        # Verificar se a página carregou (aguardar campo CPF)
        etapa = "aguardar_campo_cpf"
        logs.append(f"Aguardando campo CPF ({SELETOR_CAMPO_CPF})...")
        try:
            campo_cpf = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, SELETOR_CAMPO_CPF))
            )
            logs.append("Campo CPF encontrado.")
        except TimeoutException:
            # Tentar seletores alternativos
            logs.append(f"Seletor {SELETOR_CAMPO_CPF} não encontrado. Tentando alternativas...")
            seletores_alt = [
                "input[name='CPF']",
                "input[name='cpf']",
                "input[placeholder*='CPF']",
                "input[type='text']",
            ]
            campo_cpf = None
            for sel in seletores_alt:
                try:
                    campo_cpf = driver.find_element(By.CSS_SELECTOR, sel)
                    logs.append(f"Campo encontrado com seletor alternativo: {sel}")
                    break
                except NoSuchElementException:
                    continue

            if campo_cpf is None:
                logs.append("ERRO: Nenhum campo CPF encontrado na página.")
                logs.append(f"Título da página: {driver.title}")
                logs.append(f"HTML parcial: {driver.page_source[:500]}")
                return _erro(cpf, "Campo CPF não encontrado na página do CREA-MG.", etapa, url_acessada, logs)

        # --- Etapa 3: Preencher CPF ---
        etapa = "preencher_cpf"
        logs.append(f"Preenchendo CPF: {cpf}")
        campo_cpf.clear()
        campo_cpf.send_keys(cpf)
        time.sleep(0.5)
        logs.append("CPF preenchido.")

        # --- Etapa 4: Clicar em Pesquisar ---
        etapa = "clicar_pesquisar"
        logs.append(f"Procurando botão Pesquisar ({SELETOR_BTN_PESQUISAR})...")
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SELETOR_BTN_PESQUISAR))
            )
            logs.append("Botão Pesquisar encontrado. Clicando...")
            btn.click()
        except TimeoutException:
            # Tentar alternativas
            logs.append("Botão #PESQUISAR não encontrado. Tentando alternativas...")
            seletores_btn = [
                "input[value='Pesquisar']",
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Pesquisar')",
                "#btnPesquisar",
            ]
            btn_encontrado = False
            for sel in seletores_btn:
                try:
                    btn = driver.find_element(By.CSS_SELECTOR, sel)
                    btn.click()
                    btn_encontrado = True
                    logs.append(f"Botão clicado com seletor alternativo: {sel}")
                    break
                except (NoSuchElementException, Exception):
                    continue

            if not btn_encontrado:
                logs.append("ERRO: Botão Pesquisar não encontrado.")
                return _erro(cpf, "Botão Pesquisar não encontrado na página.", etapa, url_acessada, logs)

        # --- Etapa 5: Aguardar resultado ---
        etapa = "aguardar_resultado"
        logs.append("Aguardando resultado da pesquisa (até 20s)...")
        time.sleep(2)  # Tempo mínimo para a página processar

        # Tentar localizar a tabela de resultados
        resultado_encontrado = False
        nome_crea = ""
        situacao_crea = ""
        titulo_crea = ""

        # Estratégia 1: Procurar tabela de resultados
        try:
            WebDriverWait(driver, 18).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "table")) > 0
                or len(d.find_elements(By.CSS_SELECTOR, ".mensagem, .aviso, .alert")) > 0
            )
            logs.append("Página respondeu após a pesquisa.")
        except TimeoutException:
            logs.append("Timeout aguardando resposta da pesquisa.")

        url_acessada = driver.current_url

        # Verificar se há mensagem de "não encontrado"
        try:
            msgs = driver.find_elements(By.CSS_SELECTOR, ".mensagem, .aviso, .alert, .nao-encontrado")
            for msg in msgs:
                txt = msg.text.strip()
                if txt:
                    logs.append(f"Mensagem na página: {txt}")
                    if "não" in txt.lower() and ("encontr" in txt.lower() or "resultado" in txt.lower()):
                        return _nao_encontrado(cpf, txt, etapa, url_acessada, logs)
        except Exception:
            pass

        # Procurar resultados em tabelas
        etapa = "extrair_dados"
        tables = driver.find_elements(By.CSS_SELECTOR, "table")
        logs.append(f"Tabelas encontradas na página: {len(tables)}")

        for idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            logs.append(f"Tabela {idx}: {len(rows)} linhas")

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_texts = [c.text.strip() for c in cells]

                # Procurar padrão: rótulo | valor
                for i, cell_text in enumerate(cell_texts):
                    lower = cell_text.lower()
                    if "nome" in lower and i + 1 < len(cell_texts) and not nome_crea:
                        nome_crea = cell_texts[i + 1]
                        logs.append(f"Nome CREA extraído: {nome_crea}")
                        resultado_encontrado = True
                    elif ("situação" in lower or "situacao" in lower) and i + 1 < len(cell_texts) and not situacao_crea:
                        situacao_crea = cell_texts[i + 1]
                        logs.append(f"Situação CREA extraída: {situacao_crea}")
                        resultado_encontrado = True
                    elif ("título" in lower or "titulo" in lower) and i + 1 < len(cell_texts) and not titulo_crea:
                        titulo_crea = cell_texts[i + 1]
                        logs.append(f"Título CREA extraído: {titulo_crea}")
                        resultado_encontrado = True

                # Também procurar em linhas da tabela como colunas diretas
                if len(cell_texts) >= 3 and not resultado_encontrado:
                    # Algumas tabelas listam: Nome | Situação | Título em colunas
                    pass

        if not resultado_encontrado:
            # Última tentativa: capturar todo o texto da página para diagnóstico
            body_text = driver.find_element(By.TAG_NAME, "body").text[:1000]
            logs.append(f"Texto da página (parcial): {body_text}")

            if cpf in body_text or any(keyword in body_text.lower() for keyword in ["profissional", "registro", "nome"]):
                logs.append("Dados parecem estar na página mas não foram extraídos pelos seletores atuais.")
                return _erro(cpf, "Dados encontrados na página mas não extraídos. Revisar seletores.", etapa, url_acessada, logs)

            return _nao_encontrado(cpf, "Nenhum resultado encontrado para o CPF informado.", etapa, url_acessada, logs)

        logs.append("Consulta concluída com sucesso.")
        return {
            "cpf": cpf,
            "nome_crea": nome_crea,
            "situacao_crea": situacao_crea,
            "titulo_crea": titulo_crea,
            "status": "sucesso",
            "error_message": "",
            "etapa": "concluido",
            "url_acessada": url_acessada,
            "logs": logs,
        }

    except WebDriverException as e:
        logs.append(f"Erro WebDriver: {str(e)[:300]}")
        return _erro(cpf, f"Erro no navegador automatizado: {str(e)[:200]}", etapa, url_acessada, logs)

    except Exception as e:
        logs.append(f"Erro inesperado: {type(e).__name__}: {str(e)[:300]}")
        return _erro(cpf, f"Erro inesperado: {str(e)[:200]}", etapa, url_acessada, logs)

    finally:
        if driver:
            try:
                driver.quit()
                logs.append("Driver encerrado.")
            except Exception:
                pass


def _erro(cpf: str, msg: str, etapa: str, url: str, logs: list[str]) -> dict:
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


def _nao_encontrado(cpf: str, msg: str, etapa: str, url: str, logs: list[str]) -> dict:
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
