import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

estados = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS"]
def simplificar_cep(cep):
    cep = str(cep)
    cep = cep[:-3]
    cep = cep + '000'
    return cep
for e in estados:
    print(e)
    dftotal = pd.read_csv('cep\\'+e+'/ceptotal.csv')
    dftotal['cep_simp'] =  dftotal['cep'].apply(simplificar_cep)
    df1 = dftotal.drop_duplicates(subset=['cep_simp'],keep='first')
    df2 = dftotal.drop_duplicates(subset=['cep_simp'],keep='last')
    dftotal = pd.concat([df1,df2])

    dfcep = pd.read_csv('cep/'+e+'/coord.csv')

    dftotal['lat'] = dfcep['lat']
    dftotal['long'] = dfcep['long']
    dftotal.to_csv('cep\\'+e+'/ceptotal2.csv')
    dftotal = pd.read_csv('cep\\'+e+'/ceptotal2.csv')

    listap = []
    for c in range(0,len(dftotal)):
        listap.append(Point(dftotal['long'][c],dftotal['lat'][c]))
    dftotal['geometry'] = listap

    gdf = gpd.GeoDataFrame(dftotal,geometry='geometry',crs='epsg:4674')
    gdf.to_file('cep/'+e+'/'+e+'.shp')