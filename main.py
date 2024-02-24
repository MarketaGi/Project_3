
'''
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Markéta Giňovská
email: marketa.ginovska@gmail.com
discord: MarketaGi
'''



import csv
import requests
from bs4 import BeautifulSoup
import sys
import hashlib
from os import path
import re
import argparse
from datetime import datetime

#def zpracuj_odpoved_serveru(url: str) -> BeautifulSoup:  
#    odpoved = requests.get(url)
#    return BeautifulSoup(odpoved.text, "html.parser")

def scrape_web_page(url: str) -> BeautifulSoup:  
    url_hash=hashlib.md5(url.encode('utf-8')).hexdigest()
    if not path.exists(url_hash):
        odpoved = requests.get(url)
        if not odpoved.ok:
            print(f"spatny odkaz {url}")
            exit(1)
        text=odpoved.text
        with open(url_hash,'w') as f:
            f.write(odpoved.text)
    else:
        with open(url_hash,'r') as f:
            text=f.read()    

    return BeautifulSoup(text, "html.parser")

#def scrape_web_page(url: str) -> BeautifulSoup:  
#    odpoved = requests.get(url)
#    if not odpoved.ok:
#        print(f"spatny odkaz {url}")
#        exit(1)
#    text=odpoved.text
#    return BeautifulSoup(text, "html.parser")

def find_link(soup: BeautifulSoup,okrsek) : #druhá část odkazu, která nás přenáší na stránku obce
    tables=soup.find_all('table')
    for table in tables:
        rows=table.find_all('tr')
        for row in rows[2:]:
            cells =row.find_all('td')
            location=cells[1].text
            if location!=okrsek:
                continue
            odkaz=cells[3].find('a')['href']
    nova_url ="https://volby.cz/pls/ps2017nss/" + odkaz
    return nova_url  

def export_to_csv(data,vystup):
    fieldnames=[]
    for d in data:
        for key in d.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with open(vystup, 'w', newline='', encoding='utf-8-sig') as file: #utf-8-sig - ošetřuje speciální
        writer = csv.DictWriter(file, fieldnames=fieldnames) #do souboru zapisuju klíče ze slovníku
        writer.writeheader() #hlavička souboru
        for row in data:  #jednotlivé řádky
            writer.writerow(row)
    
def process_choice_of_municipality(soup: BeautifulSoup):
    out =[]
    tables=soup.find_all('table')
    for table in tables:
        rows=table.find_all('tr')
        for row in rows[2:]:
            outrow=dict()
            cells =row.find_all('td')
            outrow['code']=cells[0].text
            outrow['location']=cells[1].text
            try:
                odkaz=cells[2].find('a')['href']
            except:
                continue
            nova_url ="https://volby.cz/pls/ps2017nss/" + odkaz
            okrsek_nebo_obec=scrape_web_page(nova_url)
            if len(okrsek_nebo_obec.find_all('table'))==1:
                # obec s vice okrsky
                vysledky = process_municipality_with_precincts(okrsek_nebo_obec)
                outrow.update(vysledky)
                out.append(outrow)
                pass
            else:
                # obec s jednim okrskem
                vysledky=process_municipality_one_precint(okrsek_nebo_obec)
                outrow.update(vysledky)
                out.append(outrow)
                pass
    return out

def process_municipality_with_precincts(soup):
    table_okrsek=soup.find_all('table')
    rows=table_okrsek[0].find_all('tr')
    outrow=dict()
    for row in rows[1:]:
        cells =row.find_all('td')
        for cell in cells:
            try:
                odkaz = cell.find('a')['href']
            except:
                continue
            nova_url ="https://volby.cz/pls/ps2017nss/" + odkaz
            soup = scrape_web_page(nova_url)
            vysledky=process_municipality_more_precints(soup)
            for key, value in vysledky.items():
                if key in outrow:
                    outrow[key]+=value
                else:
                    outrow[key]=value
    return outrow

def process_political_sides(table: BeautifulSoup) -> dict :
    out = dict()
    rows=table.find_all('tr')
    for row in rows[2:]:
        cells =row.find_all('td')
        try:
            out[cells[1].text]=int(cells[2].text)
        except:
            continue
    return out

def process_municipality_one_precint(soup: BeautifulSoup) -> dict :
    out = dict()
    tables=soup.find_all('table')
    cells = tables[0].find_all('td')
    text=re.sub("[^0-9]","",cells[3].text)
    out['registered']=int(text)
    text=re.sub("[^0-9]","",cells[4].text)
    out['envelopes']=int(text)
    text=re.sub("[^0-9]","",cells[-2].text)
    out['valid']=int(text)
    for table in tables[1:]:
        strany=process_political_sides(table)
        out.update(strany)
    return out
        
def process_municipality_more_precints(soup: BeautifulSoup) -> dict :
    out = dict()
    tables=soup.find_all('table')
    cells = tables[0].find_all('td')
    text=re.sub("[^0-9]","",cells[0].text)
    out['registered']=int(text)
    text=re.sub("[^0-9]","",cells[1].text)
    out['envelopes']=int(text)
    text=re.sub("[^0-9]","",cells[-2].text)
    out['valid']=int(text)
    out['envelopes']=int(cells[1].text)
    out['valid']=int(cells[-2].text)
    for table in tables[1:]:
        strany=process_political_sides(table)
        out.update(strany)
    return out    

def main(url: str,vystup):
 
    data = process_choice_of_municipality(scrape_web_page(url))
    export_to_csv(data,vystup)
   
if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument("uzemni_celek",help="odkaz na územní celek, např. https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103 ")
    parser.add_argument("csv_filename",help="jméno csv souboru s příponou")
    args=parser.parse_args()

    uzemni_celek=args.uzemni_celek
    vystup = args.csv_filename
   

    if not uzemni_celek.startswith('https://volby.cz/pls/ps2017nss/ps32?'):
        print(f"Zadal jsi nesprávný odkaz: {uzemni_celek}")
        exit(1)

    if not args.csv_filename.endswith('.csv'):
        print("Jméno souboru musí končit příponou '.csv'.")
        sys.exit(1)

    print(datetime.now())
    main(uzemni_celek,vystup)
    print(datetime.now())
    
#python main.py 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103' 'vysledky_prostejov.csv'  




