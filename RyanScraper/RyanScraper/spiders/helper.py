import re
import csv

from bs4 import BeautifulSoup

def build_regex_or(strings, file_extension=False):
    '''
    Return a regex that matches any strings in a given list
    '''
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
    '''
    Return a BS4 dom object for the specified "data-stat" value.
    '''
    for d in dom_obj.find_all('td', attrs={'data-stat': data_stat}):
        return d

def add_to_row(data_dict, team, field, value):
    '''
    Add to a team's data row.
    '''
    data_dict[team][field] = value

def write_to_csv(data_dict, csv_file_path, csv_header_fields):
    '''
    Write data from dictionary to CSV.
    '''
    with open(csv_file_path, 'w') as f:
        w = csv.DictWriter(f, fieldnames=csv_header_fields)
        w.writeheader()

        for team in data_dict:
            w.writerow(data_dict[team])
