import csv
import requests
from bs4 import BeautifulSoup
import sys
import hashlib
from os import path
import re
import argparse
from datetime import datetime

def scrape_web_page(url: str) -> BeautifulSoup:  
    '''
    Downloads the web page, caches it to disk (current folder), and returns a BeautifulSoup object.

    Parameters:
        url (str): The URL of the web page to scrape.

    Returns:
        BeautifulSoup: A BeautifulSoup
    '''

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

def export_to_csv(data: dict,vystup:str):
    '''
    Export data from a dictionary to a CSV file.

    Parameters:
        data (dict): Dictionary containing the data to be exported.
        output (str): Path to the output CSV file.

    Returns:
        None
    '''

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
    
def process_choice_of_municipality(soup: BeautifulSoup) ->list[dict]:

    '''
    Processes the choice of municipality from the provided BeautifulSoup object and returns a list of dictionaries containing the data.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup 

    Returns:
        list[dict]: A list of dictionaries containing the processed data for each municipality.
    '''

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

def process_municipality_with_precincts(soup: BeautifulSoup) -> dict:

    '''
    Processes a municipality with multiple precincts from the provided BeautifulSoup object and returns a dictionary containing the data.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup 

    Returns:
        dict: A dictionary containing the processed data for the municipality with multiple precincts.
    '''

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
    '''
    Processes political sides from the provided BeautifulSoup table and returns a dictionary containing the data.

    Parameters:
        table (BeautifulSoup): The BeautifulSoup 

    Returns:
        dict: A dictionary containing the processed political sides data.
    '''

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
    '''
    Processes a municipality with a single precinct from the provided BeautifulSoup object and returns a dictionary containing the data.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup

    Returns:
        dict: A dictionary containing the processed data for the municipality with a single precinct.
    '''

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
    '''
    Processes a municipality with multiple precincts from the provided BeautifulSoup object and returns a dictionary containing the data.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup 

    Returns:
        dict: A dictionary containing the processed data for the municipality with multiple precincts.
    '''

    out = dict()
    tables=soup.find_all('table')
    cells = tables[0].find_all('td')
    text=re.sub("[^0-9]","",cells[0].text)
    out['registered']=int(text)
    text=re.sub("[^0-9]","",cells[1].text)
    out['envelopes']=int(text)
    text=re.sub("[^0-9]","",cells[-2].text)
    out['valid']=int(text)
    for table in tables[1:]:
        strany=process_political_sides(table)
        out.update(strany)
    return out    

def main(url: str,vystup: str):
    '''
    Main function to process data from the provided URL and export it to a CSV file.

    Parameters:
        url (str): The URL of the web page to scrape.
        output (str): Path to the output CSV file.

    Returns:
        None
    '''
    
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




