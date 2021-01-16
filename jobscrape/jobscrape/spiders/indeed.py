#########################################################
# Indeed clearly doesn't like spiders and scrapers      #
# The Indeed spider keeps getting blocked by robots.txt #
#########################################################




import scrapy
import time

class IndeedSpider(scrapy.Spider):
    name = 'indeed'
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/jobs?q=data%20analyst&l=New%20Jersey']
    download_delay = 1.0

    def parse(self, response):
        # print(repsonse.body)
        
        yield {
            'jobs' : response.xpath('.//div[@id="searchCountPages"]/text()').get('').strip()
        }

        # Found the below on stack exchange
        SET_SELECTOR = '.jobsearch-SerpJobCard'
        for jobListing in response.css(SET_SELECTOR):
            url = jobListing.xpath('.//h2[@class="title"]/a/@href').get('').strip()
            # time.sleep(1)
            yield scrapy.Request(
                    response.urljoin(url),
                    callback=self.parse_post_page
                    )
            # Yield is necessary to return scraped data.
            # yield {
            #     # And here you get a value from each job.
            #     'company': jobListing.xpath('.//span[@class="company"]/a/text()').get('').strip(),
            #     'location': jobListing.xpath('.//div[@class="location"]/a/text()').get('').strip()
            # }
    
    def parse_post_page(self, response):

            yield {
                'job title' : response.css('h1 ::text').extract_first(),
                'company and locale' : response.css('.jobsearch-InlineCompanyRating').get('').strip()
            }


