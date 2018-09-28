from bs4 import BeautifulSoup
from tools import *
from selenium.common.exceptions import NoSuchElementException
import re
from sys import argv
from time import sleep
import pandas as pd

URL_BASE = "https://www.fazenda.sp.gov.br/VDTIT/ConsultarVotos.aspx?instancia=2"
PATH_TO_GOOGLEDRIVE = "/home/cloves/Documentos/Crawler-Acordoes/chrome-driver/chromedriver_linux64/chromedriver"

def main(querys):
	browser = iniciar_google_drive(PATH_TO_GOOGLEDRIVE)
	browser.implicitly_wait(10)
	browser.get(URL_BASE)
	column_names = ["Data_da_Publicacao", "Recurso", "DRT", "Processo", "Ano", "AIIM", "Ementa", "Arquivo"]
	for query in querys:
		incerir_conteudo_caixaPesquisa(browser, '//*[@id="ctl00_ConteudoPagina_txbFiltroEmenta"]', query)
		# apertar botão de pesquisa
		apertar_botao(browser, '//*[@id="ctl00_ConteudoPagina_btnConsultar"]')
		sleep(10)
		page_count = 1
		tabela = get_table_Portal_Fazenda(browser)
		cond = True
		sentinela = []
		print("Começando a query: %s"%query)
		while cond:
		    # Increase page_count value on each iteration on +1
		    page_count += 1
		    # Clicking on "2" on pagination on first iteration, "3" on second...
		    try:
		        lista = get_table_Portal_Fazenda(browser)
		        browser.find_element_by_link_text(str(page_count)).click()
		        sleep(5)
		        sentinela.append(1)
		        tabela += lista
		        print('Getting data of page %d.'%page_count)
		        download_pdfs_fazenda(browser)
		    except NoSuchElementException:
		        if page_count >= 10 and page_count <= 11:
		            try:
		                xpath = '//*[@id="ctl00_ConteudoPagina_gdvEntidade"]/tbody/tr[9]/td/table/tbody/tr/td[11]/a'
		                apertar_botao(browser, xpath)
		                sleep(5)
		                sentinela.append(2)
		    
		            except NoSuchElementException:
		                cond = False
		            
		                
		        else:
		            try:
		                xpath = '//*[@id="ctl00_ConteudoPagina_gdvEntidade"]/tbody/tr[9]/td/table/tbody/tr/td[12]/a'
		                apertar_botao(browser, xpath)
		                sleep(5)
		                sentinela.append(3)
		            except NoSuchElementException:
		                cond = False
		    n = len(sentinela) - 1
		    if sum(sentinela[n-1:]) >= 6:
		        cond = False

		df = pd.DataFrame(data=tabela, columns=column_names)
		df.to_csv('data/'+query+'-Fazenda'+'.csv', index=False, sep=';')
		print("Terminado a query: %s\n\n"%query)

	print('FIM!')

if __name__== "__main__":
	search_query = argv[1]
	search_query = search_query.split(',')
	main(search_query)
