import re
from urllib.parse import urljoin
import scrapy
from scrapy import Selector

from ..items import BoggiMilanoItem


class BoogiSpiderSpider(scrapy.Spider):
    name = "boogi_spider"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        urls = "https://www.boggi.com/en_IN/clothing/jeans/"

        yield scrapy.Request(url=urls, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'current_page': 1})

    def category_parser(self, response):
        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", True)
        current_page = response.meta.get("current_page", 1)
        if first_hit:
            total_count_str = selector.xpath('//small/text()').extract_first()
            # total_count = int(''.join(char for char in total_count_str if char.isdigit()))
            total_count = 16
            page_size = 12
            # number_of_pages = int(total_count / page_size)
            number_of_pages = 2
            # print(total_count)
            for pages in range(current_page, number_of_pages):
                next_page_url = f'{response.url}?start={pages * page_size}&sz={page_size}'
                # next_page_url = selector.xpath('//a[contains(@class,"page-switcher next")]/@href').extract_first()
                yield scrapy.Request(url=next_page_url, headers=self.header, callback=self.category_parser,
                                     meta={'first_hit': False, 'current_page': f"{pages + 1}"})

        jeans = selector.xpath('//div[contains(@class,"product-image")]/a[contains(@class,"product-image-render")]/@href').extract()
        for jean in jeans:
            jeans_url = jean
            # print(jeans_url)
            yield scrapy.Request(url=jeans_url, headers=self.header, callback=self.product_parser)

    def product_parser(self, response):

        selector = Selector(text=response.text)
        items = BoggiMilanoItem()

        name_str = selector.xpath('//h1[contains(@class,"h4 product-name")]/text()').extract_first()
        name = name_str.replace("\n","").strip()
        breadcrumbs_list = [bread.replace("\n","").strip() for bread in selector.xpath('//div[contains(@class, "breadcrumb-group")]/ul/li/a/text()').extract()]
        # color = selector.xpath('//span[contains(@class,"h6")]/span').extract_first()
        # color = selector.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "h6", " " ))]//span').extract_first()
        color = selector.xpath('//li[@class = "selectable selected"]/a[@class = "swatchanchor swatches-color"]/img/@alt').extract_first()
        description_value = selector.xpath("//div[@class = 'content'][1]//div[contains(@style, 'width:125%;text-align:justify;')]/text()").extract()
        description = "".join(description_value)
        feature_image = selector.xpath('//img[contains(@class, "product-image-hero")]/@src').extract_first()
        mrp_value = selector.xpath('//span[contains(@class,"product-standard-price")]/text()').extract_first()
        mrp_value = mrp_value.replace("\n", "").strip() if mrp_value else None
        mrp = float(re.search(r'(\d+,\d+)', mrp_value).group(1).replace(',','.')) if mrp_value else None
        price = selector.xpath('//span[contains(@class,"product-sales") or contains(@class,"price-sales")]/text()').extract_first()
        selling_price = float(re.search(r'(\d+,\d+)', price).group(1).replace(',','.'))
        # pdp_images = selector.xpath('//img[starts-with(@data-index, "1") or starts-with(@data-index, "2") or starts-with(@data-index, "3") or starts-with(@data-index, "4") or starts-with(@data-index, "5")]/@src').get()
        pdp_images = selector.xpath('//img[contains(@class,"product-thumbnail")]/@src').extract()
        feature_list_key = selector.xpath('//div[contains(@class, "attributeWrapper")]//div[contains(@class, "attributeLabel")]/text()').extract()
        feature_list_value = selector.xpath('*//div[contains(@class, "attributeWrapper")]//div[contains(@class, "attributeValue")]/text()').extract()
        feature_list = [f'{key} : {value}' for key, value in zip(feature_list_key, feature_list_value)]
        style_attribute = selector.xpath('//div[contains(@class, "expandable product-modelwear-info cell small-12 medium-8 medium-offset-2 large-12 large-offset-0")]//div[contains(@class,"content")]//ul//li/text()').extract()
        style_attributes = [attribute.replace("\n","").replace("\r", "").strip() for attribute in style_attribute]
        size = selector.xpath('//div[contains(@class, "value variants-content")]//ul[contains(@class, "swatches-list swatches-size")]//li//a/text()').extract()
        sizes = [data.replace("\n","") for data in size]
        available = selector.xpath('//div[contains(@class, "value variants-content")]//ul[contains(@class, "swatches-list swatches-size")]//li/@class').extract()
        available_value = [purchase.replace(" variation-group-value", "") for purchase in available]
        availability = [True if avalue == "selectable" else False for avalue in available_value]
        variants = []
        for i in range(len(sizes)):
            variant = {
                "available": availability[i],
                "color": color,
                "size": sizes[i],
                "stock": None,
                "variant-sku": ""
            }
            variants.append(variant)
        # offers = selector.xpath('//span[contains(@class, "price-promo-callout")]/text()')[1].extract()
        # offer_list = [offer.replace("/n", "") for offer in offers]
        related_products = selector.xpath('//div[@class="product-image quick-view-container"]//a[contains(@class, "product-image-render")]/@href').extract()
        relation_text = selector.xpath('//div[contains(@class, "product-recommendations")]//h3[contains(@class, "text-center")]/text()').extract_first()
        relation = relation_text.replace("\n", "")

        items['product_name'] = name
        items['color'] = color
        items['description'] = description
        items['breadcrumbs'] = breadcrumbs_list
        items['feature_image'] = feature_image
        items['mrp'] = mrp
        items['selling_price'] = selling_price
        items['pdp_images'] = pdp_images
        items['feature_list'] = feature_list
        items['style_attributes'] = style_attributes
        # items['sizes'] = sizes
        # items['availability'] = availability

        items['variants'] = variants
        items['related_products'] = related_products
        items['relation'] = relation
        # items['offer_list'] = offer_list

        yield items
