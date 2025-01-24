from urllib.parse import urljoin
import scrapy
from scrapy import Selector
from ..items import BooksToScrapeItem
from word2number import w2n


class BooksSpiderSpider(scrapy.Spider):
    name = "books_spider"
    # book_count = 0
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

    def start_requests(self):
        urls = "https://books.toscrape.com/"

        yield scrapy.Request(url=urls, headers=self.header, callback=self.category_parser,
                             meta={'first_hit': True, 'current_page': 1, 'start_rank': 0})

    def category_parser(self, response):
        # https://books.toscrape.com/catalogue/page-2.html

        selector = Selector(text=response.text)
        first_hit = response.meta.get("first_hit", True)
        current_page = response.meta.get("current_page", 1)
        rank = response.meta.get("start_rank", 0)

        if first_hit:
            total_count = 1000
            page_size = 20
            number_of_pages = int(total_count / page_size)
            # url_parts = list(urlparse(response.url))
            for pages in range(current_page, number_of_pages ):
                next_page = f'catalogue/page-{pages+1}.html'
                next_page_url = urljoin(response.url, next_page)
                yield scrapy.Request(url=next_page_url, headers=self.header, callback=self.category_parser,
                                     meta={'first_hit': False, 'current_page': f"{pages+1}", "start_rank": pages*page_size})

        books = selector.xpath('//article[@class="product_pod"]/div/a/@href').extract()
        for book in books:
            # print(book)
            # BooksSpiderSpider.book_count += 1
            # book_rank = BooksSpiderSpider.book_count
            # pages = response.meta.get('current_page')

            book_url = urljoin(response.url, book)
            # print(book_rank, book_url)
            rank += 1
            book_rank = rank

            yield scrapy.Request(url=book_url, headers=self.header, callback=self.product_parser, meta={"book_rank": rank})

    def product_parser(self, response, ):

        selector = Selector(text=response.text)
        items = BooksToScrapeItem()

        book_rank = response.meta.get('book_rank')
        book_name = selector.xpath('//h1/text()').extract_first()
        image = selector.xpath('//img/@src').extract_first()
        book_image = image.replace('../../', 'https://books.toscrape.com/')
        price = selector.xpath('//div//p[contains(@class,"price_color")]/text()').extract_first()
        book_price = float(price[1:])
        rating = selector.xpath('//p[contains(@class, "star-rating")]/@class').extract_first()
        book_rating = float(w2n.word_to_num(rating.replace('star-rating ', '')))
        book_description = selector.xpath('//div[contains(@id,"product_description")]//following::p[1]/text()').extract_first()
        stock = selector.xpath('//p[contains(@class,"instock")]/text()')[1].extract()
        book_stock = int(''.join(char for char in stock if char.isdigit()))
        # string(normalize-space(translate(//p/text(), '\n', ' ')))
        # print(book_rating)

        items['book_rank'] = book_rank
        items['book_name'] = book_name
        items['book_image'] = book_image
        items['book_price'] = book_price
        items['book_description'] = book_description
        items['book_rating'] = book_rating
        items['book_stock'] = book_stock
        yield items
