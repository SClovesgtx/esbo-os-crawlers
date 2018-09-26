# encoding:utf-8

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from time import sleep
import pandas as pd 
import re


def get(drive, xpath):
    element = WebDriverWait(drive, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath))
    )
    return element

def extrair_tabela_prefeituraSP(browser):
    html = browser.page_source
    soup = BeautifulSoup(html)
    tabela = []
    lista = []
    ids = get_id_tag_a_processos(browser)
    i = 0
    for td in soup.find_all('td')[3:-1]:
        lista.append(td.text.replace('\n', ''))
        if len(lista) == 3:
            browser.find_element_by_id(ids[i]).click()
            sleep(2)
            janela1 = browser.window_handles[0]
            janela2 = browser.window_handles[1]
            browser.switch_to_window(janela2)
            url_pdf = browser.current_url
            lista.append(url_pdf)
            browser.close()
            browser.switch_to_window(janela1)
            tabela.append(lista)
            i+=1
            lista = []

    return tabela

def incerir_conteudo_caixaPesquisa(browser, xpath, conteudo):
    browser.find_element_by_xpath(xpath).send_keys(conteudo)

def get_id_tag_a_processos(browser):
    html = browser.page_source
    soup = BeautifulSoup(html)
    r = re.compile('grdPesquisaDecisoes_ctl(\d*)_lnkPa')
    numero_recursos_id_tag = [a.get('id') for a in soup.findAll('a', {'id': r})]
    return numero_recursos_id_tag

def iniciar_google_drive(path_do_google_drive):
    prefs = {'download.default_directory' : 'home/cloves/Documentos/Crawler-Acordoes/data/pdf_acordoes'}
    webdriver.ChromeOptions().add_experimental_option('prefs', prefs)
    browser = webdriver.Chrome(path_do_google_drive)
    browser.maximize_window()  # para maximizar janela da página
    # espera implicitamente 20 segundos caso conexão falhe
    browser.implicitly_wait(20)

    return browser


def apertar_botao(browser, xpath):
    # return browser.find_element_by_xpath(xpath).click()
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    n = 0
    try:
        botao = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        browser.execute_script("arguments[0].focus();", botao)  # scrolar até achar elemento botao
        botao.click()
        return 1
    except (TimeoutException, WebDriverException) as e:
        return 0

def get_numero_paginas(browser):
    xpath = '//*[@id="dataScroller_1_table"]/tbody/tr/td[4]/span'
    element =  browser.find_element(By.XPATH, xpath).text
    if len(element.split()) >= 1:
        return int(element.split()[-1])
    else:
        return 0
def get_acordoes(soup):
    tags_tr = soup.find("table", {"class": "rich-table table_listagem"}).find('tbody').findAll('tr')
    acordoes = []
    for tr in tags_tr:
        acordoes.append(tr.find('a').text)
    return acordoes

def numero_docs_naPagina(browser):
    html = browser.page_source
    soup = BeautifulSoup(html)
    n = len(soup.find("table", {"class": "rich-table table_listagem"}).find('tbody').findAll('tr'))
    return n

def get_lista_acordes(browser):
    lista_acordoes = []
    html = browser.page_source
    soup = BeautifulSoup(html)
    n_pg = get_numero_paginas(browser)
    for n in range(n_pg):
        html = browser.page_source
        soup = BeautifulSoup(html)
        lista_acordoes += get_acordoes(soup)
        # próxima página
        apertar_botao(browser, '//*[@id="dataScroller_1_table"]/tbody/tr/td[5]/div')
        sleep(20)
    return lista_acordoes

def apertar_botao_pesquisar(browser):
    apertar_botao(browser, '//*[@id="botaoPesquisarCarf"]') 
    sleep(5)
    return browser

def pesquisar_acordao(browser, numero_acordao):
    browser.get(url_base_conselho_administrativo)
    sleep(5)
    # apertar botão de acordão
    apertar_botao(browser, '//*[@id="campo_pesquisa1"]/tbody/tr/td[2]/label/input')
    # inserir número do acordão
    browser.find_element_by_xpath('//*[@id="valor_pesquisa1"]').send_keys(numero_acordao)
    browser = apertar_botao_pesquisar(browser)
    sleep(3)

def get_meta_data_acordao(browser, numero_acordao):
    pesquisar_acordao(browser, numero_acordao)
    apertar_botao(browser, '//*[@id="tblJurisprudencia:0:numDecisao"]')
    acordao = numero_acordao
    Numero_do_Processo = browser.find_element_by_xpath('//*[@id="formAcordaos:numProcesso"]').text
    Contribuinte = browser.find_element_by_xpath('//*[@id="formAcordaos:contribuinte"]').text
    Tipo_do_Recurso =  browser.find_element_by_xpath('//*[@id="formAcordaos:tdivTipoRecurso"]/span[2]').text
    Data_da_Sessao = browser.find_element_by_xpath('//*[@id="formAcordaos:dataSessao"]').text
    Relator = browser.find_element_by_xpath('//*[@id="formAcordaos:relator"]').text
    Decisao = browser.find_element_by_xpath('//*[@id="formAcordaos:textDecisao"]').text
    Ementa = browser.find_element_by_xpath('//*[@id="formAcordaos:ementa"]').text
    dic = {"acordão":acordao,
      "Numero_do_Processo": Numero_do_Processo,
      "Contribuinte": Contribuinte,
      "Tipo_do_Recurso": Tipo_do_Recurso,
      "Data_da_Sessao": Data_da_Sessao,
      "Relator":Relator,
      "Decisao": Decisao,
      "Ementa": Ementa}
    #fazer download do anexo
    apertar_botao(browser, '//*[@id="formAcordaos:j_id60:0:imageAnexos"]')
    return dic

