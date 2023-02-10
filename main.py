import requests
import csv
from bs4 import BeautifulSoup
import os
import shutil
import re

BASE_URL = "http://books.toscrape.com/"


def get_one_book(url):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        # DATA EXTRACTION
        upc = soup.find("th", string="UPC").find_next_sibling().text
        title = soup.find("h1").text
        price_including_tax = soup.find("th", string="Price (incl. tax)").find_next_sibling().text
        price_excluding_tax = soup.find("th", string="Price (excl. tax)").find_next_sibling().text
        number_available = soup.find("th", string="Availability").find_next_sibling().text
        description_raw = soup.find("div", id="product_description")
        if description_raw:
            description = description_raw.find_next_sibling().text
        else:
            description = 'NO DESCRIPTION AVAILABLE !'
        breadcrumb = soup.find("ul", class_="breadcrumb").find_all("li")
        category = breadcrumb[2].text
        review_rating = soup.find("p", class_="star-rating").attrs["class"][1]
        temp_image_url = soup.select_one('#product_gallery img')['src']
        image_url_clean = temp_image_url.removeprefix('../../')
        image_url = BASE_URL + image_url_clean

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


def write_file(books_list, category_name):
    # Enregistrer les données dans un fichier CSV
    directory = category_name
    os.makedirs(os.path.dirname('data/'), exist_ok=True)
    path = os.path.join('data/', directory)
    os.makedirs(path)
    with open(f'data/{category_name}/0_{category_name}.csv', mode='w') as csv_file:
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
        for book in books_list:
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
            book_url = book['image_url']
            file_name_raw = re.sub('\W+','', book['title'])
            file_name = file_name_raw + '.jpg'
            download_image(book_url,
                           category_name,
                           file_name)


def download_image(img_url, category_name, file_name):
    res = requests.get(img_url, stream=True)
    if res.status_code == 200:
        with open(f'data/{category_name}/{file_name}', 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        print('Image sucessfully Downloaded: ', file_name)
    else:
        print('Image Couldn\'t be retrieved')


def get_books_url_from_single_page(category_url):
    books_url = []
    page = requests.get(category_url)
    soup = BeautifulSoup(page.content, "html.parser")
    books_list = soup.find_all("div", class_='image_container')
    for book in books_list:
        url_raw = book.find('a')['href']
        url_clean = url_raw.removeprefix('../../../')
        full_book_url = 'http://books.toscrape.com/catalogue/' + url_clean
        books_url.append(full_book_url)
    return books_url


def crawl_category_pages(url, page=1):
    # List to store all the URLs
    urls = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    next_page = soup.find("li", class_="next")
    urls.append(url)
    if next_page:
        url_raw = url.rstrip('index.html').rstrip(f'page-{page}.html')
        new_url = url_raw + f'page-{page + 1}.html'
        urls.extend(crawl_category_pages(new_url, page + 1))
    return urls


def extract_all_books_from_category(category_url):
    books_infos = []
    category_pages = crawl_category_pages(category_url)
    for page in category_pages:
        books_url = get_books_url_from_single_page(page)
        for book in books_url:
            book_details = get_one_book(book)
            print(book_details)
            books_infos.append(book_details)
    return books_infos


def get_categories():
    categories = {}
    page = requests.get(BASE_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    side_categories = soup.find("ul", class_="nav nav-list")
    list = side_categories.find_next("ul")
    links = list.find_all("a")
    for link in links:
        href = link.get("href")
        url = BASE_URL + href
        text = link.string.strip()
        categories[text] = url
    return categories


def main():
    categories = get_categories()
    for cat in categories:
        cat_name = cat
        url = categories.get(cat)
        book_infos = extract_all_books_from_category(url)
        write_file(book_infos, cat_name)


main()
