from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from geopy.geocoders import Nominatim
import geopy.distance
from config import CONFIG
from loading import init_s3_client, upload_file
import json
import time

def get_imovirtual_properties(url):
    start_time = time.time()

    headers = CONFIG.HTTP_HEADERS
    geolocator = Nominatim(user_agent='web_scraper')
    city_centre_coordinates = geolocator.geocode(CONFIG.REAL_ESTATE_CITY)

    s3 = init_s3_client()

    # get number of pages
    url = url + '&nrAdsPerPage=72'
    try:
        html = requests.get(url, headers=headers)
        html.raise_for_status()
    except requests.HTTPError as hp:
        print(hp)
        exit(1)

    soup = BeautifulSoup(html.text, "html.parser")
    pager = soup.find('ul', attrs={"class": "pager"})
    children = pager.findChildren("a" , recursive=True)

    p = []
    for item in children:
        if len(item.text) <= 3 & len(item.text) != 0:
            # print(item)
            p.append(item.text)
    if p:
        lastPage = int(p.pop())
    else:
        lastPage = 1

    print(f"Number of pages: {lastPage}")

    # iterate pages
    for page in range(CONFIG.INITIAL_OFFSET, CONFIG.LAST_PAGE if CONFIG.LAST_PAGE else lastPage + 1):

        url_page = url + f'&page={page}'

        print(f"Fetching data from page #{page}: {url_page} ...")

        mid_time = time.time()

        articles = []

        try:
            html = requests.get(url_page, headers=headers)
            html.raise_for_status()

            soup = BeautifulSoup(html.text, "html.parser")
            class_regex = re.compile('offer-item ad_id.*')
            articles_list = soup.findAll('article', attrs={"class": class_regex})

            print(f"Found {len(articles_list)} properties on page #{page}.")

            for article_obj in articles_list:
                article = {}

                article["id"] = article_obj['data-item-id']
                article["url"] = article_obj['data-url']

                typology = article_obj.find('li', attrs={"class": re.compile(".*offer-item-rooms.*")})
                area_m2 = article_obj.find('li', attrs={"class": re.compile(".*offer-item-area.*")})
                price_per_m = article_obj.find('li', attrs={"class": re.compile(".*offer-item-price-per-m.*")})
                price = article_obj.find('li', attrs={"class": re.compile(".*offer-item-price.*")})

                article["typology"] = typology.text if typology else None
                try:
                    article["area_m2"] = float(re.sub(',', '.', area_m2.text.split(' ')[0])) if area_m2 else None
                except ValueError:
                     article["area_m2"] = None

                article["price"] = price.text.strip() if price else None
                article["price_per_meter"] = price_per_m.text if price_per_m else None

                try:
                    article["last_normalized_price"] = float(re.sub('[€ ]', '', article["price"])) if article["price"] else None
                except ValueError:
                    article["last_normalized_price"] = None

                try:
                    article["normalized_price_per_m"] = float(re.sub('[(€/m²) ]', '', article["price_per_meter"])) if article["price_per_meter"] else None
                except ValueError:
                    article["normalized_price_per_m"] = None

                article["fingerprint"] = f'{article["id"]}-{article["last_normalized_price"] if article["last_normalized_price"] else article["price"]}'

                article_details = article_obj.find('div', attrs={"class": re.compile(".*offer-item-details.*")})
                location = article_details.find('p', attrs={"class": re.compile(".*text-nowrap.*")})
                for span_tag in location.findAll('span'):
                    span_tag.replace_with('')

                article["location"] = location.text if location else None

                coordinates = geolocator.geocode(article["location"])

                if coordinates:
                    article["location_latitude"] = coordinates.latitude
                    article["location_longitude"] = coordinates.longitude

                    article["distance_to_city_centre"] = geopy.distance.geodesic(city_centre_coordinates.point, coordinates.point).km

                article["synchronized_at"] = datetime.now()

                # add article to list
                articles.append(article)

            upload_file(s3, CONFIG.AWS_BUCKET, f'{CONFIG.AWS_BUCKET_LOCATION}/export_{datetime.now().strftime("%Y%m%d")}_page{page}.json', json.dumps(articles, indent=4, sort_keys=True, default=str, ensure_ascii=False).encode('utf8'))

            print(f"-- Took {time.time() - mid_time} seconds to process page #{page}. --")

        except requests.HTTPError as hp:
            print(hp)

    print("Data was fetched successfully.")
    print(f"- Took {time.time() - start_time} to fetch data. -")

    print(f"***** Total execution time: {time.time() - start_time} seconds. *****")
