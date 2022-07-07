from pandas import DataFrame            # for creating dataframes
import numpy as np                      # for arrays

from collections import Counter         # for counting elements
from datetime import datetime           #for actual date
import re                               # !!! relativní Novinka - regular expressions
from time import sleep                  # for sleeping (slowing down) inside a function
import random
import math
import pandas as pd
from selenium.webdriver.chrome.options import Options

import requests                         # for robots check
from bs4 import BeautifulSoup           # for parsing
import json                             # for Requests
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

WEBDRIVER_TYPES = ["Chrome"]

def get_soup_elements(typ_obchodu="prodej", typ_stavby="byty", pages=1):

    for webdriver_type in WEBDRIVER_TYPES:
        if webdriver_type == "Chrome":
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    #browser = webdriver.Chrome(ChromeDriverManager().install())
    ##########################################
    # 1. Volba Prodej/Pronájem, Byty/Domy,                 --Aukce/Bez Aukce (jen pro Prodeje) zatím nechávám být, cpe se mi to doprostřed url
    ##########################################

    url_x = r"https://www.sreality.cz/hledani"
    url = url_x + "/" + typ_obchodu + "/" + typ_stavby

    ##########################################
    # 2. načtení webu
    ##########################################

    browser.get(url)  # (url).text ??
    sleep(random.uniform(1.0, 1.5))
    innerHTML = browser.execute_script("return document.body.innerHTML")
    soup = BeautifulSoup(innerHTML, 'lxml')  # "parser" ??

    elements = []

    for link in soup.findAll('a', attrs={'href': re.compile(
            "^/detail/")}):  # !!!!!!!!!!!!!!!!! změněno, protože H2 neobsahovalo všechny věci, jen nadpisek.
        link = link.get('href')
        elements.append(link)
    elements = elements[0::2]

    ##########################################
    # 3. zjištění počtu listů - mělo by být optional, ale nevadí
    ##########################################
    records = soup.find_all(class_='numero ng-binding')[1].text
    records = re.split(r'\D', str(records))
    records = ",".join(records).replace(",", "")
    records = int(records)
    max_page = math.ceil(records / 20)
    print("----------------")
    print("Scrapuji: " + str(typ_obchodu) + " " + str(typ_stavby))
    print("Celkem inzerátů: " + str(records))
    print("Celkem stránek: " + str(max_page))

    ##########################################
    # 4. nastavení počtu stránek  -mělo být víc promakané
    ##########################################
    print("Scrapuji (pouze) " + str(pages) + " stran.")
    print("----------------")

    ##########################################
    # 5. Scrapping zbylých listů - naštěstí v jednom okně
    ##########################################

    for i in range(pages - 1):
        i = i + 2

        sys.stdout.write('\r' + "Strana " + str(i - 1) + " = " + str(
            round(100 * (i - 1) / (pages), 2)) + "% progress. Zbývá cca: " + str(
            round(random.uniform(3.4, 3.8) * (pages - (i - 1)),
                  2)) + " sekund.")  # Asi upravím čas, na rychlejším kabelu v obýváku je to občas i tak 3 sec :O

        url2 = url + "?strana=" + str(i)
        browser.get(url2)

        sleep(random.uniform(1.0, 1.5))

        innerHTML = browser.execute_script("return document.body.innerHTML")
        soup2 = BeautifulSoup(innerHTML, 'lxml')

        elements2 = []

        for link in soup2.findAll('a', attrs={'href': re.compile("^/detail/prodej/")}):
            link = link.get('href')
            elements2.append(link)

        elements2 = elements2[0::2]

        elements = elements + elements2  # tyto se už můžou posčítat, naštěstí, řpedtím než z nich budeme dělat elems = prvky třeba jména

    browser.quit()

    return elements


def elements_and_ids(x):
    elements = pd.DataFrame({"url": x})

    def get_id(x):
        x = x.split("/")[-1]
        return x

    elements["url_id"] = elements["url"].apply(get_id)

    len1 = len(elements)
    # Přidáno nově, v tuto chvíli odmažu duplikáty a jsem v pohodě a šetřím si čas dál.
    elements = elements.drop_duplicates(subset=["url", "url_id"], keep="first", inplace=False)
    len2 = len(elements)

    print("-- Vymazáno " + str(len1 - len2) + " záznamů kvůli duplikaci.")
    elements = elements[:200]
    return elements


def get_image_url_and_title(x):
    url = "https://www.sreality.cz/api/cs/v2/estates/" + str(x)

    response = requests.get(url)
    flat_info = json.loads(response.text, encoding='utf-8')
    # image_url = flat_info['_embedded']['images'][0]['_links']['self']['href']
    try:
        image_url = flat_info['_embedded']['images'][0]['_links']['view']['href']
    except Exception as e:
        return None

    try:
        title = flat_info['name']['value']
    except Exception as e:
        return None

    try:
        locality = flat_info['locality']['value']
    except Exception as e:
        return None

    return image_url, str(title) + "\n" + str(locality)



def get_title(x):
    url = "https://www.sreality.cz/api/cs/v2/estates/" + str(x)

    response = requests.get(url)
    flat_info = json.loads(response.text, encoding='utf-8')

