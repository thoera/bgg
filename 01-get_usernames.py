# -*- coding: utf-8 -*-

"""
In accordance with https://boardgamegeek.com/robots.txt
- scraping the usernames is permitted
- we should respect a delay of 5 seconds between each request
"""

from bs4 import BeautifulSoup
import logging
import requests
import time

logging.basicConfig(filename='logs/usernames.log',
                    filemode='w', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def get_last_page(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    return int(soup.find('a', title='last page')
                   .text
                   .replace('[', '')
                   .replace(']', ''))


def get_usernames(url):
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, 'html.parser')
    return [user.find('a', href=True)['href'][6:]
            for user in soup.find_all('div', class_='username')]


def write_usernames(usernames, file):
    with open(file, mode='a+', encoding='utf-8') as f:
        for username in usernames:
            f.write(f'{username}\n')


url = 'https://boardgamegeek.com/users?country=France&state=&city='
last_page = int(get_last_page(url))

for page in range(1, last_page + 1):
    usernames = []
    url = (f'https://boardgamegeek.com/users/page/{page}'
           '?country=France&state=&city=')
    usernames.extend(get_usernames(url))
    write_usernames(usernames, 'data/usernames.txt')
    print(f'page {page}/{last_page} done')
    logging.info(f'page {page}/{last_page} done')
    time.sleep(5)  # be nice with the server and wait 5 seconds
