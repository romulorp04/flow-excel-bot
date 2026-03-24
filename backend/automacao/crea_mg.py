"""
Automação real de consulta ao CREA-MG via Selenium.

URL: https://crea-mg.sitac.com.br/app/view/sight/externo.php?form=PesquisarProfissionalEmpresa

Fluxo:
  1. Acessa a página de pesquisa
  2. Valida se chegou na página correta (sem redirect/bloqueio)
  3. Preenche o campo CPF
  4. Clica em "Pesquisar" (é um <a> com id=PESQUISAR)
  5. Aguarda div #pesquisa_result ficar visível
  6. Extrai dados da tabela dentro de #Result_pesquisa

NOTA: A página usa reCAPTCHA invisível (v2). Em modo headless com
configurações stealth, o reCAPTCHA invisível geralmente é resolvido
automaticamente. Se começar a bloquear, será necessário integrar
um serviço de resolução de captcha.
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

# Indicadores de página de bloqueio / redirect indesejado
PAGINAS_BLOQUEIO = ["updatebrowser", "blocked", "captcha", "access denied", "403"]


def consultar_crea_mg(cpf: str) -> dict:
    """Executa consulta real no CREA-MG e retorna resultado com logs detalhados."""
    logs: list[str] = []
    etapa = "inicializacao"
    url_inicial = URL_CREA
    url_final = URL_CREA
    driver = None

    try:
        # --- Etapa 1: Criar driver ---
        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        logs.append("Driver criado.")

        # --- Etapa 2: Acessar página ---
        etapa = "acessar_pagina"
        logs.append(f"Acessando: {URL_CREA}")
        driver.get(URL_CREA)
        url_final = driver.current_url
        titulo_pagina = driver.title
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título: {titulo_pagina}")

        # --- Etapa 3: Detectar redirect / bloqueio ---
        etapa = "validar_pagina"
        if url_final != URL_CREA:
            logs.append(f"⚠ REDIRECIONAMENTO detectado: {URL_CREA} → {url_final}")

        page_lower = driver.page_source[:2000].lower()
        for termo in PAGINAS_BLOQUEIO:
            if termo in page_lower or termo in url_final.lower():
                logs.append(f"⛔ Página de bloqueio detectada ('{termo}')")
                return _erro(cpf, f"Página bloqueada/redirecionada ({termo}). URL final: {url_final}", etapa, url_final, logs)

        # Validar que é a página de pesquisa real
        if "pesquisarprofissionalempresa" not in url_final.lower().replace(" ", "") and "pesquisar" not in page_lower:
            logs.append("⚠ Página não parece ser o formulário de pesquisa do CREA-MG.")
            body_snippet = driver.find_element(By.TAG_NAME, "body").text[:500]
            logs.append(f"Conteúdo: {body_snippet}")
            return _erro(cpf, "Página carregada não é o formulário de pesquisa esperado.", etapa, url_final, logs)

        logs.append("✓ Página de pesquisa validada.")

        # --- Etapa 4: Localizar campo CPF (#CPF) ---
        etapa = "localizar_campo_cpf"
        logs.append("Procurando campo CPF (#CPF)...")
        try:
            campo_cpf = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#CPF"))
            )
            logs.append("✓ Campo #CPF encontrado.")
        except TimeoutException:
            # Alternativas
            logs.append("#CPF não encontrado. Tentando seletores alternativos...")
            campo_cpf = None
            for sel in ["input[name='CPF']", "input[name='cpf']", "input[id='CPF']"]:
                try:
                    campo_cpf = driver.find_element(By.CSS_SELECTOR, sel)
                    logs.append(f"✓ Campo CPF encontrado via: {sel}")
                    break
                except NoSuchElementException:
                    continue
            if campo_cpf is None:
                logs.append(f"✗ Nenhum campo CPF na página. Título: {titulo_pagina}")
                return _erro(cpf, "Campo CPF não encontrado na página.", etapa, url_final, logs)

        # --- Etapa 5: Preencher CPF ---
        etapa = "preencher_cpf"
        campo_cpf.clear()
        campo_cpf.send_keys(cpf)
        time.sleep(0.3)
        valor_preenchido = campo_cpf.get_attribute("value")
        logs.append(f"✓ CPF preenchido: {valor_preenchido}")

        # --- Etapa 6: Clicar em Pesquisar ---
        # O botão é um <a id="PESQUISAR" class="... botao_informacao">
        etapa = "clicar_pesquisar"
        logs.append("Procurando botão Pesquisar (#PESQUISAR)...")
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#PESQUISAR"))
            )
            tag_name = btn.tag_name
            logs.append(f"✓ Botão encontrado (<{tag_name}> id=PESQUISAR). Clicando...")
            btn.click()
        except TimeoutException:
            logs.append("#PESQUISAR não clicável. Tentando alternativas...")
            clicou = False
            for sel in ["a#PESQUISAR", "a.botao_informacao", "#PESQUISAR"]:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, sel)
                    driver.execute_script("arguments[0].click();", el)
                    clicou = True
                    logs.append(f"✓ Clicado via JS: {sel}")
                    break
                except Exception:
                    continue
            if not clicou:
                # Tentar submit do form
                try:
                    driver.execute_script("document.getElementById('form').submit();")
                    clicou = True
                    logs.append("✓ Form submetido via JS.")
                except Exception:
                    pass
            if not clicou:
                return _erro(cpf, "Botão Pesquisar não encontrado/clicável.", etapa, url_final, logs)

        # --- Etapa 7: Aguardar resultado ---
        etapa = "aguardar_resultado"
        logs.append("Aguardando resultado (div #pesquisa_result)...")

        # A página mostra/esconde #pesquisa_result via display
        try:
            WebDriverWait(driver, 25).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "#pesquisa_result").value_of_css_property("display") != "none"
                or len(d.find_elements(By.CSS_SELECTOR, "#Result_pesquisa *")) > 0
            )
            logs.append("✓ Resultado apareceu na página.")
        except TimeoutException:
            # Verificar se reCAPTCHA bloqueou
            recaptcha_visible = False
            try:
                badge = driver.find_element(By.CSS_SELECTOR, ".grecaptcha-badge")
                if badge.is_displayed():
                    recaptcha_visible = True
            except Exception:
                pass

            if recaptcha_visible:
                logs.append("⛔ reCAPTCHA pode ter bloqueado a consulta.")
                return _erro(cpf, "reCAPTCHA bloqueou a consulta. Não é possível resolver automaticamente.", etapa, url_final, logs)

            # Verificar overlay de processamento
            try:
                overlay = driver.find_element(By.CSS_SELECTOR, "#ajax-overlay")
                if overlay.is_displayed():
                    logs.append("Overlay 'Processando...' ainda visível. Aguardando mais 10s...")
                    time.sleep(10)
            except Exception:
                pass

            # Verificar novamente
            try:
                result_div = driver.find_element(By.CSS_SELECTOR, "#Result_pesquisa")
                if result_div.text.strip():
                    logs.append("✓ Resultado encontrado após espera extra.")
                else:
                    logs.append("✗ Timeout: resultado não apareceu.")
                    body_text = driver.find_element(By.TAG_NAME, "body").text[:800]
                    logs.append(f"Texto da página: {body_text}")
                    return _erro(cpf, "Timeout aguardando resultado da pesquisa.", etapa, url_final, logs)
            except Exception:
                logs.append("✗ Div #Result_pesquisa não encontrada.")
                return _erro(cpf, "Resultado não carregou após pesquisa.", etapa, url_final, logs)

        url_final = driver.current_url

        # --- Etapa 8: Extrair dados ---
        etapa = "extrair_dados"
        nome_crea = ""
        situacao_crea = ""
        titulo_crea = ""

        # Conteúdo do resultado fica em #Result_pesquisa
        try:
            result_div = driver.find_element(By.CSS_SELECTOR, "#Result_pesquisa")
            result_html = result_div.get_attribute("innerHTML")
            result_text = result_div.text.strip()
            logs.append(f"Conteúdo do resultado ({len(result_text)} chars)")
        except NoSuchElementException:
            return _erro(cpf, "Div de resultado não encontrada.", etapa, url_final, logs)

        if not result_text:
            return _nao_encontrado(cpf, "Resultado vazio — CPF não encontrado no CREA-MG.", etapa, url_final, logs)

        # Verificar mensagem de "não encontrado"
        result_lower = result_text.lower()
        if "nenhum" in result_lower and ("encontrad" in result_lower or "resultado" in result_lower):
            logs.append(f"Mensagem de não encontrado: {result_text[:200]}")
            return _nao_encontrado(cpf, result_text[:200], etapa, url_final, logs)

        # Extrair de tabelas dentro do resultado
        tables = result_div.find_elements(By.TAG_NAME, "table")
        logs.append(f"Tabelas no resultado: {len(tables)}")

        # Também tentar links/detalhes (a página pode mostrar um link para o profissional)
        links = result_div.find_elements(By.TAG_NAME, "a")
        if links and not tables:
            logs.append(f"Links encontrados: {len(links)}")
            # Se houver link para detalhe, clicar no primeiro
            try:
                primeiro_link = links[0]
                logs.append(f"Clicando no primeiro resultado: {primeiro_link.text}")
                primeiro_link.click()
                time.sleep(3)
                # Agora extrair da página de detalhe
                tables = driver.find_elements(By.TAG_NAME, "table")
                logs.append(f"Tabelas na página de detalhe: {len(tables)}")
            except Exception as e:
                logs.append(f"Erro ao clicar link: {e}")

        for idx, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                texts = [c.text.strip() for c in cells]

                for i, txt in enumerate(texts):
                    low = txt.lower()
                    if "nome" in low and i + 1 < len(texts) and not nome_crea:
                        nome_crea = texts[i + 1]
                        logs.append(f"✓ Nome: {nome_crea}")
                    elif ("situação" in low or "situacao" in low) and i + 1 < len(texts) and not situacao_crea:
                        situacao_crea = texts[i + 1]
                        logs.append(f"✓ Situação: {situacao_crea}")
                    elif ("título" in low or "titulo" in low) and i + 1 < len(texts) and not titulo_crea:
                        titulo_crea = texts[i + 1]
                        logs.append(f"✓ Título: {titulo_crea}")

                # Tentar header (th) + td
                if not nome_crea:
                    ths = row.find_elements(By.TAG_NAME, "th")
                    for j, th in enumerate(ths):
                        th_low = th.text.strip().lower()
                        if j < len(texts):
                            if "nome" in th_low and not nome_crea:
                                nome_crea = texts[j]
                            elif ("situação" in th_low or "situacao" in th_low) and not situacao_crea:
                                situacao_crea = texts[j]
                            elif ("título" in th_low or "titulo" in th_low) and not titulo_crea:
                                titulo_crea = texts[j]

        if not nome_crea and not situacao_crea and not titulo_crea:
            # Fallback: pegar texto bruto do resultado
            logs.append(f"Dados não extraídos pelos seletores. Texto: {result_text[:500]}")
            return _erro(cpf, "Dados na página mas não extraídos. Revisar seletores.", etapa, url_final, logs)

        logs.append("✓ Consulta concluída com sucesso.")
        return {
            "cpf": cpf,
            "nome_crea": nome_crea,
            "situacao_crea": situacao_crea,
            "titulo_crea": titulo_crea,
            "status": "sucesso",
            "error_message": "",
            "etapa": "concluido",
            "url_acessada": url_final,
            "logs": logs,
        }

    except WebDriverException as e:
        logs.append(f"Erro WebDriver: {str(e)[:300]}")
        return _erro(cpf, f"Erro no navegador: {str(e)[:200]}", etapa, url_final, logs)
    except Exception as e:
        logs.append(f"Erro inesperado: {type(e).__name__}: {str(e)[:300]}")
        return _erro(cpf, f"{type(e).__name__}: {str(e)[:200]}", etapa, url_final, logs)
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def _erro(cpf: str, msg: str, etapa: str, url: str, logs: list[str]) -> dict:
    return {
        "cpf": cpf, "nome_crea": "", "situacao_crea": "", "titulo_crea": "",
        "status": "erro", "error_message": msg, "etapa": etapa,
        "url_acessada": url, "logs": logs,
    }


def _nao_encontrado(cpf: str, msg: str, etapa: str, url: str, logs: list[str]) -> dict:
    return {
        "cpf": cpf, "nome_crea": "", "situacao_crea": "", "titulo_crea": "",
        "status": "nao_encontrado", "error_message": msg, "etapa": etapa,
        "url_acessada": url, "logs": logs,
    }
