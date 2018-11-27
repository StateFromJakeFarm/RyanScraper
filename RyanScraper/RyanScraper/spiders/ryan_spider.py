import scrapy
import logging

from scrapy.spiders import CrawlSpider
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from bs4 import BeautifulSoup
from .helper import *

class RyanSpider(CrawlSpider):
    # Ryan is an Internet arachnid
    name = 'Ryan'

    def __init__(self, teams='', year=2017):
        # Teams to search for (passed with -a option on cmd line)
        self.teams = teams.split(',')

        # Year we're interested in
        self.year = str(year)

        # Regex to find team pages for our year
        self.year_regex = re.compile('teams\/[a-z]{3}\/' + self.year + '.htm')

        self.team_page_fields = [
            'points',
            'points_opp',
            'points_diff'
        ]

        # Landing page
        self.base_url = 'https://www.pro-football-reference.com'

        # Store data in dictionary before it's written to a file
        self.data = {}

        # Write data on spider close
        dispatcher.connect(self.write_data, signals.spider_closed)

    def write_data(self, spider):
        print(self.data)

    def start_requests(self):
        yield scrapy.Request(url=self.base_url + '/teams', callback=self.get_team_pages)
        yield scrapy.Request(url=self.base_url + '/years/{}/opp.htm'.format(self.year), callback=self.parse_opp_def_page)

    def get_team_pages(self, response):
        '''
        Submit request for each team we're interested in.
        '''
        soup = BeautifulSoup(response.body, 'lxml')

        # Get links to team pages
        team_regex = re.compile(build_regex_or(self.teams))
        for a in soup.find_all('a', text=team_regex):
            # Team's base page has some basic stats not available from
            # more detailed view
            team_url = self.base_url + a['href']
            yield scrapy.Request(url=team_url, callback=self.parse_team_page,
                meta={'team': a.text})

    def parse_team_page(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        team = response.meta.get('team')

        for a in soup.find_all('a', href=self.year_regex):
            tr = a.parent.parent

            for field in self.team_page_fields:
                value = get_data_stat(tr, field).text
                add_to_row(self.data, team, field, value)

    def parse_opp_def_page(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
