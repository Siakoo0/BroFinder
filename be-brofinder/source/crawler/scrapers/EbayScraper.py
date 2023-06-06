import bs4, requests
from pprint import pprint
import json

# pre_link = "https://www.ebay.it/"
link = "https://www.ebay.it/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=iphone&_sacat=0"


class EbayScraper:
    def search(self, product : str):
        return []



response = requests.get(link)                           #utilizzando il metodo get della libreria requests che abbiamo precedentemente importato
                                                        #abbiamo la possibilità di ottenere il link specificato tramite una richiesta http
response.raise_for_status()                             #per verificare lo stato della risposta del browser
soup = bs4.BeautifulSoup(response.text, 'html.parser')  #questa funzione estrapola il testo della risposta ottenuta che sarà in formato html

div_ads = soup.find('div', class_ = 'srp-river-results clearfix')   #ottengo il div di tutti gli annunci

#------------------------------scraping nome del prodotto-------------------------

div_name = div_ads.find_all('div', class_ = 's-item__title')

name_ads = []

#utlizzo un for in cui per ogni div_nome trovo lo span tramite find
for div in div_name:
    span_name = div.find('span')
    name_prod = span_name.text.replace("Nuova inserzione", "")
    name_ads.append(name_prod.strip())


#---------------------------scraping prezzo del prodotto------------------------------

div_price = div_ads.find_all('span', class_ = 's-item__price')  #ottengo il div di tutti gli annunci

price_ads = []

for div in div_price:
    price_prod = div.text.replace("EUR", "")
    price_ads.append('€' + price_prod)
    
# pprint(price_ads)


#---------------------------scraping descrizione del prodotto------------------------------

under_link = "https://www.ebay.it/itm/155366227110?hash=item242c8c7ca6:g:J~8AAOSwFOpkZ0a4&amdata=enc%3AAQAIAAAA4HLqzkMLO3G%2Bdmim1YUNuBWK7jBnwrWg4GgzR7U4buy5CclvqDYw2wwEAFkYuirxMhUvIY7NoeKh%2Fx9WCgUCbzwpka0CvIj7HoAgOwLM6Z45BtAURabb%2B01lBSnRPST%2BW0dc4laI2ipuSIsTA4D4QqsX%2FDsXd2Vhx26ZvZIynHNGlINwHqmQwjhMCsBLGCwWrYr4iXfjPfRNmxw3oaakC7UfdsTcE%2FlxMHlccnv8FVtNIPp8iVPrq0wBgIK3LrjeeOJ1bxz9liKt0MxbFILdUfAwxvHBszhncZkhZcSdF39c%7Ctkp%3ABFBMkLyOz49i"

response = requests.get(under_link)

response.raise_for_status()
soup = bs4.BeautifulSoup(response.text, 'html.parser')

div_features = soup.find('div', class_ = 'ux-layout-section-module-evo')    #div contenente descrizione del prodotto

child_features = div_features.find_all('div', class_ = 'ux-layout-section-evo__row')

list_features = {}

for div in child_features:
    label = div.find('div', class_ = 'ux-labels-values__labels')
    value = div.find('div', class_ = 'ux-labels-values__values')
    list_features[label.text] = value.text


