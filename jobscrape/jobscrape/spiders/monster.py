"""
This spider crawls monster.com for job postings.

"""

# Packages
import scrapy
import pprint
import json

from bs4 import BeautifulSoup
from bs4.element import Comment

from datetime import datetime, timedelta

# Functions 
def tags_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def get_html_text(body):
    """Extract text from html tags in the json job descriptions"""
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_text = filter(tags_visible, texts)
    return u" ".join(t.strip() for t in visible_text)

# Criteria
###############
# Job titles
prefixes = [
    'entry level ',
    'junior ', 'associate ',
    ''
    ]

titles = [
    'data',
    'data analyst', 'data scientist', 
            'business analyst', 'financial analyst', 'macro analyst', 
            'data engineer'
            ]
 

search_locations = [
    'New York, NY', 'NY',
    'Stamford, CT', 'Greenwich, CT', 'CT',
    'Newark, NJ', 'Princeton, NJ', 'Jersey City, NJ', 
    'Trenton, NJ', 'Bridgewater, NJ', 'Somerville, NJ', 
    'Summit, NJ', 'Morristown, NJ', 'Edison, NJ', 'Metuchen, NJ', 'Hackensack, NJ', 'NJ',
    'Philadelphia, PA', 'PA', 
    # 'New York', 'New Jersey', 'New Hampshire', 'Pennsylvania', 'Connecticut',
    # 'NY', 'NJ', 'CT', 
    # 'NH', 'PA',
    'NH', "New Hampshire", "Manchester, NH", "Concord, NH", "Nashua, NH", "Brattleboro, NH", "Keene, NH",
    'remote' 
    ]


class MonsterSpider(scrapy.Spider):
    name = 'monster'
    allowed_domains = ['monster.com']
    download_delay = 10
    start_urls = [f"https://www.monster.com/jobs/search/?q={title.replace(' ', '-')}&where={location.replace(' ', '-').replace(',', '__2C')}&{pages}" 
        for title in [p + t for p in prefixes for t in titles] 
            for location in search_locations
                for pages in ['stpage=1&page=7', 'stpage=8&page=15']]

    def parse(self, response):
        # print(response.body)
        # yield {
        #     'search' : response.css('h1 ::text').extract_first().strip(),
        #     'results' : response.css('h2 ::text').extract_first().strip(),
        # }
        
        job_ids = response.css('.card-content').xpath('//section/@data-jobid').extract()
        for job_id in job_ids:
            link = f'https://job-openings.monster.com/v2/job/pure-json-view?jobid={job_id}'
            yield scrapy.Request(
                        response.urljoin(link),
                        callback=self.parse_job_posting
                        )
        """ 
        Code below prints out the information from each job card. 
        This method has been abandoned in favor of extracting all job id's 
        and extracting the information from the json page associated with the job id
        """
        # SET_SELECTOR = '.card-content' 
        # for post in range(len(response.css(SET_SELECTOR))-1):
            # Yield is necessary to return scraped data.
            # yield {
                # And here you get a value from each job.
                # 'company': response.css(SET_SELECTOR)[post].xpath('.//div[@class="company"]/span/text()').get('').strip(),
                # 'title' : response.css(SET_SELECTOR)[post].css('h2 ::text').get('').strip(),
                # 'location' : response.css(SET_SELECTOR)[post].xpath('.//div[@class="location"]/span/text()').get('').strip(),
                # 'posted' : response.css(SET_SELECTOR)[post].css('time ::text').get('').strip(),
                # 'job id' : job_ids[post],
                # 'link' : response.xpath('.//header[@class="card-header"]//a/@href').get('').strip()
            # }
            # link = post.xpath('.//header[@class="card-header"]//a/@href').get('').strip()

            
    
    def parse_job_posting(self, response):
        results = json.loads(response.body)
        # pprint(results)
        
        description = get_html_text(results['jobDescription'])
        # yield {
        #     # 'description' : description,
        #     'company' : results['companyInfo']['name'],
        #     # 'loc' : 'jobDescription',
        #     'info' : results['summary']['info'][1]['text'],
        #     'id' : results['jobId']
        # }
        
        details = {}

        details['jobId'] = results['jobId']

        try:
            details['title'] = results['companyInfo']['companyHeader']
        except:
            details['title'] = None

        details['description'] = description

        try:    
            details['company'] = results['companyInfo']['name']
        except:
            details['company'] = None
        
        try:
            details['location'] = results['companyInfo']['jobLocation']
        except:
            details['location'] = None
        
        try:
            info = results['summary']['info']
            for i in info:
                details[i['title']] = i['text']
        except:
            None
        
        details['scrape_date'] = datetime.now()

        try:
            details['category'] = results['jobCategory']
        except:
            details['category'] = None
        # details['search_location'] = location
        # details['search_title'] = title
        return details

