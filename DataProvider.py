import time
import json
import asyncio
import random
import requests

from functools import lru_cache
from random import choice
from urllib.parse import unquote
from sys import stderr
from loguru import logger
from urllib3 import disable_warnings

from urllib.parse import urlparse

HOSTS = 'https://github.com/opengs/uashieldtargets/blob/v2/sites.json'
PROXIES_URL = 'https://raw.githubusercontent.com/opengs/uashieldtargets/master/proxy.json'


class DataProvider:
    def __init__(self):
        self._proxies = []
        self._sites = []
        self.index = 0
        self._lastupdate = 0
        # self.eTag = ''

    def get_url(self):
        if self.index <= 0:
            self.get_sites()
        self.index = self.index - 1
        url = self._sites[self.index]
        return url

    def get_proxies(self, url: str = PROXIES_URL):
        if not self._proxies:
            while True:
                try:
                    data = requests.get(url, timeout=5).json()
                    for proxy_data in data:
                        url = f'{proxy_data["auth"]}@{proxy_data["ip"]}'
                        self._proxies.append(unquote(url))
                    break
                except:
                    continue

        return self._proxies


    def get_sites(self, url: str = HOSTS):
        if not self._sites or time.time() > self._lastupdate + 60*60: #updte every hour
            while True:
                try:
                    # print("updating targets...")
                    # https://api.github.com/repos/opengs/uashieldtargets/commits?path=sites.json&page=1&per_page=1
                    # response = requests.head(url, allow_redirects=False)
                    # if response.status_code != 200:
                    #     etag = None
                    # else:
                    #     etag = response.headers.get("ETag")
                    # if not etag or (etag == self.eTag):
                    #     self.index = len(self._sites)
                    #     break
                    # else: 
                    #     self.eTag = etag
                    data = requests.get(url, timeout=5).json()
                    self._sites = []
                    for site in data:
                        if 'attack' not in site or ('attack' in site and not site['attack'] == 0):
                            domain = urlparse(unquote(site['page']))
                            self._sites.append(domain.netloc)
                    self._lastupdate = time.time()
                    break
                except:
                    continue
        self.index = len(self._sites)
        return self._sites
    
    def fix_url(self, url: str, force_https: bool = False) -> str:
        if not url.startswith('http'):
            'http://' + url
        if force_https:
            url = url.replace('http://', 'https://')
        return url



