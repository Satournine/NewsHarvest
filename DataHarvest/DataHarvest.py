from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pymongo import MongoClient

current_directory = os.path.dirname(os.path.abspath(__file__))
log_directory = os.path.join(current_directory, "..", "logs")
os.makedirs(log_directory, exist_ok=True)
log_filename = "logs.log"
log_file_path = os.path.join(log_directory, log_filename)

logging.basicConfig(filename=log_file_path, level = logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = MongoClient("mongodb://localhost:27017")
db = client["orkun_tuna"]

news_collection = db["news"]
word_frequency_collection = db["word_frequency"]
stats_collection = db["stats"]

chrome_driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
browser = webdriver.Chrome()
base_URL = 'https://turkishnetworktimes.com/kategori/gundem/'
max_pages = 50
count = 0
success_count = 0
fail_count = 0

browser.get(base_URL)

start_time = time.time()

def insert_news(news_data):
    try:
        news_collection.insert_one(news_data)
        logging.info(f"News data inserted successfully: {news_data}")
    except Exception as e:
        logging.error(f"Error inserting news data: {e}")

def insert_stats(stats_data):
    try:
        stats_collection.insert_one(stats_data)
        logging.info(f"Stat data inserted succesfully: {stats_data}")
    except Exception as e:
        logging.error(f"Error inserting stat data: {e}")

def get_links_from_page(page_number):
    page_url = base_URL if page_number == 1 else f"{base_URL}page/{page_number}/"
    request = requests.get(page_url).content
    soup = BeautifulSoup(request, "html.parser")
    news_list = soup.find_all('div', {'class': 'kategori_yazilist'})
    return [link['href'] for news in news_list for link in news.find_all('a', {'class': 'post-link'})]


def extract_img_urls(soup, div_class ):
    div = soup.find('div', {'class': div_class})
    img_urls = []
    if div:
        for img in div.find_all('img'):
            img_url = img.get('data-src', img.get('src'))
            if img_url and not img_url.startswith('data:image'):
                img_urls.append(img_url)
    return img_urls

def extract_dates(soup, div_class):
    yazibio_div = soup.find('div', class_= div_class)
    tarih_spans = yazibio_div.find_all('span', class_='tarih')

    publish_date = 'Unknown'
    update_date = 'Unknown'

    try:
        publish_date = tarih_spans[0].find('time').get('datetime')
    except IndexError:
        pass  #keep publish_date as 'Unknown'
    try:
        update_date = tarih_spans[1].find('time').get('datetime')
    except IndexError:
        pass  #keep update_date as 'Unknown'

    return publish_date, update_date

def scrape_article(link):
    try:
        response = requests.get(link).content
        details_soup = BeautifulSoup(response, "html.parser")
        publish_date, update_date = extract_dates(details_soup, div_class='yazibio')
        text_content_div = details_soup.find('div', {'class': 'yazi_icerik'})
        news_content_text = ' '.join(p.get_text(strip=True) for p in text_content_div.find_all('p')) if text_content_div else ''
        logging.info(f"Article scraped successfully from {link}")
        return {
            "url": link,
            "header": details_soup.find('h1', {'class': 'single_title'}).get_text(strip=True),
            "summary": details_soup.find('h2', {'class': 'single_excerpt'}).find('p').get_text(strip=True),
            "text": news_content_text,
            "img_url_list": extract_img_urls(details_soup, div_class='post_line'),
            "publish_date": publish_date,
            "update_date": update_date
        }
    except Exception as e:
        logging.error(f"Error occurred on {link}: {e}")
        print(f"Error occured on {link} : {e}")
        return None


all_links = []
for page_number in range(1, max_pages + 1):
    all_links.extend(get_links_from_page(page_number))
count = len(all_links)

with ThreadPoolExecutor(max_workers = 10) as executor:
    future_to_link = {executor.submit(scrape_article, link): link for link in all_links}
    for future in as_completed(future_to_link):
        result = future.result()
        if result:
            print(result)
            insert_news(result)
            success_count += 1
        else:
            fail_count += 1

end_time = time.time()
elapsed_time = end_time - start_time


stats = {
    "elapsed_time": elapsed_time,
    "count": count,
    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "success_count": success_count,
    "fail_count": fail_count
}
logging.info(f"Finished scraping. Total time: {elapsed_time} seconds.")
logging.info(f"Scraping stats: {stats}")
insert_stats(stats)
print(stats)

client.close()