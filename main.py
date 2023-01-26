import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URLs
base_url = "http://books.toscrape.com"
url = "http://books.toscrape.com/catalogue/sharp-objects_997/index.html"

# Envoyer une requête HTTP GET pour obtenir le contenu de la page
page = requests.get(url)

# Créer un objet BeautifulSoup à partir du contenu de la page
soup = BeautifulSoup(page.content, "html.parser")

# DATA LISTS INIT
upcs = []
titles = []
price_including_taxes = []
price_excluding_taxes = []
number_availables = []
product_descriptions = []
categories = []
review_ratings = []
image_urls = []


# DATA EXTRACTION
upc = soup.find("th", string="UPC").find_next_sibling().text
title = soup.find("h1").text
price_including_tax = soup.find("th", string="Price (incl. tax)").find_next_sibling().text
price_excluding_tax = soup.find("th", string="Price (excl. tax)").find_next_sibling().text
number_available = soup.find("th", string="Availability").find_next_sibling().text
description = soup.find("div", id="product_description").find_next_sibling().text
breadcrumb = soup.find("ul", class_="breadcrumb").find_all("li")
category = breadcrumb[2].text
review_rating = soup.find("p", class_="star-rating").attrs["class"][1]
temp_image_url = soup.select_one('#product_gallery img')['src']
image_url = urljoin(base_url, temp_image_url)

print(url)
print(upc)
print(title)
print(price_including_tax)
print(price_excluding_tax)
print(number_available)
print(description)
print(category)
print(review_rating)
print(image_url)

# Enregistrer les données dans un fichier CSV
with open('data.csv', mode='w') as csv_file:
    fieldnames = ['url',
                  'upc',
                  'title',
                  'price_including_tax',
                  'price_excluding_tax',
                  'number_available',
                  'description',
                  'category',
                  'review_rating',
                  'image_url']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow({'url': url,
                     'upc': upc,
                     'title': title,
                     'price_including_tax': price_including_tax,
                     'price_excluding_tax': price_excluding_tax,
                     'number_available': number_available,
                     'description': description,
                     'category': category,
                     'review_rating': review_rating,
                     'image_url': image_url})


