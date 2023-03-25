import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import logging

logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.INFO)



URL = 'http://www.ioerj.com.br/portal/modules/conteudoonline/busca_do.php?acao=busca'


string = """
    <option selected value="12">Parte I (Poder Executivo)</option>
    <option  value="1">Parte IA - (Ministério Público)</option>
    <option  value="2">Parte IB - (Tribunal de Contas)</option>
    <option  value="13">Parte I DPGE - (Defensoria Pública Geral do Estado)</option>
    <option  value="20">Parte I JC (Junta Comercial)</option>
    <option  value="3">Parte II (Poder Legislativo)</option>
    <option  value="6">Parte III - E (Poder Judiciário Estadual)</option>
    <option  value="7">Parte III - F (Justiça Federal)</option>
    <option  value="10">Parte III - F (Justiça do Trabalho)</option>
    <option  value="11">Parte III - F (Justiça Eleitoral)</option>
    <option  value="5">Parte IV (Municipalidades)</option>
    <option  value="4">Parte V (Publicações a Pedido)</option>
    <option  value="18">DO Campos (Poder Executivo)</option>
"""
list_jornals = []
soup = BeautifulSoup(string)
for option in soup.findAll('option'):
    list_jornals.append(option['value'])
    
list_meses = [i for i in range(1,13)]
list_anos  = [i for i in range(2018, 2019)]


def resultados_busca(busca):
    lista_resultados = []
    lista_erros = []

    for jornal in tqdm(list_jornals):
        for ano in list_anos:
            for mes in list_meses:
                logging.info(f"{jornal}, {mes}, {ano}")
                data = {
                    "textobusca"         : busca,
                    "busca[jornal]"      : jornal,
                    "datapublicacao[dia]": "",
                    "datapublicacao[mes]": mes,
                    "datapublicacao[ano]": ano,
                    "tipobusca"          : "texto",
                    "buscaordem"         : "datapublicacao desc",
                    "buscar"             : "Buscar"
                }


                response = requests.post(URL, data)
                soup = BeautifulSoup(response.content)
                soup = soup.find(id='xo-content')
                
                conteudo = soup.find('div', class_='conteudo_b')
                try:
                    pags = int(conteudo.findAll('b')[1].text.strip())
                    logging.info(f'Registros encontrados: {pags}')
                except:
                    lista_erros.append([jornal, mes, ano])
                
                soup = soup.findAll('table')[1]
                
                lista_trs = soup.findAll('tr')
                len_trs = len(lista_trs)
                for i in range(0, len_trs - 3, 3):
                    tds        = lista_trs[i].findAll('td')
                    link       = 'http://www.ioerj.com.br' + tds[0].find('a')['href']
                    titulo     = tds[1].text.strip()
                    data       = titulo.split()[0]
                    pag        = titulo.split()[2]
                    materia_id = titulo.split()[6]
                    
                    tds        = lista_trs[i + 1].findAll('td')
                    tipo       = tds[1].text.strip().replace('Tipo: ', '')
                    
                    tds        = lista_trs[i + 2].findAll('td')
                    resumo     = tds[0].text.strip()
                    
                    dict_result = {
                        'link'      : link,
                        'data'      : data,
                        'pag'       : pag,
                        'materia_id': materia_id,
                        'jornal'    : jornal,
                        'tipo'      : tipo,
                        'resumo'    : resumo,
                        'ano'       : ano,
                        'mes'       : mes
                    }
                    
                    lista_resultados.append(dict_result)
    return pd.DataFrame(lista_resultados)


df = resultados_busca('cedae')
df.to_csv('resultados.csv')

