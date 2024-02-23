# Uživatelská příručka

Tento program slouží k získání a zpracování výsledků voleb do Poslanecké sněmovny Parlamentu České republiky konané ve dnech 20.10.- 21.10.2017. Tyto výsledky je možné získat z tohoto odkazu: https://volby.cz/pls/ps2017nss/ps3?xjazyk=CZ . Například chcete-li vidět výsledky z Územní úrovně Olomouc, použijete tento odkaz: https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101, ke kterému můžete dojít také přes prolink x na původním odkazu.


## Instalace potřebných knihoven

Aby bylo možné program spustit, je nutné si přes IDE nebo příkazový řádek nainstalovat potřebné knihovny třetích stran, které můžete najít v části requirements.txt. 

pip install requests
pip install BeautifulSoup

## Spuštění programu

Výsledný soubor budete spouštět pomocí dvou argumentů. První argument obsahuje odkaz, který územní celek chcete scrapovat (https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103), druhý argument obsahuje jméno výstupního souboru, v mém případě: vysledky_prostejov.csv

Forma spuštění je následující:
python main.py 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103' 'vysledky_prostejov.csv'

## Výstupní soubor

Výstupní soubor bude obsahovat:
1. code - číslo obce
2. location - název obce
3. registered - počet voličů
4. enveloped - počet vydaných obálek
5. valid - počet platných hlasů
6. kandidující strany včetně jejich platných hlasů

Výstupní soubor územní úrovně Olomouc taktéž naleznete v gitu.
