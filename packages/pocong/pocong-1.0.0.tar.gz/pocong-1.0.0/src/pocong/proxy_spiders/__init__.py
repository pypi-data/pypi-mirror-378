# Init file for spiders module to make it a package
import random

import requests
import pandas as pd
from scrapy.crawler import CrawlerProcess

from pocong.proxy_spiders.spiders.free_proxy_list_net_spider import ProxySpider


class GetProxy():
    '''
    Class to get proxies using Scrapy spiders and validate them.
    '''
    def __init__(self):
        pass

    def _check_proxy(self, x):
        proxy = f"http://{x['ip']}:{x['port']}"
        try:
            response = requests.get("https://httpbin.org/ip", proxies={'https': proxy}, timeout=10)
            if response.status_code == 200 and response.json().get('origin') == x['ip']:
                print(f"checking proxy: {proxy} success")  # noqa
                return response.status_code
            print(f"checking proxy: {proxy} failed")  # noqa
            return 0
        except requests.RequestException:
            print(f"checking proxy: {proxy} failed")  # noqa
            return 0

    def _run_example_spider(self):
        process = CrawlerProcess(settings={
            "LOG_LEVEL": "ERROR",
            "ITEM_PIPELINES": {'pocong.proxy_spiders.pipelines.Pipelines': 1},
        })
        process.crawl(ProxySpider)
        process.start()
        from pocong.proxy_spiders.pipelines import collected_items
        return collected_items

    def _get_proxy_from_scrape(self):
        items = self._run_example_spider()
        df = pd.DataFrame(items)
        df = df[df['https'] == 'yes']
        df = df.drop_duplicates(subset=['ip', 'port'])
        proxies_json = df.to_dict(orient='records')
        return proxies_json

    def get_proxy(self):
        '''
        Get a working proxy from the list of proxies.
        parameter: None
        return: dict or None
        '''
        proxies_json = self._get_proxy_from_scrape()
        for proxy in proxies_json:
            if self._check_proxy(proxy) == 200:
                return proxy

    def get_proxy_random(self):
        '''
        Get a random working proxy from the list of proxies.
        parameter: None
        return: dict or None
        '''
        proxies_json = self._get_proxy_from_scrape()
        retry = 0
        proxy = None
        while retry < 20:
            retry += 1
            proxy = random.choice(proxies_json)
            if self._check_proxy(proxy) == 200:
                break
        return proxy
