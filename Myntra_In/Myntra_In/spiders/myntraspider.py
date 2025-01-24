import json
import math
import re
from urllib.parse import urlparse, parse_qsl, urljoin

import scrapy
from jsonpath import jsonpath
from scrapy import Selector
from ..items import MyntraInItem


class MyntraspiderSpider(scrapy.Spider):
    name = "myntraspider"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    base_url = "https://www.myntra.com/"
    start_urls = ["https://www.myntra.com/face-moisturisers"]
    url = "https://www.myntra.com/face-moisturisers"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'current_page': 1, 'start_rank': 0})

    def category_parser(self, response):
        global cat_json, total_pages, product_url
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", True)
        current_page = response.meta.get("current_page", 1)
        product_urls = []
        page_size = 50
        script_text = selector.xpath("//script[contains(text(),'searchData')]//text()").extract_first()
        json_text = re.findall(r'{.*}', script_text)[0]
        cat_json = json.loads(json_text)
        total_count = jsonpath(cat_json, '$.searchData.results.totalCount')
        total_count = int(total_count[0])
        total_pages = math.ceil(total_count / page_size)
        products = jsonpath(cat_json, f'$.searchData.results.products')[0]
        # print(products)


        for product in products:
             print(product["landingPageUrl"])

        # yield {"product_url":product_url}

        for page in range(total_pages):
            next_page = f'{response.url}?p={page + 1}'
            yield scrapy.Request(url=next_page, headers=self.header, callback=self.category_parser,
                                 meta={'first_hit': False, 'current_page': f"{page + 1}"})


    def parse(self, response):
        pass
