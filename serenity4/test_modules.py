import pytest
from serenity4.job_parser import JobsFetch

def test_IndeedParser():
    query = JobsFetch(
                search_terms = ['Marketing'],
                search_terms_excluded = ['test'],
                search_locations = ['Lyon'],
                search_engines = ['Indeed.fr']
                ).results()
    assert len(query) > 0

def test_LinkedinParser():
    pytest.xfail('Linkedin parser bugged')
    query = JobsFetch(
                search_terms = ['Marketing'],
                search_terms_excluded = ['test'],
                search_locations = ['Lyon'],
                search_engines = ['Linkedin.fr']
                ).results()
    assert len(query) > 0

def test_FranceEmploiParser():
    pytest.xfail('FranceEmploi parser not installed')
    query = JobsFetch(
                search_terms = ['Marketing'],
                search_terms_excluded = ['test'],
                search_locations = ['Lyon'],
                search_engines = ['Linkedin.fr']
                ).results()
    assert len(query) > 0
