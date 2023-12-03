from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime

from concurrent.futures import ThreadPoolExecutor, as_completed

chrome_driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
browser = webdriver.Chrome()
base_URL = 'https://turkishnetworktimes.com/kategori/gundem/'
max_pages = 50
count = 0
success_count = 0
fail_count = 0

browser.get(base_URL)

start_time = time.time()

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


"""for news in news_list:
    for link in news.find_all('a', {'post-link'}):
        count += 1
        try:

            response = requests.get(link['href']).content
            details_soup = BeautifulSoup(response, "html.parser")
            publish_date, update_date = extract_dates(details_soup, div_class='yazibio')
            text_content_div = details_soup.find('div', {'class': 'yazi_icerik'})
            news_content_text = ' '.join(p.get_text(strip = True) for p in text_content_div.find_all('p')) if text_content_div else ''
            news_data = {
                "url": link['href'],
                "header": details_soup.find('h1', {'class': 'single_title'}).get_text(strip=True),
                "summary": details_soup.find('h2', {'class': 'single_excerpt'}).find('p').get_text(strip=True),
                "text": news_content_text,
                "img_url_list": extract_img_urls(details_soup, div_class='post_line'),
                "publish_date": publish_date,
                "update_date": update_date
            }
            print(news_data)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f"Error occured: {e}")"""

def scrape_article(link):
    try:
        response = requests.get(link).content
        details_soup = BeautifulSoup(response, "html.parser")
        publish_date, update_date = extract_dates(details_soup, div_class='yazibio')
        text_content_div = details_soup.find('div', {'class': 'yazi_icerik'})
        news_content_text = ' '.join(p.get_text(strip=True) for p in text_content_div.find_all('p')) if text_content_div else ''
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
        print(f"Error occured on {link} : {e}")
        return None


all_links = []
for page_number in range(1, 2):
    all_links.extend(get_links_from_page(page_number))
count = len(all_links)

with ThreadPoolExecutor(max_workers = 10) as executor:
    future_to_link = {executor.submit(scrape_article, link): link for link in all_links}
    for future in as_completed(future_to_link):
        result = future.result()
        if result:
            print(result)
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

print(stats)