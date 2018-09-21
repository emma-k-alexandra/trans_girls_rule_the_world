import json

import requests
from bs4 import BeautifulSoup

def scrape(tag):
    """Scrape post data from a tag's search page"""
    page = requests.get('https://tumblr.com/search/{}/recent'.format(tag))
    html = BeautifulSoup(page.text, features='html.parser')

    posts = []
    for post in html.find_all('article', class_='post'):
        post_json = json.loads(post.attrs['data-json'])
        post_tags = [post.attrs['data-tag'] for post in post.find_all('a', class_='post_tag')]

        post_json['tags'] = post_tags
        posts.append(post_json)

    return post_json


if __name__ == '__main__':
    import pprint
    pprint.pprint(scrape('transgirlsruletheworld'))
