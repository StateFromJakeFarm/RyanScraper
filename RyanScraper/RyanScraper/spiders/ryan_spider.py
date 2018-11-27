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

    def __init__(self, teams='', year=2017, csv_file_path=''):
        '''
        Build-a-Ryan.
        '''
        # Teams to search for (passed with -a option on cmd line)
        if teams != '':
            self.teams = teams.split(',')
        else:
            self.teams = [
                'Arizona Cardinals',
                'Atlanta Falcons',
                'Baltimore Ravens',
                'Buffalo Bills',
                'Carolina Panthers',
                'Chicago Bears',
                'Cincinnati Bengals',
                'Cleveland Browns',
                'Dallas Cowboys',
                'Denver Broncos',
                'Detroit Lions',
                'Green Bay Packers',
                'Houston Texans',
                'Indianapolis Colts',
                'Jacksonville Jaguars',
                'Kansas City Chiefs',
                'Miami Dolphins',
                'Minnesota Vikings',
                'New England Patriots',
                'New Orleans Saints',
                'New York Giants',
                'New York Jets',
                'Oakland Raiders',
                'Philadelphia Eagles',
                'Pittsburgh Steelers',
                'Los Angeles Rams',
                'Los Angeles Chargers',
                'San Francisco 49ers',
                'Seattle Seahawks',
                'Tampa Bay Buccaneers',
                'Tennessee Titans',
                'Washington Redskins'
            ]

        # Year we're interested in
        self.year = str(year)

        self.csv_file_path = csv_file_path
        if csv_file_path == '':
            self.csv_file_path = self.year + '.csv'

        # Regex to match all teams
        self.team_regex = re.compile(build_regex_or(self.teams))

        # Regex to find team pages for our year
        self.year_regex = re.compile('teams\/[a-z]{3}\/' + self.year + '.htm')

        # Store data in dictionary before it's written to a file
        self.data_dict = {}
        for team in self.teams:
            self.data_dict[team] = {}
            self.data_dict[team]['team'] = team


        # Fields on team-specific page
        self.team_page_fields = [
            'points',
            'points_opp',
            'points_diff'
        ]

        # Fields on opposition and defensive page
        self.opp_def_page_fields = [
            'points',
            'total_yards',
            'plays_offense',
            'fumbles_lost',
            'pass_att',
            'pass_cmp',
            'turnover_pct',
            'exp_pts_def_tot',
            'penalties_yds'
        ]

        self.csv_header_fields = ['team'] + self.team_page_fields + \
            self.opp_def_page_fields

        # Landing page
        self.base_url = 'https://www.pro-football-reference.com'

        # Write data on spider close
        dispatcher.connect(self.write_data, signals.spider_closed)

    def write_data(self, spider):
        '''
        Write data from our dictionary to a CSV file.
        '''
        write_to_csv(self.data_dict, self.csv_file_path, self.csv_header_fields)

    def start_requests(self):
        '''
        Start requests off by visiting generic teams page and the opposition and defensive
        stats page for the year we care about.
        '''
        yield scrapy.Request(url=self.base_url + '/years/{}/opp.htm'.format(self.year),
            callback=self.parse_opp_def_page)
        yield scrapy.Request(url=self.base_url + '/teams', callback=self.get_team_pages)

    def get_team_pages(self, response):
        '''
        Submit request for each team we're interested in.
        '''
        soup = BeautifulSoup(response.body, 'lxml')

        # Get links to team pages
        for a in soup.find_all('a', text=self.team_regex):
            # Team's base page has some basic stats not available from
            # more detailed view
            team_url = self.base_url + a['href']
            yield scrapy.Request(url=team_url, callback=self.parse_team_page,
                meta={'team': a.text})

    def parse_team_page(self, response):
        '''
        Get data from a team's page.
        '''
        soup = BeautifulSoup(response.body, 'lxml')

        team = response.meta.get('team')

        for a in soup.find_all('a', href=self.year_regex):
            tr = a.parent.parent

            for field in self.team_page_fields:
                value = get_data_stat(tr, field).text
                add_to_row(self.data_dict, team, field, value)

    def parse_opp_def_page(self, response):
        '''
        Get data from the opposition and defensive stats page.
        '''
        soup = BeautifulSoup(response.body, 'lxml')

        for a in soup.find_all('a', text=self.team_regex):
            team = a.text
            tr = a.parent.parent

            for field in self.opp_def_page_fields:
                try:
                    value = get_data_stat(tr, field).text
                    add_to_row(self.data_dict, team, field, value)
                except:
                    logging.warn('get_data_stat() failed for team = {} and field = {}'.format(
                        team, field))
