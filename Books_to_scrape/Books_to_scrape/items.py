# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BooksToScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    book_rank = scrapy.Field()
    book_name = scrapy.Field()
    book_image = scrapy.Field()
    book_price = scrapy.Field()
    book_rating = scrapy.Field()
    book_description = scrapy.Field()
    book_stock = scrapy.Field()


