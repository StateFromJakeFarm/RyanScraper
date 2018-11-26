import scrapy
import logging

from bs4 import BeautifulSoup
from datetime import datetime
from scrapy.spiders import CrawlSpider
from .helper import *

class RyanSpider(CrawlSpider):
    # Ryan is an Internet arachnid
    name = 'Ryan'

    def __init__(self, teams='', earliest_year=1989):
        # Teams to search for (passed with -a option on cmd line)
        self.teams = teams.split(',')

        # Earliest year for which we want data
        self.earliest_year = int(earliest_year)

        self.base_url = 'https://www.pro-football-reference.com'

    def start_requests(self):
        # We will start on the base team page
        yield scrapy.Request(url=self.base_url + '/teams', callback=self.get_team_links)

    def get_team_links(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        # Get links for teams we're interested in
        team_regex = re.compile(build_regex_or(self.teams))
        for a in soup.find_all('a', text=team_regex):
            yield scrapy.Request(url=self.base_url + a['href'], callback=self.get_team_data)

    def get_team_data(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        years = [str(self.earliest_year + y) for y in
            range(datetime.now().year - self.earliest_year + 1)]
        year_regex = re.compile(build_regex_or(years))
        for a in soup.find_all('a', text=year_regex):
            print(a.parent.parent)
