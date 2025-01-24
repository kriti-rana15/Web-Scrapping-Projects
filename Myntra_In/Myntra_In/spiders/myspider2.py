import json
import math
import re
from urllib.parse import urlparse, parse_qsl, urljoin

import scrapy
from jsonpath import jsonpath
from scrapy import Selector
from ..items import MyntraInItem


class MyntraSpiderSpider(scrapy.Spider):
    name = "myntra_spider2"
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
                             meta={'first_hit': True, 'current_page': 1, 'start_rank': 0, 'cat_json': None})

    def category_parser(self, response):
        # global cat_json, total_pages
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", True)
        current_page = response.meta.get("current_page", 1)
        # rank = response.meta.get("start_rank", 1)
        product_urls = []
        page_size = 50
        script_text = selector.xpath("//script[contains(text(),'searchData')]//text()").extract_first()
        json_text = re.findall(r'{.*}', script_text)[0]
        cat_json = json.loads(json_text)
        total_count = jsonpath(cat_json, '$.searchData.results.totalCount')
        total_count = int(total_count[0])
        total_pages = math.ceil(total_count / page_size)
        products = jsonpath(cat_json, '$.searchData.results.products')[0]

        for i in products:
            product_url = jsonpath(i, '$.landingPageUrl')[0]
            product_url = urljoin(self.base_url, product_url)
            # print(product_url)
            # product_urls.append(product_url)
            # yield scrapy.Request(url=product_url, headers=self.header, callback=self.product_parser)
            yield {"product_url": product_url}
        for page in range(33):
            next_page = f'{self.url}?p={page}'
            # print(next_page)
            yield scrapy.Request(url=next_page, headers=self.header, callback=self.category_parser,
                                 meta={'first_hit': False, 'current_page': f"{page + 1}", 'cat_json': cat_json})


    def product_parser(self, response):
        selector = Selector(text=response.text)
        items = MyntraInItem()
        script_text = selector.xpath("//script[contains(text(),'pdpData')]//text()").extract_first()
        json_text = re.findall(r'{.*}', script_text)[0]
        prod_json = json.loads(json_text)
        # prod_data = jsonpath()

        name = jsonpath(prod_json, '$.pdpData.name')[0]


        # print(name)
        items['name'] = name
        yield items
