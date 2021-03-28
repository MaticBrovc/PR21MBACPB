import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv

#import sys
#!{sys.executable} -m pip install beautifulsoup4

vozila = pd.read_csv("ukrvozila.csv", sep=";")
kMesta = pd.read_csv("kraticeMesta.txt", sep=";")

vozila['znamka'].isnull().values.any() #true
vozila['tip'].isnull().values.any() #true
vozila['registrska'].isnull().values.any() #true
vozila['sasija'].isnull().values.any() #false
vozila['barva'].isnull().values.any() #true
vozila['datumodvzema'].isnull().values.any() #false

vozila['znamka'] = vozila['znamka'].fillna("")
vozila['tip'] = vozila['tip'].fillna("")
vozila['registrska'] = vozila['registrska'].fillna("")
vozila['barva'] = vozila['barva'].fillna("")

#vozila["registrska"][vozila["registrska"].str.contains("^I")]

def getWebsiteData(sasija):
    
    url="http://avtolog.si/search/"+sasija+"/"
    html_content = requests.get(url).text
    parsed_html = BeautifulSoup(html_content,'html.parser')
    
    ## Get table data
    allTables = parsed_html.find_all("div", attrs={"class": "pane"})
    
    #Take the usefull data: Podatki o vozilu; Podatki o lastniku.
    d1 = allTables[0]
    d3 = allTables[2]

    t1 = d1.findAll("table")[0]
    t_headers = []
    for th in t1.find_all("th"):
        # remove any newlines and extra spaces from left and right
        t_headers.append(th.text.replace('\n', ' ').strip())
    #print(t_headers)
    table_data = []
    for td in t1.find_all("td"):
        a = re.sub("\n +"," ", td.text.strip())
        tdt = re.sub(" +"," ", a)
        table_data.append(tdt)
    sz = [x for x in zip(t_headers, table_data)]    
    if(d3.findAll("table") != []):
        t3 = d3.findAll("table")[0]
        tds = t3.find_all("td")[-3]
        a = re.sub("\n +"," ", tds.text.strip())
        sz.append(('Status/starost',re.sub(" +"," ", a)))
    s = ("sasija", sasija)
    sz.insert(0,s)
    return sz

V0_2000 = vozila["sasija"][0:2000] #Done
V2000_4000 = vozila["sasija"][2000:4000]
V4000_6000 = vozila["sasija"][4000:6000]
V6000_8000 = vozila["sasija"][6000:8000]
V8000_10000 = vozila["sasija"][8000:10000]
V10000_12000 = vozila["sasija"][10000:12000]
V12000_14000 = vozila["sasija"][12000:14000]
V14000_16000 = vozila["sasija"][14000:16000]
V16000_konc = vozila["sasija"][16000:]


#print(len(V0_2000) + len(V2000_4000) + len(V4000_6000) + len(V6000_8000) + len(V8000_10000) + len(V10000_12000) + len(V12000_14000) + len(V14000_16000) + len(V16000_konc))

#Done: 2000 - errors
#V0_2000
def getDataFromRange(array):
    c = 0;
    dataArray = []
    errorArray = []
    for x in array:
        try:
            podatki = getWebsiteData(x)
            dataArray.append(podatki)
        except:
            errorArray.append(c)
        c+=1
    return (dataArray, errorArray)


#Zaženi na vsake nekaj časa, da ne preobremenimo strežnika.
#dataArray, errorArray = getDataFromRange(V0_2000)

#Preveri ali so podakti pravilno zapisani
#dataArray

#counter = []
#for x in dataArray:
#    counter.append(len(x))

#Preveri ali imajo vsi najmanj 12 in največ 13 vnosov.
#set(counter)

#errorArray

#vozila.iloc[1245]

def addTotxtError(array):
    file = open('napake.txt', 'a')
    for x in array:
        er = vozila["sasija"].iloc[x]
        file.write(er + "\n")
    file.close()

def firstCsv():
    with open('normal.csv', mode='a', newline='') as voz_file:
        voz_writer = csv.writer(voz_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        headers = []
        for x in dataArray[0]:
            headers.append(x[0])
        voz_writer.writerow(headers)
        voz_file.close()

def addTocsvNormal(array):
     with open('normal.csv', mode='a', newline='') as voz_file:
        voz_writer = csv.writer(voz_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for x in array:
            podatki = [y[1] for y in x]
            if len(podatki) == 12:
                podatki.append("BREZ")
            voz_writer.writerow(podatki)    
        voz_file.close()

#Ko dobiš nove podatke zapiši vse errorje v datoteko.
#addTotxtError(errorArray)

#Zaženi samo prvič, da se ustvarijo headerji
#firstCsv()

#Vsakič ko dobiš nove podatke, zaženi.
#addTocsvNormal(dataArray)