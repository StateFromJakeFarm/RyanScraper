import re

from bs4 import BeautifulSoup

def build_regex_or(strings, file_extension=False):
    '''Return a regex that matches any strings in a given list'''
    regex = ''
    letter_re = re.compile('[A-Z]|[a-z]')
    for i, string in enumerate(strings):
        string = re.escape(string)

        if i > 0:
            regex += '|'

        regex += '('
        if file_extension:
            regex += '\.' + string + '$)'
        else:
            regex += string + ')'

    return regex

def get_data_stat(dom_obj, data_stat):
    for d in dom_obj.find_all('td', attrs={'data-stat': data_stat}):
        return d

def add_to_row(data_dict, team, field, value):
    if team not in data_dict:
        data_dict[team] = {}

    data_dict[team][field] = value
