import scrapy


class GrouplacSpiderSpider(scrapy.Spider):
    name = "GroupLAC_Spider"
    allowed_domains = ["scienti.minciencias.gov.co"]
    start_urls = ["https://scienti.minciencias.gov.co/gruplac/jsp/visualiza/visualizagr.jsp?nro=00000000004807"]

    def parse(self, response):
        pass
