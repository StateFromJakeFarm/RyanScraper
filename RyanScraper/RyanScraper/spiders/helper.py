import re

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
