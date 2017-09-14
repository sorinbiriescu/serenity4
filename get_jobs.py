#to fetch data
from requests import Request, Session
from bs4 import BeautifulSoup

from sqlalchemy import and_

#to find similar entries
import re

#to increase the time between requests
import time

#to insert the current time in db
from datetime import datetime

#to pause the request to not overload the server
from random import randint

#import db connection
from serenity4 import db
from serenity4.models import Jobs

#create empty dataframe. will be used later on to concatenate the results
columns = ['Title','Company','Location','Short Description','Link','Search Term','Source']

#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
#request headers
headers = {'User-Agent': 'Chrome/39.0.2171.95'}

#parser for indeed.fr. Accepts a soup
def indeed_jobs_parser(soup,query):

    data_error = 'Not found'
    for item in soup.find_all(name='div', attrs={'class':re.compile('.*row.*')}):

        #create an empty list. will be populated later with results and appended to the dataframe
        job_item = dict.fromkeys(columns)

        #get the job title
        for a in item.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
            try:
                job_item['Title'] = a['title']
            except:
                job_item['Title'] = data_error

        #get the name of the company
        for span in item.find_all(name='span', attrs={'itemprop':'name'}):
            try:
                job_item['Company'] = span.a.text.strip()
            except AttributeError:
                job_item['Company'] = span.text.strip()
            else:
                job_item['Company'] = data_error


        #get the city of the job
        for span in item.find_all(name='span', attrs={'itemprop':'addressLocality'}):
            try:
                job_item['Location'] = span.a.text.strip()
            except AttributeError:
                job_item['Location'] = span.text.strip()
            else:
                job_item['Location'] = data_error

        #get the summary of the job
        for span in item.find_all(name='span', attrs={'class':'summary'}):
            try:
                job_item['Short Description'] = span.text.strip()
            except:
                job_item['Short Description'] = data_error

        #get the link of the job
        for a in item.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
            try:
                link = 'https://www.indeed.fr'+a['href']
                job_item['Link'] = link
            except:
                job_item['Link'] = data_error

        job_item['Search Term'] = query

        job_item['Source'] = 'Indeed.fr'

        if not Jobs.query.filter(and_(Jobs.title==job_item['Title'],
                                        Jobs.description==job_item['Short Description'])).first():

            db.session.add(Jobs(title=job_item['Title'],
                                company=job_item['Company'],
                                location=job_item['Location'],
                                description=job_item['Short Description'],
                                link=job_item['Link'],
                                search_term=(job_item['Search Term']).replace("+"," ").title(),
                                source=job_item['Source']))

            db.session.commit()
        else:
            duplicate = Jobs.query.filter(and_(Jobs.title==job_item['Title'],
                                        Jobs.description==job_item['Short Description'])).first()
            duplicate.discovery_count += 1
            duplicate.last_date_found = datetime.utcnow()
            db.session.commit()

    return True

#how many results
indeed_max_results = 20

s = Session()

#queries to be used.
#remember that you need to use + for spaces, the queries are used to compose the URL
queries = ['assistant+bilingue','assistant+evenementiel','assistant+marketing','marketing+operationnel','marketing+junior','english','marketing','event+assistant']

#terms to exclude
exclude = ['alternance','stage','internship','stagiaire']

indeed_compiled_exclude = '+-'.join(exclude)

#iterates over the queries and fetches the pages. uses the parser on them and concatenates the results in the main dataframe
for query in queries:
    for result_batch in range (0,indeed_max_results,10):
        payload = {'q':query+'+-'+indeed_compiled_exclude,'l':'Lyon','start':result_batch}
        request = Request('GET','https://www.indeed.fr/emplois',params=payload)
        prepared_req = request.prepare()
        prepared_req.url = (prepared_req.url).replace("%2B", "+")
        page = s.send(prepared_req)

        #1 second between requests
        time.sleep(randint(0, 9))

        soup = BeautifulSoup(page.content, 'lxml')
        indeed_jobs_parser(soup,query)
