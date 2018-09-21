import json

import requests
from bs4 import BeautifulSoup

def scrape(tag):
    """Scrape post data from a tag's search page"""
    page = requests.get('https://tumblr.com/search/{}/recent'.format(tag))
    html = BeautifulSoup(page.text, features='html.parser')

    return [json.loads(post.attrs['data-json']) for post in html.find_all('article', class_='post')]


if __name__ == '__main__':
    import pprint
    pprint.pprint(scrape('transgirlsruletheworld'))
