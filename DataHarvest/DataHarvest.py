from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_driver_path = r"C:\Program Files\Google\Chrome\Application\chromedriver.exe"
browser = webdriver.Chrome()
base_URL = 'https://turkishnetworktimes.com/kategori/gundem/'

browser.get(base_URL)

request = requests.get(base_URL).content
soup = BeautifulSoup(request, "html.parser")
news_list = soup.find_all('div', {'class': 'kategori_yazilist'})


def extract_img_urls(soup, div_class ):
    div = soup.find('div', {'class': div_class})
    img_urls = []
    if div:
        for img in div.find_all('img'):
            # Check for 'data-src' attribute first, then fall back to 'src'
            img_url = img.get('data-src', img.get('src'))
            if img_url and not img_url.startswith('data:image'):
                img_urls.append(img_url)
    return img_urls
def extract_dates(soup, div_class):
    yazibio_div = details_soup.find('div', class_= div_class)
    tarih_spans = yazibio_div.find_all('span', class_='tarih')

    publish_date = 'Unknown'
    update_date = 'Unknown'

    try:
        publish_date = tarih_spans[0].find('time').get('datetime')
    except IndexError:
        pass  # If there's no such element, keep publish_date as 'Unknown'
    try:
        update_date = tarih_spans[1].find('time').get('datetime')
    except IndexError:
        pass  # If there's no such element, keep update_date as 'Unknown'

    return publish_date, update_date


for news in news_list:
    for link in news.find_all('a', {'post-link'}):
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