#%%
import time
from random import randint
from lxml import html
from requests import Request, Session

class JobElement:
    ''' Creates an object with the results of the query.
    **************
    Required attributes:
    -----
    title = String
    company = String
    location = String
    description = String
    link = String
    search_term = String
    source  = String
     '''
    def validate_result(self, result):
        ''' Validates the class attributes before instancing the class'''
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

    def __repr__(self):
        return '%s,%s,%s,%s,%s,%s,%s' % (
            self.title,
            self.company,
            self.location,
            self.description,
            self.link,
            self.search_term,
            self.source
            )

class IndeedParser:
    ''' Creates object to parse queries
    **************
    Required attributes:
    -----
    search_terms = List \n
    search_terms_excluded = List \n
    search_locations = List \n
    result_limit = Integer \n
    ****** ********
    Methods:
    -----
    format_query(self, query) \n
    send_request(self, search_term, search_term_exclude, location, start)
    '''
    def __init__(self, **kwargs):
        self.search_terms = kwargs['search_terms']
        self.search_terms_excluded = kwargs['search_terms_excluded']
        self.search_locations = kwargs['search_locations']
        self.result_limit = kwargs['result_limit']

    def format_query(self, query):
        '''Prepares the query by replacing spaces with + symbol'''
        search_term_formatted = []
        search_term_formatted = [w.replace(" ", "+") for w in query]
        return search_term_formatted

    def send_request(self, search_term, search_term_exclude, location, start):
        ''' Prepares and sends the request.abs
        **************
        1. Itilialize session
        2. Create payload with URL parameters
        3. prepares the request by replacing "%2B" with "+"
        4. Sends the request
        5. Returns the result object
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

    def parse_queries(self):
        ''' Parses queries passed to it.
        IndeedParser needs to be initialised to call this method.
        **************
        1. Prepares search temrs and excluded search terms by calling the
        format_query methon on them (replaces spaces with +)
        2. Iterates over the list of search terms
        3. Sends the request (with a call to send_request method) and stores the result
        4. Extracts the relevant info from the result and concatenates the results
        in a list
        5. Returns the list
        '''
        compiled_search_term = self.format_query(self.search_terms)
        compiled_search_term_exclude = '+-'.join(self.format_query(self.search_terms_excluded))
        job_list = []
        for search_term in compiled_search_term:
            for location in self.search_locations:
                for result_batch in range(0, self.result_limit, 10):
                    request = self.send_request(
                        search_term=search_term,
                        search_term_exclude=compiled_search_term_exclude,
                        location=location,
                        start=result_batch)
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

                        job_entry = JobElement(
                            title=job_title[0],
                            company=company,
                            location=location[0],
                            description=description,
                            link=link,
                            search_term=search_term,
                            source=source)
                        job_list.append(job_entry)

        time.sleep(randint(0, 9))
        return job_list
