#!/usr/bin/env python3

import MySQLdb
import os
import re

def search_examples(head_id, roman, t_dict):

    def tuple_to_dict(row):
        ''' Changes mysql row tuples to dictionaries with named keys 
        '''
        dict_row = {
            'Id':row[0],
            'Type':row[1],
            'Chinese':row[2],
            'English':row[3].replace("''", "'"),
            'Code':row[13],
            'Tai_char':row[14]}
        if roman == 't':
            dict_row['Tai'] = row[5]
            dict_row['Tai_numbers'] = row[11]
        elif roman == 'd':
            dict_row['Tai'] = row[6]
            dict_row['Tai_numbers'] = row[12]
        else:
            dict_row['Tai'] = row[4]
            dict_row['Tai_numbers'] = row[10]
        return dict_row
    
    # Connect to database in SQL

    my_username = os.environ.get("MKDICT_DB_USERNAME", '')
    my_password = os.environ.get("MKDICT_DB_PASSWORD", '')
    
    conn = MySQLdb.connect(host="localhost", user=my_username, passwd=my_password,
                           db='mkdictionary', charset='utf8')
    cursor = conn.cursor()
    SQL = cursor.execute

    # Get examples
    
    if t_dict == 'moe':
        table = 'Moe_dict'
    else:
        table = 'Dict'
    
    examples = True
    results = []
    my_id = int(head_id) + 1
    while examples:
        SQL("SELECT * FROM " + table + " WHERE id= %s", (my_id,))
        row = cursor.fetchone()
        row = tuple_to_dict(row)
        if row['Type'] == 1:
            my_id += 1
            if row['Tai'] != '':
                results.append(row)
        else:
            examples = False

    # Close connection

    cursor.close()
    conn.close()

    # Send it on

    return results
