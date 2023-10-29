from time import sleep
from bs4 import BeautifulSoup
import pandas as pd


estados = ["RO","RR","SC","SP","SE","TO"]
inds = {}
for estado in estados:
    print('####################################')
    print(estado)
    def simplificar_cep(cep):
        cep = str(cep)
        cep = cep[:-3]
        cep = cep + '000'
        return cep
    dftotal = pd.DataFrame()
    for c in range(1,6):
        df = pd.read_csv(r'cep\\'+estado+'\\'+estado.lower()+'.cepaberto_parte_'+str(c)+'.csv',names=['cep','rua','x','x1','x2','x3'])
        dftotal = pd.concat([dftotal,df])

    dftotal.dropna(subset='cep',inplace=True)
    dftotal.to_csv('cep\\'+estado+'/ceptotal.csv')
    print(len(dftotal))
    dftotal = pd.read_csv('cep\\'+estado+'/ceptotal.csv')
    dftotal['cep_simp'] =  dftotal['cep'].apply(simplificar_cep)
    df1 = dftotal.drop_duplicates(subset=['cep_simp'],keep='first')
    df2 = dftotal.drop_duplicates(subset=['cep_simp'],keep='last')
    dftotal = pd.concat([df1,df2])
    print(len(dftotal))


    print('gerou csv geral')
    import requests

    x = 1

    latitudes = []
    longitudes = []
    indices = []
    count3 = 1
    for cep in dftotal['cep']:
        try:
            delay = 5
            max_retries = 3
            for _ in range(max_retries):
                try:
                    url = "https://cepdarua.net/cep/"+str(cep)
                    response = requests.get(url)
                    content = response.content
                    site = BeautifulSoup(content, 'html.parser')
                
                    count = 1
                    for c in site.find_all('td'):
                        if count == 6:
                            coord = c.text
                            coord = coord.split(', ')
                            latitudes.append(coord[0])
                            longitudes.append(coord[1])
                        count += 1
                except :
                    sleep(delay)
                    delay *= 2
        except:
            indices.append(count3)
            latitudes.append('#')
            longitudes.append("#")
        if count3 > x:
            print(count3)
            print(x)
            print('---------')
            x = x * 1.5
        count3 += 1


    dfx = pd.DataFrame({'lat':latitudes,'long':longitudes})
    dfx.to_csv('cep\\'+estado+'/coord.csv')
    inds[estado] = indices

print(inds)