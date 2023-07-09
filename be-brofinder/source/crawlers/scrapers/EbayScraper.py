from typing import List
from bs4 import BeautifulSoup, ResultSet, Tag

from concurrent.futures import ThreadPoolExecutor

from source.database.mongodb.entities.Product import Product
from source.database.mongodb.entities.Review import Review
from source.crawlers.scrapers.Scraper import Scraper 

from urllib.parse import urlencode

import re

class EbayScraper(Scraper):
    
    @property
    def base_url(self):
        return "https://www.ebay.it"
    
    def request(self, url, headers : dict = {}):
        headers = headers | {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        return super().request(url, headers)
    
    def search(self, product: str) -> List[Product]:
        
        params : dict = {"_nkw" : product}
        url : str = "{}/sch/i.html?{}".format(self.base_url, urlencode(params))
        
        response = self.request(url)
        
        pages = self._fetchPages(response, 3) #esegue il fetch di 4 pagine di prodotti

        #Array che conterra tutti i prodotti
        products = []
        
        #in ogni pagine estrapola tutti i prodotti e le reccoglie nell'array sopra dichiarato
        with ThreadPoolExecutor(5) as pool:#classe che permette di utilizzare i Thread dalla pool
            for page in pages:
                pool.submit(self.extractFromPage, page, products, product)
              

    def extractProduct(self, item):
        self.extractInfoProduct(item["url"], item["keyword"])
        self.logger.info(f"Estrazione del prodotto completata {item['url']}.")
        
    #Funzione che estrapola gli elementi
    def extractFromPage(self, url, products : List[Product], keyword):
        self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {url}")
        
        response = self.request(url) #questo url contiene la prima pagina di prodotti 
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        
        product_links : ResultSet[Tag] = soup.select('.srp-river-results .clearfix .s-item__link')
        
        product_links : List[str] = [product.get("href").split("?")[0] for product in product_links] #estrapolo tutti i link dei prodotti dalla 1° pagina alla 4°
        
        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")
        
        for product in product_links:
            with ThreadPoolExecutor(10) as pool:
                prod = Product.get(product)
                if prod and prod.isExpired(): continue
                
                pool.submit(self.extractInfoProduct, product, keyword)
            
    def extractInfoProduct(self, product_url : str, keyword):
        print(f"Inizio fetching del prodotto {product_url}")
        
        # Entro nel prodotto selezionato e comincio lo scrape delle informazioni
        page = self.request(product_url)
        
        soup = BeautifulSoup(page.text, "html.parser")
        
        #creo il dizionario che conterrà tutte le info dei determianti prodotti
        product_info = {
            "name" : ".x-item-title__mainTitle span",
            "price" : ".x-price-primary span.ux-textspans"
        }
        
        for key, selector in product_info.items(): 
            product_info[key] : Tag = soup.select_one(selector)
            
            if product_info[key]:
                product_info[key] : Tag = product_info[key].text.strip()
            else:
                product_info[key] = "Non disponibile"
            
        price = product_info["price"].split(" ")

        p = re.compile("([0-9])+\,([0-9])+")
        price = [s for s in price if p.match(s)]
        if len(price) > 0:
            product_info["price"] = float(price[0].replace(",", "."))
        else: product_info["price"] = "Non disponibile"

        #fino ad arrivare ai dettagli del prodotto, che inserisco in un array e che estrapolo uno alla volta
        descr_prod_1 = soup.select('.x-about-this-item .ux-labels-values__values .ux-labels-values__values-content')
        descr_prod = []
        
        #dopo aver preso tuttki i div per la descrizione li ispezione uno alla volta andando ad estrarre tutte le info che mi servono
        for prod in descr_prod_1:
            #ogni div conterra 1 o più span con il testo da cui dovro estrarre il valore desiderato
            prod_span = prod.select('span.ux-textspans')
            #se quel valore presente nello span è "Non disponibile" viene sostituito con una stringa vuota
            if prod.text == "Non applicabile":
               prod.text.replace('Non applicabile', '')
            #se nell'array di span, sono presenti più di 3 span si andrà prendere la terza occorrenza (quella interessata)
            elif len(prod_span) >= 3:
                prod = prod_span[2].text
                descr_prod.append(prod)
            #altrimenti si appenda nell'array finale l'unica occorrenza presente
            else:
                descr_prod.append(prod.text)
        
        #infine salvo la descrizione e l'url di quel prodotto nel dizionario
        product_info["description"] = ", ".join(descr_prod)
        product_info["url"] = product_url

        product_info["keyword"] = keyword
        

        # funzione che calcola media delle recensioni che verrà inserita in reviews_summary
        def calcola_media(valori: list):
            somma = sum(valori)
            media = somma / len(valori)
            return media
        
        div_reviews_summary = soup.select_one('#LISTING_FRAME_MODULE > div > div.d-stores-info-categories__details-container > div.d-stores-info-categories__details-category-container > div.d-stores-info-categories__details-container__detail-seller-ratings > div > div')
        if div_reviews_summary is None:
            product_info["reviews_summary"] = None
        else:
            # raccolgo i valori per effettuare la media delle recensioni
            valori: list = []
            for i in range(1, 5):
                element = soup.select_one(f'#LISTING_FRAME_MODULE > div > div.d-stores-info-categories__details-container > div.d-stores-info-categories__details-category-container > div.d-stores-info-categories__details-container__detail-seller-ratings > div > div > div > div:nth-child({i}) > span')
                if element.text == '--':
                    pass
                else:
                    valori.append(float(element.text))
            reviews_summary = calcola_media(valori)
        
            # inserisco la media calcolata nell'apposita sezione dell'array product_info
            product_info["reviews_summary"] = reviews_summary
                
        reviews: List[Review] = []

        control_review = soup.select_one('#LISTING_FRAME_MODULE > div > div.d-stores-info-categories__details-container')
        with ThreadPoolExecutor(2) as pool:
            if control_review is not None:
                pool.submit(self.extractReviews, page.text, reviews, product_info)
            else:
                product_info["reviews"] = None
            pool.submit(self.extractImages, page.text, product_info)
            
        prod = Product(**product_info)
        prod.save()

        self.logger.info(f'Fine fetching del prodotto in {product_url}')
        
    def extractReviews(self, response, reviews : list, product_info: dict):
        #ottengo la struttura html del prodotto interessato
        soup = BeautifulSoup(response, 'html.parser')

        #ottengo l'href del bottone per entrare nella pagina di tutte le reviews
        button = soup.select_one('#STORE_INFORMATION0-0-54-46-10-tabpanel-0 > div > div > a')
        
        if button is None:
            button = soup.select_one('#LISTING_FRAME_MODULE > div > div.d-stores-info-categories__details-container > div.d-stores-info-categories__details-container__tabbed-list > div > div.fdbk-detail-list__btn-container > a')

        if button is None:
            button = soup.select_one('#STORE_INFORMATION0-0-58-46-10-tabpanel-0 > div > div > a')
        
        button_href = button.get('href')
        

        button_request = self.request(button_href)
        button_response = BeautifulSoup(button_request.text, 'html.parser')
        
        #seleziono il testo di tutti i commenti
        text_reviews = button_response.select('.card__comment span')
        
        #tramite un ciclo seleziono ogni singolo commento dall'array
        i = 1
        for review in text_reviews:
            review_dict: dict = {}
            review_dict['text'] = review.text
            review_dict['vote'] = None
            review_dict['media'] = []
            date_review = button_response.select_one(f'#feedback-cards > tbody > tr:nth-child({i}) > td:nth-child(3) > div:nth-child(1) > span')
            if date_review is None:
                i += 1
                date_review = button_response.select_one(f'#feedback-cards > tbody > tr:nth-child({i}) > td:nth-child(3) > div:nth-child(1) > span')
            review_dict['date'] = date_review.text
            reviews.append(Review(**review_dict))
            i += 1

        product_info["reviews"] = reviews
            
            
    def extractImages(self, response, product_info: dict):
        #ottengo la struttura html del prodotto interessato
        soup = BeautifulSoup(response, 'html.parser')

        #seleziono tutte le immagini del prodotto considerato
        product_info["images"] = [image.get("data-src") if image.get("data-src") is not None else image.get("src") for image in soup.select('.ux-image-magnify__container img.ux-image-magnify__image--original') ]


    def _fetchPages(self, response, count: int):
        soup = BeautifulSoup(response.text, "html.parser")
        page_links = [a.get('href') for a in soup.select('.pagination__item')]
        
        if len(page_links) >= count:
            return page_links[:count] #Limita a tot. elementi
        else:
            return page_links
        
        
    def _fetchPagesReview(self, response, name_seller, id_element):
        
        #entro nella pagina dell'oggetto venduto per estrapolare alcune informazione per la creazione dell'url della risposta ajax
        soup = BeautifulSoup(response, 'html.parser')
        
        base_url = "https://www.ebay.it/fdbk/update_feedback_profile?url=username"
        seller_url = "%3D" + name_seller + f"%26filter%3Dfeedback_page%253ARECEIVED_AS_SELLER%252Cperiod%253ATWELVE_MONTHS%26q"
        element_url = "%3D" + id_element + "%26page_id"
        final_url = f"%26limit%3D25&module=modules%3DFEEDBACK_SUMMARY"
        
        #accedo tramite il bottono "Vedi tutti i feedback" nella sezione dei feedback
        button_href = soup.select_one('#STORE_INFORMATION0-0-54-46-10-tabpanel-0 > div > div > a').get('href')
        button_response = self.request(button_href)
        
        #ottengo il numero di pagine dei feedback
        button_soup = BeautifulSoup(button_response.text, 'html.parser')
        
        n_page = button_soup.select('.pagination__item')
        for i in n_page:
            print("indici delle pagine dei feedback: " + i.text.strip())
        
        #ciclo il numero di pagine dei feedback per assegnare all'url il numero di pagina corrente e allo stesso tempo aprire tutti i link necessari
        url : List[str] = []
        url = [f"{base_url}{seller_url}{element_url}%3D{number}{final_url}" for number in range(1, min(5, len(n_page))+1)]
        return url
        