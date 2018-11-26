import scrapy
import logging
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider
from .helper import *

class RyanSpider(CrawlSpider):
    # Ryan is an Internet arachnid
    name = 'Ryan'

    def __init__(self, teams='', earliest_year=1989):
        # Teams to search for (passed with -a option on cmd line)
        self.teams = teams.split(',')

        # Earliest year for which we want data
        self.earliest_year = earliest_year

        self.base_url = 'https://www.pro-football-reference.com'

    def start_requests(self):
        # We will start on the base team page
        yield scrapy.Request(url=self.base_url + '/teams', callback=self.get_team_links)

    def get_team_links(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        # Get links for teams we're interested in
        team_regex = re.compile(build_regex_or(self.teams))
        for a in soup.find_all('a', text=team_regex):
            yield scrapy.Request(url=base_url + a['href'], callback=self.get_team_data)

    def get_team_data(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
