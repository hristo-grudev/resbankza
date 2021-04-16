import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import ResbankzaItem
from itemloaders.processors import TakeFirst


class ResbankzaSpider(scrapy.Spider):
	name = 'resbankza'
	start_urls = ['https://www.resbank.co.za/bin/sarb/solr/searchForPublication?operator=none&tagsListAuthored=SARB:what%27s-new&childTagSelected=&parentTag=&rows=999999&start=0&year=&sort=publishDate_desc']

	def parse(self, response):
		data = json.loads(response.text)
		for post in data['solrDocumentList']:
			url = post['url']
			date = post['publishDate']
			title = post['title']
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="my-5"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description if '{' not in p]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ResbankzaItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
