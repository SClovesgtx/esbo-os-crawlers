from bs4 import BeautifulSoup
from time import sleep
from tools import *
from selenium.common.exceptions import NoSuchElementException




URL_BASE = 'http://sagror.prefeitura.sp.gov.br/ManterDecisoes/pesquisaDecisoesCMT.aspx'
PATH_TO_GOOGLEDRIVE = "/home/cloves/Documentos/Crawler-Acordoes/chrome-driver/chromedriver_linux64/chromedriver"

def dados_PrefeituraSP(browser):
    page_count = 1
    tabela = extrair_tabela_prefeituraSP(browser)
    cond = True
    sentinela = []
    while cond:
    # Increase page_count value on each iteration on +1
        page_count += 1
    
    # Clicking on "2" on pagination on first iteration, "3" on second...
        try:
            lista = extrair_tabela_prefeituraSP(browser)
            browser.find_element_by_link_text(str(page_count)).click()
            sleep(5)
            sentinela.append(1)
            tabela += lista
        except NoSuchElementException:
            if page_count >= 10 and page_count <= 11:
                try:
                    apertar_botao(browser, '//*[@id="grdPesquisaDecisoes"]/tbody/tr[12]/td/a[10]')
                    sleep(5)
                    sentinela.append(2)
    
                except NoSuchElementException:
                    cond = False
            
                
            else:
                try:
                    apertar_botao(browser, '//*[@id="grdPesquisaDecisoes"]/tbody/tr[12]/td/a[11]')
                    sleep(5)
                    sentinela.append(3)
                except NoSuchElementException:
                    cond = False
        n = len(sentinela) - 1
        if sum(sentinela[n-1:]) >= 6:
            cond = False
         
    return tabela

def main(dic_pesquisa):
    browser = iniciar_google_drive(PATH_TO_GOOGLEDRIVE)
    browser.implicitly_wait(10)
    browser.get(URL_BASE)
    sleep(3)
    incerir_conteudo_caixaPesquisa(browser, '//*[@id="txtTodas"]', dic_pesquisa['com_todas_palavras'])
    incerir_conteudo_caixaPesquisa(browser, '//*[@id="txtExpressao"]', dic_pesquisa['Com_a_expressao'])
    # apertar botão de pesquisa
    apertar_botao(browser, '//*[@id="btnPesquisar"]')
    sleep(5)

    tabela = dados_PrefeituraSP(browser)
    df = pd.DataFrame(data = tabela, columns=['Numero_do_Recurso', 'Camara', 'Ementa', 'url_pdf'])
    df.to_csv('prefeituraSP.csv', index=False)
    browser.close()


if __name__=='__main__':

    # recebe um json como objeto de pesquisa 
    dic_pesquisa = {'com_todas_palavras': 'iss',
               'Com_a_expressao': 'exportação',
               'Com_qualquer_uma_das_palavras': None,
               'Sem_as_palavras': None,
               'Por_relator': None,
               'Por_redator_do_voto': None}

    main(dic_pesquisa)

