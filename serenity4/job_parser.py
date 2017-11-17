import time
from random import randint

from lxml import html
from requests import Request, Session
from config import jobs_per_page

class JobsFetch:
    
    def __init__ (self,search_terms,search_terms_excluded,search_locations,search_engines):

        self.search_terms = search_terms
        self.search_terms_excluded = search_terms_excluded
        self.search_locations = search_locations
        self.search_engines = search_engines
        self.result_limit = jobs_per_page
        self.job_list = []

    def run_parsers(self):
        self.parsers = {'Indeed.fr': IndeedScraper,
                        'Linkedin.fr' : LinkedinScraper}

        for site in self.search_engines:
            instance = self.parsers[site](
                self.search_terms,
                self.search_terms_excluded,
                self.search_locations,
                self.result_limit
                )
            [self.job_list.append(job) for job in instance.results()]

    def results(self):
        self.run_parsers()
        return self.job_list

class Job:

    def validate_result(self, result):
        if not result:
            return "No data found"
        else:
            return result

    def __init__(self, title, company, location, description, link, search_term, source):
        self.title = self.validate_result(title)
        self.company = self.validate_result(company)
        self.location = self.validate_result(location)
        self.description = self.validate_result(description)
        self.link = self.validate_result(link)
        self.search_term = self.validate_result(search_term)
        self.source = self.validate_result(source)

class JobParser:

    def __init__(self,search_terms,search_terms_excluded,search_locations,result_limit):

        self.search_terms = search_terms
        self.search_terms_excluded = search_terms_excluded
        self.search_locations = search_locations
        self.result_limit = result_limit

    def format_query(self, query):
        '''Prepares the query by replacing spaces with + symbol'''
        search_term_formatted = []
        search_term_formatted = [w.replace(" ", "+") for w in query]
        return search_term_formatted
               
class IndeedScraper (JobParser):
    
    def __init__(self, search_terms, search_terms_excluded, search_locations,result_limit):
        super().__init__(search_terms, search_terms_excluded, search_locations,result_limit)

    def send_request(self, search_term, search_term_exclude, location, start):
        ''' Prepares and sends the request
        '''
        session = Session()
        payload = {
            'q': search_term + '+-' + search_term_exclude,
            'l': location,
            'start': start
        }
        request = Request('GET', 'https://www.indeed.fr/emplois', params=payload)
        prepared_req = request.prepare()
        prepared_req.url = (prepared_req.url).replace("%2B", "+")
        page = session.send(prepared_req)

        return page

    def get_jobs(self):
        ''' Parses queries passed to it.
        '''
        compiled_search_term = self.format_query(self.search_terms)
        compiled_search_term_exclude = '+-'.join(self.format_query(self.search_terms_excluded))

        for search_term in compiled_search_term:
            for location in self.search_locations:
                for result_batch in range(0, self.result_limit, 10):
                    request = self.send_request(
                        search_term=search_term,
                        search_term_exclude=compiled_search_term_exclude,
                        location=location,
                        start=result_batch)

                    yield request, search_term

    
    def results(self):
        
        for request, search_term in self.get_jobs():

            tree = html.fromstring(request.content)
            results = tree.xpath('//div[@class="  row  result"]')

            for element in results:
                job_title = element.xpath('.//a[@data-tn-element="jobTitle"]/@title')
                company = element.xpath('normalize-space(.//span[@class="company"]/span/a/text())')
                location = element.xpath('.//span[@class="location"]/span/text()')
                description = element.xpath('normalize-space(.//span[@class="summary"])')
                stub = element.xpath('.//a[@data-tn-element="jobTitle"]/@href')
                link = 'https://www.indeed.fr' + stub[0]
                source = "Indeed.fr"
                search_term = search_term

                job_entry = Job(
                    title=job_title[0],
                    company=company,
                    location=location[0],
                    description=description,
                    link=link,
                    search_term=search_term,
                    source=source)

                yield job_entry

class LinkedinScraper (JobParser):
    
    def __init__(self, search_terms, search_terms_excluded, search_locations,result_limit):
        super().__init__(search_terms, search_terms_excluded, search_locations,result_limit)

    def send_request(self, search_term, search_term_exclude, location, start):
        ''' Prepares and sends the request
        '''
        session = Session()
        payload = {
            'keywords': search_term,
            'location': location,
            'start': start
        }
        request = Request('GET', 'https://www.linkedin.com/jobs/search/', params=payload)
        prepared_req = request.prepare()
        prepared_req.url = (prepared_req.url).replace("%2B", "+")
        page = session.send(prepared_req)

        return page

    def get_jobs(self):
        ''' Parses queries passed to it.
        '''
        compiled_search_term = self.format_query(self.search_terms)
        compiled_search_term_exclude = '+-'.join(self.format_query(self.search_terms_excluded))

        for search_term in compiled_search_term:
            for location in self.search_locations:
                for result_batch in range(0, self.result_limit, 25):
                    request = self.send_request(
                        search_term=search_term,
                        search_term_exclude=compiled_search_term_exclude,
                        location=location,
                        start=result_batch)

                    yield request, search_term

    
    def results(self):
        
        for request, search_term in self.get_jobs():

            tree = html.fromstring(request.content)
            results = tree.xpath('//li[@class="job-listing"]')

            for element in results:
                job_title = element.xpath('normalize-space(.//span[@class="job-title-text"/text())')
                company = element.xpath('normalize-space(.//span[@class="company-name-text"]/text())')
                location = element.xpath('normalize-space(.//span[@class="job-location"]/text())')
                description = element.xpath('normalize-space(.//span[@class="job-description"]/text())')
                link = element.xpath('.//a[@class="job-title-link"]/@href')
                source = "LinkedIn"
                search_term = search_term

                job_entry = Job(
                    title=job_title[0],
                    company=company,
                    location=location[0],
                    description=description,
                    link=link,
                    search_term=search_term,
                    source=source)

                yield job_entry

class GlassdoorScraper (JobParser):
    
    def __init__(self, search_terms, search_terms_excluded, search_locations,result_limit):
        super().__init__(search_terms, search_terms_excluded, search_locations,result_limit)

    def send_request(self, search_term, search_term_exclude, location, start):
        ''' Prepares and sends the request
        '''
        session = Session()
        payload = {
            'keywords': search_term,
            'location': location,
            'start': start
        }
        request = Request('GET', 'https://www.linkedin.com/jobs/search/', params=payload)
        prepared_req = request.prepare()
        prepared_req.url = (prepared_req.url).replace("%2B", "+")
        page = session.send(prepared_req)

        return page

    def get_jobs(self):
        ''' Parses queries passed to it.
        '''
        compiled_search_term = self.format_query(self.search_terms)
        compiled_search_term_exclude = '+-'.join(self.format_query(self.search_terms_excluded))

        for search_term in compiled_search_term:
            for location in self.search_locations:
                for result_batch in range(0, self.result_limit, 25):
                    request = self.send_request(
                        search_term=search_term,
                        search_term_exclude=compiled_search_term_exclude,
                        location=location,
                        start=result_batch)

                    yield request, search_term

    
    def results(self):
        
        for request, search_term in self.get_jobs():

            tree = html.fromstring(request.content)
            results = tree.xpath('//li[@class="job-listing"]')

            for element in results:
                job_title = element.xpath('normalize-space(.//span[@class="job-title-text"/text())')
                company = element.xpath('normalize-space(.//span[@class="company-name-text"]/text())')
                location = element.xpath('normalize-space(.//span[@class="job-location"]/text())')
                description = element.xpath('normalize-space(.//span[@class="job-description"]/text())')
                link = element.xpath('.//a[@class="job-title-link"]/@href')
                source = "LinkedIn"
                search_term = search_term

                job_entry = Job(
                    title=job_title[0],
                    company=company,
                    location=location[0],
                    description=description,
                    link=link,
                    search_term=search_term,
                    source=source)

                yield job_entry

#