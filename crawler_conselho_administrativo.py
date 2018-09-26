import pandas as pd
from tools import *
from sys import argv

PATH_TO_GOOGLE_DRIVE = "/home/cloves/Documentos/Crawler-Acordoes/chrome-driver/chromedriver_linux64/chromedriver"
url_base_conselho_administrativo = "https://carf.fazenda.gov.br/sincon/public/pages/ConsultarJurisprudencia/consultarJurisprudenciaCarf.jsf"


def Conselho_Administrativo_de_Recursos_Fiscais(search_query):
	"""
	Objetivo da função é fazer o scraping dos acordões no site
	http://idg.carf.fazenda.gov.br/

	Recebe uma lista de string(as querys de pesquisa) como parâmetro
	e retorna um csv dos meta dados e pdfs relacionados aos acordões que vieram 
	como resultado da pesquisa desta lista de querys. 
	"""
	browser = iniciar_google_drive(PATH_TO_GOOGLE_DRIVE)
	lista_acordoes = []
	for query in search_query:
		browser.get(url_base_conselho_administrativo)
		browser.find_element_by_name("valor_pesquisa3").send_keys(query) # inserir query no campo de pesquisa
		print("Pesquisando sobre: %s"%query)
		apertar_botao(browser, '//*[@id="botaoPesquisarCarf"]') # apertar botão de pesquisar
		sleep(10)
		print("Capturando os acordões.")
		lista_acordoes += get_lista_acordes(browser) # pegar número dos acordões que sairam como resultado da query
		lista_dic = []
		for acordao in lista_acordoes:
			browser.get(url_base_conselho_administrativo)
			sleep(3)
			lista_dic.append(get_meta_data_acordao(browser, acordao)) # pegando metadata de cada acordão
			print("Dados do acordão nº %s capturado!" %acordao)
		print("Meta dados de todos acordões capturados!")
		df = pd.DataFrame(lista_dic)
		nome_do_csv = '%s.csv'%query
		df.to_csv(nome_do_csv, header=True, index=False)
		print("Meta dados salvos em %s.\n\n"%nome_do_csv)

	browser.close()


if __name__== "__main__":
	search_query = argv[1]
	search_query = search_query.split(',')
	Conselho_Administrativo_de_Recursos_Fiscais(search_query)

