import re
from urllib.parse import urljoin, urlparse, parse_qsl, urlencode, urlunparse
import scrapy
from scrapy import Selector

from ..items import BataItem


class BataSpiderSpider(scrapy.Spider):
    name = "bata_spider"
    domains = ['https://www.bata.com']
    url = "https://www.bata.com/in/women/shoes/flats/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        yield scrapy.Request(url=self.url, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'current_page': 1})

    def category_parser(self, response):
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", True)
        current_page = response.meta.get("current_page", 1)
        if first_hit:
            total_count_str = selector.xpath('//span[contains(@class, "cc-plp-counter-products")]/text()').extract_first()
            total_count = re.findall(r"\d+", total_count_str)
            total_count = int(total_count[0])
            page_size = 24

            url_parts = list(urlparse(self.url))
            query = dict(parse_qsl(url_parts[4]))
            query['start'] = 0
            query['sz'] = total_count
            url_parts[4] = urlencode(query)
            next_url = urlunparse(url_parts)

            yield scrapy.Request(url=next_url, headers=self.header, callback=self.category_parser,
                                 meta={'first_hit': False})

        shoes = selector.xpath("//a[@class='js-analytics-productClick']/@href").extract()
        for shoe in shoes:
            shoe_url = urljoin("https://www.bata.com", shoe)


            yield scrapy.Request(url=shoe_url, headers=self.header, callback=self.product_parser)

    def product_parser(self, response):

        selector = Selector(text=response.text)
        items = BataItem()

        name = selector.xpath("//h1[contains(@class, 'product-name cc-pdp-product-name')]/text()").extract_first()
        
        breadcrumbs_list = [bread.replace("\n","").strip() for bread in selector.xpath("//li[contains(@class, 'breadcrumb-item cc-breadcrumb-item')]//a/text()").extract()]
        
        color = selector.xpath("//span[contains(@class, 'color-value')]/text()").extract_first()
        color = color.replace("\n","").strip()
        
        labels = selector.xpath("//span[contains(@class, 'cc-description-attribute-label')]/text()").extract()
        description_labels = [label.replace("\n","").strip() for label in labels]
        
        article_number = selector.xpath("//span[contains(@data-target, 'articleNo')]/text()").extract_first().replace("\n","").strip()
        
        brand = selector.xpath("//span[contains(@data-target, 'brand')]/text()").extract_first().replace("\n","").strip()
        
        manufacturer = selector.xpath("//span[contains(@data-target, 'manufacturerName')]/text()").extract_first().replace("\n","").strip()
        
        origin = selector.xpath("//span[contains(@data-target, 'madeIn')]/text()").extract_first().replace("\n","").strip()
        generic = selector.xpath("//span[contains(@data-target, 'displayCategory')]/text()").extract_first().replace("\n","").strip()
        quantity = selector.xpath("//span[contains(@data-target, 'packagingUnits')]/text()").extract_first().replace("\n","").strip()
        marketed = selector.xpath("//span[contains(@data-target, 'marketedBy')]/text()").extract_first().replace("\n","").strip()
        warranty = selector.xpath("//span[contains(@data-target, 'warranty')]/text()").extract_first().replace("\n","").strip()
        heelHeight = selector.xpath("//span[contains(@data-target, 'heelHeight')]/text()").extract_first().replace("\n","").strip()
        platformHeight = selector.xpath("//span[contains(@data-target, 'platformHeight')]/text()").extract_first().replace("\n","").strip()
        shoeHeight = selector.xpath("//span[contains(@data-target, 'shoeHeight')]/text()").extract_first().replace("\n","").strip()
        dimHeight = selector.xpath("//span[contains(@data-target, 'dimHeight')]/text()").extract_first().replace("\n","").strip()
        dimWidth = selector.xpath("//span[contains(@data-target, 'dimWidth')]/text()").extract_first().replace("\n","").strip()
        dimDepth = selector.xpath("//span[contains(@data-target, 'dimDepth')]/text()").extract_first().replace("\n","").strip()
        strapLength = selector.xpath("//span[contains(@data-target, 'strapLength')]/text()").extract_first().replace("\n","").strip()
        additionalHandle = selector.xpath("//span[contains(@data-target, 'additionalHandle')]/text()").extract_first().replace("\n","").strip()
        materials_headings = selector.xpath("//div[contains(@class,'b-pdp__material-type cc-pdp__material-type')]//span[contains(@class, 'b-pdp__text')]/text()").extract()
        materials_values = selector.xpath("//span[contains(@class,'b-pdp__material-info cc-pdp__material-info')]//span[contains(@class, 'b-pdp__text')]/text()").extract()
        materials ={}

        for i in range(len(materials_headings)):
            key = materials_headings[i]
            value = materials_values[i]
            materials[key] = value

        description_values = [article_number,brand,manufacturer,origin,generic,quantity,marketed,warranty,heelHeight,platformHeight,shoeHeight,dimHeight,dimWidth,dimDepth,strapLength,additionalHandle,materials]
        description = {}
        for i in range(len(description_labels)):
            key = description_labels[i]
            value = description_values[i]
            description[key] = value

        feature_image = selector.xpath("//div[contains(@class, 'cc-container-dis-picture')]//picture//img/@data-src").extract_first()

        items['description'] = description
        items['feature_image'] = feature_image
        items['product_name'] = name
        items['breadcrumbs'] = breadcrumbs_list
        items['color'] = color
        # items['description_labels'] = description_labels
        yield items