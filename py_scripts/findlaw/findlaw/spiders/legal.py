# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor



class legalSpider(CrawlSpider):
    name = "legal"
    allowed_domains = ["http://caselaw.findlaw.com/"]
    start_urls = [
        'http://caselaw.findlaw.com/summary/search/?query=filters&court=us-1st-circuit&dateFormat=yyyyMMdd&topic=cs_42&pgnum=1',
        'http://caselaw.findlaw.com/summary/search/?query=filters&court=us-2nd-circuit&dateFormat=yyyyMMdd&topic=cs_42&pgnum=1'
    ]


    rules = (Rule(LinkExtractor(allow=(), allow_domains=allowed_domains),callback='parse_item', follow=True),)


    print('WTF')

    def parse_item(self, response):
        print('Processing..' + response.url)
        print('WWWWTF')



        # item_links = response.css('.large > .detailsLink::attr(href)').extract()
        # for a in item_links:
        #     yield scrapy.Request(a, callback=self.parse_detail_page)


    def parse_detail_page(self, response):
        title = response.css('h1::text').extract()[0].strip()
        price = response.css('.pricelabel > strong::text').extract()[0]

        #         item = OlxItem()
        #         item['title'] = title
        #         item['price'] = pricels

        #         item['url'] = response.url
        pass
        # yield item