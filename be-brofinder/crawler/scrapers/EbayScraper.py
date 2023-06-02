import bs4, requests
from pprint import pprint

# pre_link = "https://www.ebay.it/"
link = "https://www.ebay.it/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=iphone&_sacat=0"



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
    
pprint(price_ads)


#---------------------------scraping descrizione del prodotto------------------------------

div_