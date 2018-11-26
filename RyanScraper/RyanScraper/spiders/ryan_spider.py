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

        # Current year
        self.cur_year = datetime.now().year

        # Earliest year for which we want data
        self.earliest_year = int(earliest_year)

        # Landing page
        self.base_url = 'https://www.pro-football-reference.com'

        # Make regex for years we're interested in (this will be used a lot)
        years = [str(y + self.earliest_year) for y in
            range(self.cur_year - self.earliest_year + 1)]
        self.year_regex = re.compile(build_regex_or(years))

        # Store data in dictionary before it's written to a file
        self.data = {}
        for team in self.teams:
            self.data[team] = {}
            for year in years:
                self.data[team][year] = {}

    def start_requests(self):
        # We will start on the base team page
        yield scrapy.Request(url=self.base_url + '/teams', callback=self.parse)

    def parse(self, response):
        '''
        Submit request for each team we're interested in.
        '''
        soup = BeautifulSoup(response.body, 'lxml')

        # Find only the teams we're interested in
        team_regex = re.compile(build_regex_or(self.teams))
        for a in soup.find_all('a', text=team_regex):
            # Team's base page has some basic stats not available from
            # more detailed view
            team_url = self.base_url + a['href']
            yield scrapy.Request(url=team_url, callback=self.get_basic_data,
                meta={'team': a.text})

    def get_basic_data(self, response):
        soup = BeautifulSoup(response.body, 'lxml')

        team = response.meta.get('team')

        for a in soup.find_all('a', text=self.year_regex):
            year = a.text
            tr = a.parent.parent

            # Log basic data
            total_games = 0
            for field in ['wins', 'losses', 'ties']:
                try:
                    value = get_data_stat(tr, field).text
                except AttributeError:
                    continue
                total_games += int(value)
                add_to_row(self.data, team, year, field, value)

            if total_games == 0:
                continue

            # Get win %
            add_to_row(self.data, team, year, 'win %',
                str(int(self.data[team][year]['wins']) / total_games * 100))

            # Submit request for this year's detailed stats
            detailed_url = response.url + year + '.htm'
            yield scrapy.Request(url=detailed_url, callback=self.get_detailed_data,
                meta={'team': team, 'year': year})


    def get_detailed_data(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
