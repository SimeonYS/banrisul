import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import BbanrisulItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class BbanrisulSpider(scrapy.Spider):
	name = 'banrisul'
	start_urls = ['https://www.banrisul.com.br/bob/link/bobw00hn_noticias_lista.aspx?secao_id=21']

	def parse(self, response):
		post_links = response.xpath('//span[@class="tituloNoticia corLink"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@id="ctl00_ctl00_Conteudo_MainContent_lnkProxima"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@class="data"]/text()').get()
		title = response.xpath('//span[@class="tituloNoticia"]/text()').get()
		content = response.xpath('//div[@class="conteudoTexto textoNoticia"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=BbanrisulItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
