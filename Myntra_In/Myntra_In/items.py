# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyntraInItem(scrapy.Item):
    # define the fields for your item here like:
    product_name = scrapy.Field()
    rank = scrapy.Field()
    sku = scrapy.Field()
    product_url = scrapy.Field()
    brand = scrapy.Field()
    breadcrumbs = scrapy.Field()
    color = scrapy.Field()
    mrp = scrapy.Field()
    selling_price = scrapy.Field()
    pdp_images = scrapy.Field()
    variants = scrapy.Field()
    description = scrapy.Field()
    style_attributes = scrapy.Field()
    rating = scrapy.Field()
    rating_count = scrapy.Field()
    review_count = scrapy.Field()


