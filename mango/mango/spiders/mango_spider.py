import json
import re

import scrapy
from jsonpath import jsonpath
from scrapy import Selector


class MangoSpiderSpider(scrapy.Spider):
    name = "mango_spider"
    domain = "https://shop.mango.com/"
    url = "https://shop.mango.com/de/herren/highlights/neue-kollektion-t-shirts_d19337298"
    start_urls = ["https://shop.mango.com/de/herren/highlights/neue-kollektion-t-shirts_d19337298"]
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'start_rank': 0})

    def category_parser(self, response):
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", False)
        # current_page = response.meta.get("current_page", 1)
        rank = (response.meta.get('current_page', 1) - 1)
        if first_hit:
            script_text = selector.xpath("//script[contains(text(),'idSeccionActiva')]//text()").extract_first()
            script_text = script_text.split('=', 1)[1].split(';')[0]
            text = json.loads(script_text)
            url_part = text['idSeccionActiva']
            url = f"{self.domain}ws-product-lists/v1/channels/shop/countries/de/catalogs/{url_part}?language=de"
            # print(url)
            yield scrapy.Request(url=url, headers=self.header, callback=self.category_parser,
                                 meta={'first_hit': False})

        data = json.loads(response.body)
        products = jsonpath(data, "$.")



