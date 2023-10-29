from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import geopandas as gpd
import requests
from shapely.geometry import Point

estados = ["SP"]
inds = {}
gdf = gpd.read_file('shapes/br1.shp')
def simplificar_cep(cep,):
    cep = str(cep)
    cep = cep[:-3]
    cep = cep + '000'
    return cep

def simplificar_cep2(cep):
    cep = str(cep)
    cep = cep[:-2]
    cep = cep + '00'
    return cep

def cep_complete(cep):
    cep= str(cep)
    if len(cep) < 8:
        cep = '0'+cep
    return cep
coord = '#'
for estado in estados:
    print('####################################')
    print(estado)
    
    dftotal = pd.DataFrame()
    for c in range(1,6):
        df = pd.read_csv(r'cep\\'+estado+'\\'+estado.lower()+'.cepaberto_parte_'+str(c)+'.csv',names=['cep','rua','x','x1','x2','x3'])
        df['cep'] = df['cep'].astype('str')
        dftotal = pd.concat([dftotal,df])

    dftotal.dropna(subset='cep',inplace=True)
    dftotal.to_csv('cep\\'+estado+'/ceptotal.csv',index= False)
    print(len(dftotal))
    dftotal = pd.read_csv('cep\\'+estado+'/ceptotal.csv')
    dftotal['cep_simp3'] =  dftotal['cep'].apply(simplificar_cep)
    dftotal['cep_simp2'] =  dftotal['cep'].apply(simplificar_cep2)
    df1 = dftotal.drop_duplicates(subset=['cep_simp3'],keep='first')
    df2 = dftotal.drop_duplicates(subset=['cep_simp3'],keep='last')
    dftotal = pd.concat([df1,df2])
    dftotal = dftotal.drop_duplicates(subset=['cep'],keep='first')
    
    print(len(dftotal))
    dftotal.to_csv('cep\\'+estado+'/ceptotal2.csv',index= False)
    dftotal = pd.read_csv('cep\\'+estado+'/ceptotal2.csv')
    dftotal['cep'] = dftotal['cep'].apply(cep_complete)
    print('gerou csv geral')
    

    x = 1

    latitudes = []
    longitudes = []
    indices = []
    count3 = 1
    for cep in dftotal['cep']:
        try:
            delay = 2 
            max_retries = 3
            for _ in range(max_retries):
                try:
                    url = "https://cepdarua.net/cep/"+str(cep)
                    response = requests.get(url)
                    content = response.content
                    site = BeautifulSoup(content, 'html.parser')
                except :
                    print('x')
                    sleep(delay)
                    delay *= 2
            count = 1
            save = 0
            for c in site.find_all('th'):
                if c.text == 'Coordenadas:':
                    save = count
                    break
                count +=1
            count = 1
            for c in site.find_all('td'):
                if count == save:
                    coord = c.text
                    coord = coord.split(', ')
                    latitudes.append(coord[0])
                    longitudes.append(coord[1])
                count += 1
            if save == 0:
                print('xx')
                dftotal.drop(count3-1,inplace=True) 
        except:
            print('xx')
            dftotal.drop(count3-1,inplace=True)
        if count3 > x:
            print(count3)
            print(x)
            print(coord)
            print('---------')
            x = x + 50
        
        count3 += 1
    print('finalizando csv geral')
    dftotal['lat'] = latitudes
    dftotal['long'] = longitudes
    dftotal.to_csv('cep\\'+estado+'/ceptotal2.csv',index= False)
    dftotal = pd.read_csv('cep\\'+estado+'/ceptotal2.csv')

    print('criando geometrias')
    listap = []
    for c in range(0,len(dftotal)):
        listap.append(Point(dftotal['long'][c],dftotal['lat'][c]))
    dftotal['geometry'] = listap

    print('pegando intersects')
    gdfcep = gpd.GeoDataFrame(dftotal,geometry='geometry',crs='epsg:4674')
    countuf = 0
    for c in gdf['uf']:
        if c == estado:
            break
        countuf+=1
    geometria = gdf['geometry'][countuf]
    print(len(gdfcep))
    intersectados = gdfcep[gdfcep.intersects(geometria)]
    print(len(intersectados))
    print('gerando shape final')
    intersectados.to_file('cep/'+estado+'/'+estado+'.shp')

  
