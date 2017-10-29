#Impoter moduler
import datetime
from bs4 import BeautifulSoup
import csv
import urllib.request
import simplejson
import urllib
import urllib.parse
import time
import random
import socket
import socks
import pandas as pd
import os
import traceback


def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)
def remove_scandinavian(string):
    string = string.replace('ø','oe')
    string = string.replace('Ø', 'Oe')
    string = string.replace('Å', 'AA')
    string = string.replace('å', 'aa')
    string = string.replace('æ', 'Ae')
    string = string.replace('Æ', 'Ae')
    return string

'USe Google Maps API to calculate public transport time to work'
def commute_timer(origin, destination):
        API_KEY = "AIzaSyDGJ_z-MOgXoNqzw9AIJr8G6NbbTKaBLVc"
        arrival_time = "1510646400"
        url_api = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + origin + "&destinations=" + destination + "&arrival_time=" + arrival_time + "&mode=transit" + "&key=" + API_KEY

        url_api = remove_scandinavian(url_api)
        '''Set arival time til mandag kl 08:00 en uke frem'''

        print("URL", url_api)

        result = simplejson.load(urllib.request.urlopen(url_api))
        commute_time = result['rows'][0]['elements'][0]['duration']['value']
        return commute_time;


'Google Maps Geocoding API'
def geocoding(adress):
    API_KEY = "AIzaSyDyVeOZhGDjhS0PPyJVSqSmCJYVXp0ihKM"
    url_api = "https://maps.googleapis.com/maps/api/geocode/json?address=" + adress + "&key=" + API_KEY
    geocode = simplejson.load(urllib.request.urlopen(url_api))
    latitude = geocode['results'][0]['geometry']['location']['lat']
    longitude = geocode['results'][0]['geometry']['location']['lng']
    return (latitude, longitude)


'Get Date and time'
timestr = time.strftime("%Y%m%d-%H%M%S")
print("Script startet at: ",timestr)



'Start up Tor IP (Requires Tor to be active in the background.'
ipcheck_url = 'http://checkip.amazonaws.com/'
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150)
socket.socket = socks.socksocket
print("Tor is running: The current IP is:",urllib.request.urlopen(ipcheck_url).read())

'Set page = 1'
side= 1
'Set the desired URL (Excluding New Buidlings, for Oslo Area'
theurl = "https://www.finn.no/realestate/homes/search.html?is_new_property=false&location=0.20003&location=1.20003.20046&location=1.20003.20045&location=1.20003.20043&location=1.20003.20044&location=1.20003.20050&location=1.20003.20053&location=0.20061&page=%s" %(1)
#"https://www.finn.no/realestate/homes/search.html?is_sold=false&location=0.20003&location=1.20003.20046&location=1.20003.20045&location=1.20003.20043&location=1.20003.20044&location=1.20003.20050&location=1.20003.20053&location=1.20003.20040&location=0.20007&location=1.20007.20110&location=0.20061&page="+str(side)+"&price_collective_to=5500000&property_type=3"
sider = []

print("initiating indexing pages")

'Get the total number of listing in the search'
thepage = urllib.request.urlopen(theurl)
soup = BeautifulSoup(thepage, "html.parser")
antall_treff = soup.findAll('b')[1].text
antall_treff = strip_non_ascii(antall_treff)
antall_treff = int(antall_treff)

print("-----",antall_treff)
oversikt = []

'Get the href for each listing for each page as long as #listings > 2 (always an ad as first listing'
antall_annonser = 10
side = 1
status = 1
while antall_annonser > 2:
    try:
        print("side: ", side)
        page_url = "https://www.finn.no/realestate/homes/search.html?location=0.20003&location=1.20003.20046&location=1.20003.20045&location=1.20003.20043&location=1.20003.20044&location=1.20003.20050&location=1.20003.20053&location=0.20061&page=%s" % (
        side)
        thepage = urllib.request.urlopen(page_url)
        soup = BeautifulSoup(thepage, "html.parser")
        antall_annonser = 0
        for link in soup.findAll('a'):
            linker = link.get('href')
            if "finnkode=" in linker:
                sider.append(linker)
                antall_annonser = antall_annonser +1
        side = side + 1
    except Exception:
        status = 2

tittel = []
annonsenummer = 1
'''Sett header variabelen for texten'''
header=[]
'''Set pathen til CSV'''
file_name= "C:/Users/oyvin/Desktop/Scrape/Panel_data.csv"


print("Initiating annonse:", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

'Lag DF_UT for å lagre informasjonen'

df_ut = pd.DataFrame(columns=tittel)

'For hver lagrete annonse, hent ut nøkkelinformasjon'
print(len(sider))

for annonse in sider:
    try:
        annonseurl = "https://www.finn.no" + str(annonse)
        thepage2 = urllib.request.urlopen(annonseurl)
        soup = BeautifulSoup(thepage2,"html.parser")
        tittel.append(soup.title.text.upper())

        leilighet_info = []
        hodeinfo = []
        infos = []
        tekt = []

        hodeinfo.append("TITTEL")
        leilighet_info.append(soup.title.text)
        info = soup.find_all("dd")
        tekst= soup.find_all("dt")

        '''Hente ut adressen'''
        adresse = soup.find_all("h2")
        adresse = str(adresse[2])
        adresse = adresse.replace("<h2>","")
        adresse = adresse.replace("</h2>","")
        try:
            postnummer = [x.strip() for x in adresse.split(',')]
            postnummer = postnummer[1]
        except  Exception:
            postnummer = "n.a"

        hodeinfo.append("POSTNR")
        leilighet_info.append(postnummer)
        hodeinfo.append("ADRESSE")
        leilighet_info.append(adresse)

        hodeinfo.append("URL")
        leilighet_info.append(annonseurl)

        for child in info:
            an = str(child.text)
            bn = an.replace(" ", "")
            infos.append(bn)
        for child in tekst:
            an = str(child.text)
            bn = an.replace(" ", "")
            tekt.append(bn)
        # Strippe for unødvendig tekst
        for inf in infos:
            k = strip_non_ascii(inf)
            l = k.replace(",-", "")
            m = l.replace("\n", "")
            leilighet_info.append(m)
        for inf in tekt:
            k = strip_non_ascii(inf)
            l = k.replace(",-", "")
            m = l.replace("\n", "")
            hodeinfo.append(m.upper())

        '''Hente ut matrikkelinformasjon'''
        info = soup.find("div", {"id": "matrikkelinfo"}).text
        info = "\n".join([ll.rstrip() for ll in info.splitlines() if ll.strip()])
        info = info.replace(" ", "")
        #linjer = string.split(info, '\n')
        linjer = info.splitlines()
        linjer = linjer[1:]
        for i in linjer:
            tk = [x.strip() for x in i.split(':')]
            f = tk[0].upper()
            s = tk[1]
            hodeinfo.append(f)
            leilighet_info.append(s)

        'Legg til datostempling'
        hodeinfo.append("DATOSTEMPEL")
        leilighet_info.append(time.strftime("%d/%m/%Y"))

        'Change adresse to google api format'
        adresse = adresse.replace(" ", "+")
        adresse = adresse.replace(",", "+")
        adresse = adresse.replace("++","+")
        adresse = remove_scandinavian(adresse)
        'Set adresse = origin and destination'
        print(adresse)
        origin = adresse
        destination = "Karl+Johans+gate+27+0159+Oslo"

        'try to calculate drivetime'
        try:
            times = commute_timer(origin, destination)
            leilighet_info.append(times)
        except Exception:
            leilighet_info.append("n.a")
        hodeinfo.append("Reisetid")

        '''Calculate longitude and latitude'''

        'Replace æ,ø, å'
        #adresse = remove_scandinavian(adresse)
        #adresse = strip_non_ascii(adresse)

        try:
            coordinates = geocoding(adresse)
            long = coordinates[0]
            lat = coordinates[1]
            leilighet_info.append(lat)
            leilighet_info.append(long)
        except Exception:
            long = "n.a"
            lat = "n.a"
            leilighet_info.append(lat)
            leilighet_info.append(long)
        hodeinfo.append("long")
        hodeinfo.append("lat")



        'Oppdater hodeinfo'
        for s in hodeinfo:
            if s.upper() in header:
                pass
            if s.upper() not in header:
                header.append(s.upper())
        'Legg til dictionary'
        ut_info=dict(zip(hodeinfo,leilighet_info))
        'lag unik id nøkkel med pris'
        #ID = ut_info.get('KOMMUNENR') + ut_info.get('GÅRDSNR') + ut_info.get('BRUKSNR') + ut_info.get('TOTALPRIS')
        #ut_info.update({"ID": ID})

        'Legg til leilighetsinformasjonen til data framet'
        for key in ut_info.keys():
            df_ut.loc[annonsenummer, key] = ut_info[key]

        print("Annonse nr: ", annonsenummer)

        annonsenummer = annonsenummer +1
        '''Legg til delay mellom hver request'''
        #tid = random.uniform(0.3,0.4)
        #time.sleep(tid)

    except Exception:
        print("error ",annonsenummer," ---" , annonseurl)
        tb = traceback.format_exc()
        print(tb)
        continue
'Print output til csv'
file_name_time = "C:/Users/oyvin/Desktop/Scrape/Panel_data%s.csv" %(timestr)
df_ut.to_csv(file_name_time, sep='\t')

print("Script ended at: ",datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

print("Results at: ", file_name_time)

print(len(sider))
print(annonsenummer)
