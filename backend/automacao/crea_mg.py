"""
Automação real de consulta ao CREA-MG via Selenium.

URL: https://crea-mg.sitac.com.br/app/view/sight/externo.php?form=PesquisarProfissionalEmpresa

Página real (confirmada por inspeção do HTML):
  - Campo CPF: <input id="CPF" name="CPF" type="text">
  - Botão Pesquisar: <a id="PESQUISAR" class="cad_form_txf botao_informacao">
  - Resultado: <div id="pesquisa_result"> fica display:none até resultado carregar
  - Conteúdo resultado: <div id="Result_pesquisa">
  - Overlay loading: <div id="ajax-overlay">
  - reCAPTCHA invisível v2 presente (chave 6Lf9gp8U...)

Fluxo:
  1. Acessa URL
  2. Valida se chegou na página correta (detecta redirect/bloqueio)
  3. Localiza campo #CPF
  4. Preenche CPF
  5. Clica no <a id="PESQUISAR"> (com fallback JS click)
  6. Aguarda #pesquisa_result ficar visível
  7. Extrai dados de #Result_pesquisa
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

URL_CREA = (
    "https://crea-mg.sitac.com.br/app/view/sight/externo.php"
    "?form=PesquisarProfissionalEmpresa"
)

TERMOS_BLOQUEIO = ["updatebrowser", "blocked", "access denied", "403 forbidden"]


def consultar_crea_mg(cpf: str) -> dict:
    """Executa consulta real no CREA-MG. Retorna dict com dados + logs detalhados."""
    logs: list[str] = []
    etapa = "inicializacao"
    url_final = URL_CREA
    driver = None

    try:
        # ── 1. Criar driver ──────────────────────────────────
        etapa = "criar_driver"
        logs.append("Criando Chrome headless...")
        driver = criar_driver(headless=True)
        logs.append("✓ Driver criado.")

        # ── 2. Acessar página ────────────────────────────────
        etapa = "acessar_pagina"
        logs.append(f"URL inicial: {URL_CREA}")
        driver.get(URL_CREA)
        url_final = driver.current_url
        titulo = driver.title or "(sem título)"
        logs.append(f"URL final: {url_final}")
        logs.append(f"Título: {titulo}")

        # ── 3. Detectar redirect / bloqueio ──────────────────
        etapa = "validar_pagina"
        if url_final.split("?")[0] != URL_CREA.split("?")[0]:
            logs.append(f"⚠ REDIRECIONAMENTO: {URL_CREA} → {url_final}")

        snippet = driver.page_source[:3000].lower()
        for termo in TERMOS_BLOQUEIO:
            if termo in snippet or termo in url_final.lower():
                logs.append(f"⛔ Bloqueio detectado: '{termo}'")
                return _erro(
                    cpf,
                    f"Página bloqueada/redirecionada ({termo}). URL: {url_final}",
                    etapa, url_final, logs,
                )

        # Validar que é a página de pesquisa
        if "pesquisarprofissionalempresa" not in url_final.lower().replace(" ", ""):
            if "pesquisar" not in snippet:
                logs.append("⛔ Não é a página de pesquisa do CREA-MG.")
                body_text = driver.find_element(By.TAG_NAME, "body").text[:500]
                logs.append(f"Conteúdo: {body_text}")
                return _erro(cpf, "Página carregada não é o formulário de pesquisa.", etapa, url_final, logs)

        logs.append("✓ Página de pesquisa validada.")

        # ── 4. Localizar campo CPF ───────────────────────────
        etapa = "localizar_campo_cpf"
        logs.append("Procurando campo #CPF...")
        campo_cpf = _encontrar_elemento(
            driver, 15,
            ["#CPF", "input[name='CPF']", "input[name='cpf']"],
            logs,
        )
        if campo_cpf is None:
            logs.append(f"✗ Campo CPF não encontrado. Título: {titulo}")
            return _erro(cpf, "Campo CPF não encontrado na página.", etapa, url_final, logs)
        logs.append("✓ Campo CPF encontrado.")

        # ── 5. Preencher CPF ─────────────────────────────────
        etapa = "preencher_cpf"
        campo_cpf.clear()
        campo_cpf.send_keys(cpf)
        time.sleep(0.3)
        valor = campo_cpf.get_attribute("value") or ""
        logs.append(f"✓ CPF preenchido: {valor}")

        # ── 6. Clicar Pesquisar ──────────────────────────────
        # É um <a id="PESQUISAR" class="... botao_informacao">
        etapa = "clicar_pesquisar"
        logs.append("Procurando botão #PESQUISAR...")
        btn = _encontrar_elemento(
            driver, 10,
            ["#PESQUISAR", "a#PESQUISAR", "a.botao_informacao"],
            logs,
        )
        if btn is None:
            # Tentar XPath por texto
            try:
                btn = driver.find_element(By.XPATH, "//a[contains(text(),'Pesquisar')]")
                logs.append("✓ Botão encontrado via XPath texto.")
            except NoSuchElementException:
                logs.append("✗ Botão Pesquisar não encontrado.")
                return _erro(cpf, "Botão Pesquisar não encontrado.", etapa, url_final, logs)

        tag = btn.tag_name
        logs.append(f"✓ Botão encontrado (<{tag}>). Clicando...")

        try:
            btn.click()
            logs.append("✓ Click nativo executado.")
        except Exception:
            logs.append("Click nativo falhou. Tentando via JS...")
            driver.execute_script("arguments[0].click();", btn)
            logs.append("✓ Click via JS executado.")

        # ── 7. Aguardar resultado ────────────────────────────
        etapa = "aguardar_resultado"
        logs.append("Aguardando resultado (#pesquisa_result)...")

        # Esperar overlay sumir e resultado aparecer
        resultado_apareceu = False
        for tentativa in range(1, 4):
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: (
                        d.find_element(By.CSS_SELECTOR, "#pesquisa_result")
                        .value_of_css_property("display") != "none"
                    )
                )
                resultado_apareceu = True
                logs.append(f"✓ #pesquisa_result visível (tentativa {tentativa}).")
                break
            except TimeoutException:
                logs.append(f"Tentativa {tentativa}: #pesquisa_result ainda oculto.")
                # Verificar se overlay ainda carregando
                try:
                    overlay = driver.find_element(By.CSS_SELECTOR, "#ajax-overlay")
                    if overlay.is_displayed():
                        logs.append("Overlay 'Processando...' ativo, aguardando mais...")
                        continue
                except Exception:
                    pass
                break

        if not resultado_apareceu:
            # Checar reCAPTCHA
            try:
                errs = driver.find_elements(By.CSS_SELECTOR, ".grecaptcha-error")
                for e in errs:
                    if e.text.strip():
                        logs.append(f"⛔ reCAPTCHA erro: {e.text.strip()}")
                        return _erro(cpf, "reCAPTCHA bloqueou a consulta.", etapa, url_final, logs)
            except Exception:
                pass

            # Capturar estado da página
            body = driver.find_element(By.TAG_NAME, "body").text[:800]
            logs.append(f"Texto da página: {body}")
            return _erro(cpf, "Timeout: resultado não apareceu após pesquisa.", etapa, url_final, logs)

        url_final = driver.current_url
        time.sleep(1)  # Dar tempo para conteúdo renderizar

        # ── 8. Extrair dados ─────────────────────────────────
        etapa = "extrair_dados"
        nome = ""
        situacao = ""
        titulo_prof = ""

        try:
            result_div = driver.find_element(By.CSS_SELECTOR, "#Result_pesquisa")
            result_text = result_div.text.strip()
            logs.append(f"Conteúdo resultado: {len(result_text)} chars")
        except NoSuchElementException:
            return _erro(cpf, "Div #Result_pesquisa não encontrada.", etapa, url_final, logs)

        if not result_text:
            return _nao_encontrado(cpf, "Resultado vazio — CPF não encontrado.", etapa, url_final, logs)

        # Checar "não encontrado"
        rt_lower = result_text.lower()
        if "nenhum" in rt_lower and ("encontrad" in rt_lower or "resultado" in rt_lower):
            logs.append(f"Mensagem: {result_text[:200]}")
            return _nao_encontrado(cpf, result_text[:200], etapa, url_final, logs)

        # Extrair de tabelas / links
        tables = result_div.find_elements(By.TAG_NAME, "table")
        links = result_div.find_elements(By.TAG_NAME, "a")
        logs.append(f"Tabelas: {len(tables)}, Links: {len(links)}")

        # Se houver link para detalhe e nenhuma tabela, clicar no primeiro
        if links and not tables:
            try:
                link_text = links[0].text.strip()
                logs.append(f"Clicando no resultado: {link_text}")
                links[0].click()
                time.sleep(3)
                tables = driver.find_elements(By.TAG_NAME, "table")
                logs.append(f"Tabelas na página de detalhe: {len(tables)}")
            except Exception as e:
                logs.append(f"Erro ao clicar link: {e}")

        nome, situacao, titulo_prof = _extrair_de_tabelas(tables, logs)

        if not nome and not situacao and not titulo_prof:
            logs.append(f"Não extraído. Texto: {result_text[:500]}")
            return _erro(cpf, "Dados na página mas não extraídos. Revisar seletores.", etapa, url_final, logs)

        logs.append("✓ Consulta concluída com sucesso.")
        return {
            "cpf": cpf,
            "nome_crea": nome,
            "situacao_crea": situacao,
            "titulo_crea": titulo_prof,
            "status": "sucesso",
            "error_message": "",
            "etapa": "concluido",
            "url_acessada": url_final,
            "logs": logs,
        }

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


# ── Helpers ──────────────────────────────────────────────


def _encontrar_elemento(driver, timeout, seletores, logs):
    """Tenta encontrar elemento por lista de seletores CSS, com wait no primeiro."""
    for i, sel in enumerate(seletores):
        try:
            if i == 0:
                el = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, sel))
                )
            else:
                el = driver.find_element(By.CSS_SELECTOR, sel)
            logs.append(f"  Encontrado com: {sel}")
            return el
        except (TimeoutException, NoSuchElementException):
            continue
    return None


def _extrair_de_tabelas(tables, logs):
    """Extrai nome, situação e título de tabelas da página."""
    nome = ""
    situacao = ""
    titulo = ""

    for idx, table in enumerate(tables):
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            texts = [c.text.strip() for c in cells]

            # Padrão rótulo | valor
            for i, txt in enumerate(texts):
                low = txt.lower()
                if "nome" in low and i + 1 < len(texts) and not nome:
                    nome = texts[i + 1]
                    logs.append(f"✓ Nome: {nome}")
                elif ("situação" in low or "situacao" in low) and i + 1 < len(texts) and not situacao:
                    situacao = texts[i + 1]
                    logs.append(f"✓ Situação: {situacao}")
                elif ("título" in low or "titulo" in low) and i + 1 < len(texts) and not titulo:
                    titulo = texts[i + 1]
                    logs.append(f"✓ Título: {titulo}")

            # th + td
            ths = row.find_elements(By.TAG_NAME, "th")
            for j, th in enumerate(ths):
                th_low = th.text.strip().lower()
                if j < len(texts):
                    if "nome" in th_low and not nome:
                        nome = texts[j]
                    elif ("situação" in th_low or "situacao" in th_low) and not situacao:
                        situacao = texts[j]
                    elif ("título" in th_low or "titulo" in th_low) and not titulo:
                        titulo = texts[j]

    return nome, situacao, titulo


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
