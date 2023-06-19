from typing import List

from concurrent.futures import ThreadPoolExecutor

from json import loads
from time import time
import re

from time import sleep


from bs4 import BeautifulSoup, ResultSet, Tag

from source.crawlers.entities.Product import Product
from source.crawlers.entities.Review import Review

from source.crawlers.scrapers.Scraper import Scraper

class AmazonScraperOld(Scraper):

    @property
    def base_url(self):
        return "https://www.amazon.it"

    def request(self, url, headers : dict = {}):
        headers = headers | {
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7'
        }

        return super().request(url, headers)

    def search(self, product: str) -> List[Product]:
        params : dict = {"k" : product}
        url : str = self.prepareSearchURL(self.base_url + "/s", params)
        pages_fetched = False
        time_wait = 0

        while not pages_fetched:
            try:
                # Secondi da aspettare
                if time_wait >= 10: raise RuntimeError("Can't scrape pages")

                req = self.request(url)
                pages = self.__fetchPages(req.text, url)
                pages_fetched = True
            except AttributeError:
                time_wait+=1
                sleep(time_wait)

        # Per ogni pagina estrapola tutti i prodotti e le raccogli in un vettore.
        products = []

        with ThreadPoolExecutor(5) as pool:
            for page in pages:
                pool.submit(self.extractFromPage, page, products)

    # Funzione che estrapola gli elementi
    def extractFromPage(self, url, products : List[Product]):
        self.logger.info(f"Inizio il fetching dei prodotti dalla pagina {url}")

        response = self.request(url)

        bs : BeautifulSoup = BeautifulSoup(response.text, "html.parser")

        product_links : ResultSet[Tag] = bs.select('[data-component-type="s-search-results"] [data-asin]:not([data-asin=""]) a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal[href*="/dp/"]')

        product_links : List[str] = [self.base_url + product.get("href").split("/ref")[0] for product in product_links]

        # Tolgo di mezzo i siti ripetuti derivata dalla ricerca del crawler
        product_links = list(dict.fromkeys(product_links))

        self.logger.info(f"Estrapolazione link completata con successo nell'url {url}.")
        self.logger.debug(f"Il numero di link estrapolati della pagina {url} sono: {len(product_links)}")
        products_list : List[Product] = []

        for product in product_links:
            with ThreadPoolExecutor(10) as pool:
                product_entity = Product.find(product)

                # Se il prodotto risulta essere stato rigenerato da meno di 15 minuti
                # (Meccanismo di cache)
                if product_entity and not product_entity.isExpired(15):
                    continue

                pool.submit(self.extractInfoProduct, product, products_list)

        products += products_list

    def __fetchPages(self, response, base_url):
        bs = BeautifulSoup(response, "html.parser")
        last_page = bs.select_one(".s-pagination-item.s-pagination-ellipsis + .s-pagination-item.s-pagination-disabled").getText()

        last_page = min(5, int(last_page)+1)

        return [f"{base_url}&page={num}" for num in range(1, last_page)]

    def extractInfoProduct(self, product_url : str, product_list : list):
        product_info = {
            "name" : ["#productTitle"],
            "price" : ["#apex_desktop span.a-price .a-offscreen", "#price"],
            "description" : ["#feature-bullets ul", "#bookDescription_feature_div"],
            "reviews_summary" : ['.AverageCustomerReviews span[data-hook="rating-out-of-text"]']
        }

        def extractData(source, key):
            bs = BeautifulSoup(source, "html.parser")

            possible_tags = product_info[key]

            foundBool = False

            for selector in possible_tags:
                product_info[key] : Tag = bs.select_one(selector)

                if product_info[key]:
                    foundBool = True
                    product_info[key] : str = product_info[key].text.strip()
                    product_info[key] = re.sub(' +', ' ', product_info[key])
                    break

                if not foundBool:
                    product_info[key] = ""

        def extractImages(source):
            bs = BeautifulSoup(source, "html.parser")

            checkScriptTag = lambda elem: 'm.media-amazon.com/images' in elem.text

            images_tag_script = list(filter(checkScriptTag, bs.select("#imageBlock_feature_div script")))

            if images_tag_script:
                images_tag_script = images_tag_script[0].text

                # Prelevo le immagini del prodotto, qualsiasi dimensione
                text = images_tag_script.split("var data = ")[1].split(";")[0].replace("'", "\"").split("\"colorImages\": ")[1].split('"colorToAsin"')[0].strip().rstrip(",")

                product_info["images"] = [img["hiRes"] for img in loads(text)["initial"] if img is not None]
            else:
                product_info["images"] = []

        def extractReviewsFromPage(source : BeautifulSoup, reviews : list):
            reviews_elems = source.select('[data-hook="review"]')

            for rev in reviews_elems:
                regex_vote = re.compile("^a-star-[1-5]$")

                vote_html_elem = rev.select_one(".a-icon-star").get("class")
                vote = list(filter(regex_vote.match, vote_html_elem))[0].split("-")[-1]

                review_dict = {
                    "text" : rev.select_one(".review-text").getText().strip().strip("\n"),
                    "vote" : int(vote),
                    "media" : [],
                    "date" : rev.select_one('[data-hook="review-date"]').getText().split(" il ")[-1].strip().strip("\n")
                }

                images =[image.get("src").replace("_SY88", "_SL1600_") for image in rev.select('.review-image-tile')]

                for image in images:
                    review_dict["media"].append(image)

                reviews.append(Review(**review_dict))

        def extractReviews():
            reviews = []

            # Sostituisco al link dp (Detail Page) con product-reviews
            reviews_url = re.sub("\/dp\/", "/product-reviews/", product_url)

            self.logger.info(f"Preparazione URL per fetching Recensioni del prodotto {product_url}")

            # Parto dal presupposto che la prima pagina di recensioni abbia almeno 1 recensione
            has_reviews = True

            # Pagina della recensione di cui fare il fetching
            page_number_rev = 1

            # Istanza seleniunm
            chrome = self.getChromeInstance()

            # Lista dei sorgenti delle pagine recensioni di cui fare il fetching
            pages : List[BeautifulSoup] = []

            # Se la pagina contiene delle recensioni, continua ad iterare [ DISCOVERY PHASE ]
            while has_reviews and page_number_rev < 5:
                url = self.prepareSearchURL(reviews_url, {"pageNumber" : page_number_rev})

                chrome.get(url)

                source = BeautifulSoup(chrome.page_source, "html.parser")
                reviews_elems = source.select('[data-hook="review"]')

                # Controllo se la pagina contiene delle recensioni
                has_reviews = len(reviews_elems) > 0

                # Se non ne contiene altre, termina e passa alla fase di fetching
                if not has_reviews: break

                self.logger.info(f"Trovata pagina con recensioni - {url}")

                # Inserisci il sorgente nella lista delle pagine
                pages.append(source)

                # Numero della pagina a cui si dovrà passare dopo
                page_number_rev+=1

            chrome.close()

            # Fetching Phase

            self.logger.info(f"Fetching delle recensioni in maniera concorrente del prodotto {product_url}")

            with ThreadPoolExecutor(5) as pool:
                for page in pages:
                    pool.submit(extractReviewsFromPage, page, reviews)

            self.logger.info(f"Fine fetching delle recensioni del prodotto {product_url}")

            product_info["reviews"] = reviews

        time_start = time()
        self.logger.info(f'Inizio fetching del prodotto: {product_url}')

        page = self.request(product_url)

        with ThreadPoolExecutor(3) as pool:
            for key in product_info.keys():
                pool.submit(extractData, page.text, key)

            pool.submit(extractImages, page.text)
            pool.submit(extractReviews)

        product_info["url"] = product_url

        product_list.append(Product(**product_info))

        self.logger.info(f'Fine fetching del prodotto in {round(time() - time_start, 2)}s : {product_url}')