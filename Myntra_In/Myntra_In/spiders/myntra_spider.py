import json
import math
import re
from urllib.parse import urlparse, parse_qsl, urljoin

import scrapy
from jsonpath import jsonpath
from scrapy import Selector
from ..items import MyntraInItem


class MyntraSpiderSpider(scrapy.Spider):
    name = "myntra_spider"
    # custom_settings = {
    #     'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    # }
    page_size = 50
    base_url = "https://www.myntra.com/"
    start_urls = ["https://www.myntra.com/hair-dryer"]
    url = "https://www.myntra.com/hair-dryer"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'current_page': 1, 'start_rank': 0})

    def category_parser(self, response):
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", False)
        current_page = response.meta.get("current_page", 1)
        rank = (response.meta.get('current_page', 1) - 1) * self.page_size

        if first_hit:
            script_text = selector.xpath("//script[contains(text(),'searchData')]//text()").extract_first()
            json_text = re.findall(r'{.*}', script_text)
            cat_json = json.loads(json_text[0])
            total_count = jsonpath(cat_json, '$.searchData.results.totalCount')
            total_count = int(total_count[0])
            total_pages = math.ceil(total_count / self.page_size)

            for page in range(1,total_pages):
                next_page = f'{self.url}?p={page + 1}'
                yield scrapy.Request(url=next_page, headers=self.header, callback=self.category_parser,
                                         meta={'first_hit': False, 'current_page': page + 1})

        product_json = selector.xpath('//script[contains(text(), "searchData")]/text()').extract_first()
        product_json = re.findall(r'{.*}', product_json)
        cat_json = json.loads(product_json[0])

        products_data = jsonpath(cat_json, '$.searchData.results.products')[0]

        for product in products_data:
            product_url = jsonpath(product, '$.landingPageUrl')[0]
            sku = jsonpath(product, '$.inventoryInfo[0].skuId')[0]
            url = urljoin(self.base_url, product_url)
            rank = rank + 1

            # print(url)
            data = {"url": url,
                      "rank": rank,
                    "sku": sku}

            yield scrapy.Request(url=url, headers=self.header, callback=self.product_parser, meta={'data': data})


    def product_parser(self, response):
        selector = Selector(text=response.text)
        items = MyntraInItem()
        script_text = selector.xpath("//script[contains(text(),'pdpData')]//text()").extract_first()
        data = response.meta.get('data')
        json_text = re.findall(r'{.*}', script_text)[0]
        prod_json = json.loads(json_text)
        prod_data = jsonpath(prod_json, "$.pdpData")[0]

        product_url = response.url
        name = jsonpath(prod_data, '$.name')[0]
        brand = jsonpath(prod_data, '$.brand.name')[0]

        breadcrumb_selector = selector.xpath('//script[contains(text(),"BreadcrumbList")]/text()').extract_first()
        breadcrumb_json = json.loads(breadcrumb_selector)
        breadcrumb_data = jsonpath(breadcrumb_json, '$.itemListElement')[0]

        breadcrumbs = []
        for i in breadcrumb_data:
            breadcrumbs.append(jsonpath(i, '$.item.name')[0])

        mrp = jsonpath(prod_data, '$.mrp')[0]
        selling_price = jsonpath(prod_data, '$.price.discounted')[0]
        images = jsonpath(prod_data, '$.media.albums[0].images')[0]
        color = jsonpath(prod_data, '$.baseColour')[0]
        description = jsonpath(prod_data, '$.productDetails[0].description')[0].replace("<ul>", "").replace("<li>",
                                                                                                            "").replace(
            "</li>", "").replace("</ul>", "").replace("<br>","").strip()
        style_attributes = {}

        prod_details = jsonpath(prod_data, '$.productDetails')[0]
        for i in range(1, len(prod_details)):
            title = jsonpath(prod_data, f'$.productDetails[{i}].title')[0]
            desc = jsonpath(prod_data, f'$.productDetails[{i}].description')[0].strip().split('<br>')
            style_attributes[title] = desc
        # attributes = jsonpath(prod_data, '$.articleAttributes')[0]
        # style_attributes.update(attributes)

        pdp_images = []
        for i in images:
            images_url = jsonpath(i, '$.imageURL')[0]
            pdp_images.append(images_url)
        sizes = jsonpath(prod_data, '$.sizes')[0]
        variants = []
        for i in sizes:
            available = jsonpath(i, '$.available')[0]
            stock = jsonpath(i, '$.sizeSellerData[0].availableCount')
            stock = stock[0] if available else None

            dict = {
                'size_name': jsonpath(i, '$.label')[0],
                'variant_sku': jsonpath(i, '$.skuId')[0],
                'available': jsonpath(i, '$.available')[0],
                'stock': stock,
                'color': color
            }
            variants.append(dict)

        ratings = jsonpath(prod_data, '$.ratings.averageRating')
        rating = float(ratings[0]) if ratings else None
        rating_c = jsonpath(prod_data, '$.ratings.totalCount')
        rating_count = int(rating_c[0]) if rating_c else None
        review_c = jsonpath(prod_data, '$.ratings.reviewInfo.reviewsCount')
        review_count = int(review_c[0]) if review_c else None

        items['product_name'] = name
        items['rank'] = data['rank']
        items['sku'] = data['sku']
        items['product_url'] = product_url
        items['brand'] = brand
        items['breadcrumbs'] = brand
        items['color'] = color
        items['mrp'] = mrp
        items['selling_price'] = selling_price
        items['pdp_images'] = pdp_images
        items['description'] = description
        items['style_attributes'] = style_attributes
        items['rating'] = rating
        items['rating_count'] = rating_count
        items['review_count'] = review_count
        items['variants'] = variants


        yield items
