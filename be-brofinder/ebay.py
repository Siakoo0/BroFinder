from typing import List
import bs4, requests, re
from pprint import pprint

from selenium.webdriver import Chrome

from source.crawlers.entities.Product import Product
from source.crawlers.scrapers.Scraper import Scraper

from urllib.parse import urlencode

class EbayScraper(Scraper):
    @property
    def base_url(self):
        return "https://www.ebay.it/sch/i.html"
    
    def search(self, product: str) -> List[Product]:
        
        driver : Chrome = self.getChromeInstance()

        params : dict = {"_nkw" : product}
        url : str = "{}?{}".format(self.base_url, urlencode(params))
        driver.get(url)
        
        
        response = driver.page_source
        soup = bs4.BeautifulSoup(response, 'html.parser')  #questa funzione estrapola il testo della risposta ottenuta che sarà in formato html
        
        print(self._fetchPages(url, response))

        div_ads : bs4.Tag = soup.find('div', class_ = 'srp-river-results clearfix')   #ottengo il div di tutti gli annunci
        
        #------------------------------scraping nome del prodotto-------------------------

        div_name : List[bs4.Tag] = div_ads.find_all('div', class_ = 's-item__title')
        
        #utlizzo un for in cui per ogni div_nome trovo lo span tramite find
        name_ads : list = []
        list_link_name : list = []
        
        for div in div_name:
            name_prod : str = div.text.replace("Nuova inserzione", "")
            name_ads.append(name_prod.strip())
            link_name : str = div.parent.get("href")
            list_link_name.append(link_name)
            
        #---------------------------scraping prezzo del prodotto------------------------------

        div_price : bs4.Tag = div_ads.find_all('span', class_ = 's-item__price')  #ottengo il div di tutti gli annunci
        
        price_ads : list = []
        for div in div_price:
            price_prod : str = div.text.replace("EUR", "")
            price_ads.append('€' + price_prod)
            
        # ---------------------------scraping descrizione del prodotto------------------------------
        
        # for link in list_link_name:

        response = requests.get("https://www.ebay.it/itm/284257363047?hash=item422f0f2467:g:Sf4AAOSw7kpj0Ujm&amdata=enc%3AAQAIAAAAwGsdB6W0CKcXTzOeKcCYZ0xkB2rNV50Gfx2L2PWNGLwZhBt9sbM75AE6Cajo5OsqEL3U%2BSNWaoisDMW3N92QkGlOQbRNjdJcg0ZNUie9sk4xR9dHdrq5lWygAYcEJmPL688vKvbpYYhaobmkV%2FFQJx5AWLh202klpKSWqzp6zLX1MfTgHWqB%2Bhdr5T8p2bIQkoMEJVMA8yedIyR318m%2FgiJhGr0HPn7PPbc9NrJ0duktDxRrg%2BiX1ZmGRP7%2F6aZmhQ%3D%3D%7Ctkp%3ABlBMUI7ampiXYg")
        response.raise_for_status()
        
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        div_features = soup.find('div', class_ = 'ux-layout-section-module-evo')    #div contenente descrizione del prodotto
        
        
        
        child_features = div_features.find_all('div', class_ = 'ux-layout-section-evo__row')
        list_features : dict = {}

        for row in child_features:
            labels = row.find_all('div', class_ = 'ux-labels-values__labels')
            values = row.find_all('div', class_ = 'ux-labels-values__values')
            
            # Loop attraverso le coppie label-value
            for label, value in zip(labels, values):
                # Aggiungi la coppia al dizionario list_features
                if label != "Condizione":
                    list_features[label.text.strip()] = value.text.strip()
                else:
                    list_features[label.text.strip()] = value.text.split('.')[0].strip()






        list_reviews : dict = {}
        
        # for row in child_reviews:
        tags = soup.select('.tabs__cell .fdbk-container__details__info .fdbk-container__details__info__username .fb-clipped span')
        comments = soup.select('.tabs__cell .fdbk-container__details .fdbk-container__details__comment span')
        for tag in tags:
            print(tag.text.strip())
        # for comment in comments:
        #     print(comment.text)
            # for label, value in zip(labels, values):
            #     list_reviews[label.text.strip()] = value.text.strip()
            # print(list_reviews)
        
        
        # product_list = []
        # product_list.append(name_ads, price_ads, list_features)
        # print(product_list)
        
        
        
        # name = name_ads
        # price = price_ads
        # descript : dict = list_features
        # reviews = ""
        
        # products = Product(name, price, descript, reviews)
        
        # return products
    
    
    def _fetchPages(self, url : str, respose):
        bs = bs4.BeautifulSoup(respose, "html.parser")
        return [a.get("href") for a in bs.find_all('a', class_ = 'pagination__item')]

    


