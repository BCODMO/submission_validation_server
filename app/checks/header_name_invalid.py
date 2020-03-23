from goodtables import check
import re

# Module API

@check('header-name-invalid', type='custom', context='head')
class HeaderNameInvalid(object):

    # Public
    def __init__(self, **options):
        pass


    def check_headers(self, errors, cells, sample=None):

        for cell in cells:

            # Skip if not header
            if 'header' not in cell or not cell['header']:
                continue

            header_string = cell['header']

            if header_string[0].isdigit():
                message = f'Column {cell["number"]} starts with a number'
                errors.append({
                    'code': 'header-name-invalid',
                    'message': message,
                    'row-number': None,
                    'column-number': cell['number'],
                })


            if not re.match('^[a-zA-Z0-9_]+$', header_string):
                message = f'Column {cell["number"]} contains a character other than numbers, letters, and underscores.'
                errors.append({
                    'code': 'header-name-invalid',
                    'message': message,
                    'row-number': None,
                    'column-number': cell['number'],
                })

        return errors
