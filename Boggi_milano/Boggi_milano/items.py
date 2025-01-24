# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BoggiMilanoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_name = scrapy.Field()
    color = scrapy.Field()
    description = scrapy.Field()
    breadcrumbs = scrapy.Field()
    feature_image = scrapy.Field()
    mrp = scrapy.Field()
    selling_price = scrapy.Field()
    pdp_images = scrapy.Field()
    feature_list = scrapy.Field()
    style_attributes = scrapy.Field()
    # sizes = scrapy.Field()
    # availability = scrapy.Field()
    variants = scrapy.Field()
    offer_list = scrapy.Field()
    related_products = scrapy.Field()
    relation = scrapy.Field()
