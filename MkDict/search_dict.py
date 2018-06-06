#!/usr/bin/env python3
#
# Gets users' search terms and returns results for results.html

import MySQLdb
import re
import math
import os

def search_dict(query, roman, page, q_type, t_dict):

    def process_matches(data, matches):
        ''' Makes necessary changes to raw mysql results
            Calls tuple_to_dict() and get_examples()
            Returns processed results and list of ids of matches so far
        '''
        results = []
        for row in data:
            row = tuple_to_dict(row)
            dtc = dt_check(row)
            if (row['Id'] not in matches) and dtc and (row['Type'] == 0):
                row = dtc
                matches.append(row['Id'])
                row['Examples'] = get_examples(row['Id'])
                results.append(row)
        return (results, matches)

    def tuple_to_dict(row):
        ''' Changes mysql row tuples to dictionaries with named keys
        '''
        dict_row = {
            'Id': row[0],
            'Type': row[1],
            'Chinese': row[2],
            'English': row[3].replace("''", "'"),
            'Code': row[13],
            'Tai_char': row[14],
            'POJ': row[4],
            'POJ_numbers': row[10],
            'TRS': row[5],
            'TRS_numbers': row[11],
            'DT': row[6],
            'DT_numbers': row[12]}

        return dict_row

    def get_examples(my_id):
        ''' Checks if row of given id has any subheadings and adds them
        '''
        examples = True
        my_list = []
        my_id += 1
        while examples:
            SQL("SELECT * FROM " + table + " WHERE id= %s", (my_id,))
            row = cursor.fetchone()
            if row == None:
                return my_list
            row = tuple_to_dict(row)
            if row['Type'] == 1:
                my_id += 1
                dtc = dt_check(row)
                if dtc:
                    row = dtc
                    my_list.append(row)
            else:
                examples = False
        return my_list

    def dt_check(row):
        ''' Returns False is it's a DT search and DT is blank
        '''
        if roman == 'd' and row['DT'] == '':
            return False
        elif roman != 'd' and row['DT'] == '':
            row['DT'] = '(DT unavailable)'
            return row
        else:
            return row

    def diacritics_to_numbers(q, roman):
        '''Takes queries with diacritics and changes them to numbers
        '''

        acutes = '[\u0301\u00c0\u00c8\u00cc\u00d2\u00d9\u00e0\u00e8\u00ec\u00f2\u00f9]'
        graves = '[\u0300\u00c1\u00c9\u00cd\u00d3\u00da\u00e1\u00e9\u00ed\u00f3\u00fa]'
        circum = '[\u0302\u00c2\u00da\u00ce\u00d4\u00db\u00e2\u00ea\u00ee\u00f4\u00fb]'
        line_a = '[\u0304\u0100\u0112\u012a\u014c\u016a\u0101\u0113\u012b\u014d\u016b]'
        vertic = '[\u030d]'
        dcaron = '[\u030c\u01cd\u011a\u01cf\u01d1\u01d3\u01cE\u011b\u01d0\u01d2\u01d4]'

        if roman == 'd':
            a, g, c, l, v, d = '9', '2', '3', '47', '', '5'
        else:
            a, g, c, l, v, d = '2', '3', '5', '7', '8', ''

        q = re.sub('(\w*' + acutes + '\w*)', '\g<1>' + a, q)
        q = re.sub('(\w*' + graves + '\w*)', '\g<1>' + g, q)
        q = re.sub('(\w*' + circum + '\w*)', '\g<1>' + c, q)
        q = re.sub('(\w*' + line_a + '\w*)', '\g<1>' + l, q)
        q = re.sub('(\w*' + vertic + '\w*)', '\g<1>' + v, q)
        q = re.sub('(\w*' + dcaron + '\w*)', '\g<1>' + d, q)

        #Disambiguate tones 4/7 for DT

        if roman == 'd':
            q = re.sub('gh47', 'gh7', q)
            q = re.sub('([ptkh])47', '\g<1>4', q)
            q = re.sub('47', '7', q)

        #Unmarked tones

        start = r'(^|[-\s\(])'
        end = r'([-\s\)\*\.\?,]|$)'

        q = re.sub(start + r'([a-zA-Z]+gh)' + end, '\g<1>\g<2>1\g<3>', q)
        if roman == 'd':
            q = re.sub(start + r'([a-zA-Z]+[ptkh])' + end, '\g<1>\g<2>8\g<3>', q)
        else:
            q = re.sub(start + r'([a-zA-Z]+[ptkh])' + end, '\g<1>\g<2>4\g<3>', q)
        q = re.sub(start + r'([a-zA-Z]+)' + end, '\g<1>\g<2>1\g<3>', q)

        combining = "[\u0301\u0300\u0302\u0304\u030d\u030c]"
        q = re.sub(combining, '', q)

        return q

    # Connect to database in SQL

    my_username = os.environ.get("MKDICT_DB_USERNAME", '')
    my_password = os.environ.get("MKDICT_DB_PASSWORD", '')
    
    conn = MySQLdb.connect(host="localhost", user=my_username, passwd=my_password,
                           db='mkdictionary', charset='utf8')
    cursor = conn.cursor()
    SQL = cursor.execute

    # Clean up query

    query = query.replace('ⁿ', 'nn')
    query = query.replace('·', 'o')
    query = query.replace('\u0358', 'o')
    #query = re.sub(r'[1-9]', r'', query)

    # Set dictionary

    if t_dict == 'moe':
        table = 'Moe_dict'
    else:
        table = 'Dict'

    # Figure out search type

    matches = []
    diacritics = "[\u00c0\u00c1\u00c2\u0100\u00c8\u00c9\u00da\u0112" + \
                  "\u00cc\u00cd\u00ce\u012a\u00d2\u00d3\u00d4\u014c" + \
                  "\u00d9\u00da\u00db\u016a\u00e0\u00e1\u00e2\u0101" + \
                  "\u00e8\u00e9\u00ea\u0113\u00ec\u00ed\u00ee\u012b" + \
                  "\u00f2\u00f3\u00f4\u014d\u00f9\u00fa\u00fb\u016b" + \
                  "\u030c\u01cd\u011a\u01cf\u01d1\u01d3\u01ce\u011b" + \
                  "\u01d0\u01d2\u01d4\u0301\u0300\u0302\u0304\u030d]"

    if q_type == 'en':
        column = 'English'
    elif q_type == 'ma':
        column = 'Chinese'
    else:
        if roman == 't':
            column = 'TRS_numbers'
        elif roman == 'd':
            column = 'DT_numbers'
        else:
            column = 'POJ_numbers'

        if re.search(r'[0-9]', query):
            pass
        elif re.search(diacritics, query):
            query = diacritics_to_numbers(query, roman)
        else:
            if roman == 't':
                column = 'TRS_search'
            elif roman == 'd':
                column = 'DT_search'
            else:
                column = 'POJ_search'

    # Wildcard search

    if ('*' in query) or ('?' in query) or ('"' in query):
        mod_query = query.replace('?', '.')
        mod_query = mod_query.replace('*', '.*')
        mod_query = mod_query.replace('"', '')
        mod_query = '^' + mod_query + '$'
        SQL("""
            SELECT * FROM """ + table + """
            WHERE """ + column + """ REGEXP %s LIMIT 1000
            """, [mod_query])
        data = cursor.fetchall()
        results, matches = process_matches(data, matches)

    else:

        # 1-Exact matches

        SQL("""
            SELECT * FROM """ + table + """
            WHERE """ + column + """= %s  LIMIT 1000
            """, [query])

        data = cursor.fetchall()
        (results_1, matches) = process_matches(data, matches)

        # 2-Exact matches followed by first comma

        SQL("""
            SELECT * FROM """ + table + """
            WHERE """ + column + """ LIKE %s  LIMIT 1000
            """, [query + ',%'])

        data = cursor.fetchall()
        (results_2, matches) = process_matches(data, matches)

        # 2B-Exact matches after last comma

        SQL("""
            SELECT * FROM """ + table + """
            WHERE """ + column + """ LIKE %s  LIMIT 1000
            """, ['%, ' + query])

        data = cursor.fetchall()
        (results_2B, matches) = process_matches(data, matches)

        # 3-All other fulltext matches

        results_3 = []
        if column == "English":
            if query == '':
                s_query = '""'
            else:
                s_query = query
            SQL("""
                SELECT * FROM """ + table + """ WHERE id IN (
                    SELECT id FROM """ + table + """_sphinx WHERE query=%s
                )
                """, [s_query + ';limit=1000'])

        else:
            SQL("""
                SELECT * FROM """ + table + """
                WHERE """ + column + """ LIKE %s  LIMIT 1000
                """, ['%' + query + '%'])

        data = cursor.fetchall()
        (results_3, matches) = process_matches(data, matches)
        #results_3.sort(key=lambda result: len(result['POJ'])) #Sort by length

        # Put them all together

        results = results_1 + results_2 + results_2B + results_3

    '''
    # Split up Mandarin section and adds links to holodict

    for i, row in enumerate(results):

        #Add links for Mandarin

        han = r'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]'

        a = '<a target="_blank" href="http://twblg.dict.edu.tw/holodict_new/' \
                'result.jsp?radiobutton=0&limit=20&querytarget=2&sample='

        b = '" title="Click to search in Chinese-Taiwanese dictionary. ' \
                'Includes pronunciation.">'

        c = '</a>'

        row['Chinese'] = re.sub('(%s+)' % han, r'%s\1%s\1%s' % (a, b, c),
                                row['Chinese'])

        #Commit list changes

        results[i] = row
    '''
    # Close connection

    cursor.close()
    conn.close()

    # Account for empty results

    if len(results) == 0:
        if roman == 'd':
            message = 'No matches! Try searching using a romanization other than DT.'
        else:
            message = 'No matches!'
        results = [{
            'Id': 0,
            'Type': '',
            'Chinese': '',
            'English': '',
            'Tai_char': None,
            'POJ': message,
            'POJ_numbers': '',
            'TRS': message,
            'TRS_numbers': '',
            'DT': message,
            'DT_numbers': ''
            }]

    # Divide into pages of 50 results

    import flask

    if len(results) > 1000:
        results = results[:1000]

    total_pages = int(math.ceil(len(results)/50))

    for i in range(total_pages):

        p = i+1
        page_results = results[p*50-50:p*50]
        try:
            results_url = flask.url_for('results')
        except RuntimeError:
            # for debugging
            results_url = "/results/"

        page_links = ''

        if total_pages < 2 or p > total_pages:
            page_links = ''
        else:
            page_links += 'Results pages: '
            if p > 1:
                page_links += (' <a href="%s?roman=%s&query=%s&page=%d&q_type=%s&t_dict=%s">Prev</a> '
                                % (results_url, roman, query, p-1, q_type, t_dict))
            for i in range(1, p):
                page_links += (' <a href="%s?roman=%s&query=%s&page=%d&q_type=%s&t_dict=%s">%d</a> '
                                % (results_url, roman, query, i, q_type, t_dict, i))
            page_links += page
            for i in range(p+1, total_pages+1):
                page_links += (' <a href="%s?roman=%s&query=%s&page=%d&q_type=%s&t_dict=%s">%d</a> '
                                % (results_url, roman, query, i, q_type, t_dict, i))
            if p != total_pages:
                page_links += (' <a href="%s?roman=%s&query=%s&page=%d&q_type=%s&t_dict=%s">Next</a> '
                                % (results_url, roman, query, p+1, q_type, t_dict))

        # Save results to cache

        try:
            from MkDict import APP
            cache_key = (query, roman, str(p), q_type)
            APP.cache[cache_key] = (page_results, page_links)
            try:
                APP.cache_list.remove(cache_key)
            except (ValueError, ImportError):
                pass
            APP.cache_list.append(cache_key)
            while len(APP.cache_list) > 50:
                del APP.cache[APP.cache_list[0]]
                APP.cache_list = APP.cache_list[1:]
        except (ImportError, AttributeError):
            pass

        # Mark currently querried page to send to user

        if p == int(page):
            this_page_results = page_results
            this_page_links = page_links

    # Send it on

    return this_page_results, this_page_links

if __name__ == "__main__":

    # For troubleshooting (only executes when script is run directly).

    from pprint import pprint
    while True:
        query = input("Type English word to search: ")
        if query in ('exit', 'q', 'quit'):
            break
        from time import time
        start = time()
        res = search_dict(query, 'p', '1', 'tw', 'mk')[0]
        #print(res)
        print('It took: ' + str(time() - start) + ' seconds.')
