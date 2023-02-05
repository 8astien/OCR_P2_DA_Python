import requests
import csv
from bs4 import BeautifulSoup

# URLs
base_url = "http://books.toscrape.com/"
category = 'mystery_3'
current_page = 1
url = f"/catalogue/category/books/{category}/page-{current_page}.html"
full_page_url = base_url + url

#  GET page content
page = requests.get(full_page_url)

# CREATE BS4 OBJECT
soup = BeautifulSoup(page.content, "html.parser")

# DATA LISTS INIT
books_url = []
upcs = []
titles = []
price_including_taxes = []
price_excluding_taxes = []
number_availables = []
product_descriptions = []
categories = []
review_ratings = []
image_urls = []
book_infos = []


# EXTRACT ALL BOOKS URLS FROM A PAGE
def extract_books_url(page_url):
    print('Start Extract Books URL')
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, "html.parser")
    books_list = soup.find_all("div", class_='image_container')
    for book in books_list:
        url_raw = book.find('a')['href']
        url_clean = url_raw.removeprefix('../../../')
        full_book_url = 'http://books.toscrape.com/catalogue/' + url_clean
        books_url.append(full_book_url)


def crawl_books_in_category():
    print('Start Crawl All Books in Category')
    extract_books_url(full_page_url)
    next_page = soup.find("li", class_="next")
    if next_page:
        page = current_page + 1
        new_url = base_url + f"/catalogue/category/books/{category}/page-{page}.html"
        extract_books_url(new_url)


def extract_book_info(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

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
    image_url_clean = temp_image_url.removeprefix('../../')
    image_url = base_url + image_url_clean

    book_info = {
        "url": url,
        "upc": upc,
        "title": title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "description": description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url
    }
    return book_info


def extract_books_info(books_url):
    for url in books_url:
        book_info = extract_book_info(url)
        print(book_info)
        book_infos.append(book_info)


def write_file(book_infos, cat):
    # Enregistrer les données dans un fichier CSV
    with open(f'data/{cat}.csv', mode='w') as csv_file:
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
        for book in book_infos:
            writer.writerow({'url': book['url'],
                             'upc': book['upc'],
                             'title': book['title'],
                             'price_including_tax': book['price_including_tax'],
                             'price_excluding_tax': book['price_excluding_tax'],
                             'number_available': book['number_available'],
                             'description': book['description'],
                             'category': book['category'],
                             'review_rating': book['review_rating'],
                             'image_url': book['image_url']})


def main(books_url, book_infos):
    crawl_books_in_category()
    extract_books_info(books_url)
    write_file(book_infos, category)


main(books_url, book_infos)



