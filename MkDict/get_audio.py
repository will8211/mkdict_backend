#!/usr/bin/env python3

import MySQLdb
import os
import requests
from lxml import html

def get_audio(sound_file):

    code = sound_file.replace('.mp3', '')
    if len(code) == 3:
        table = 'Moe_dict'
    else:
        table = 'Dict'


    # Connect to database in SQL

    my_username = os.environ.get("MKDICT_DB_USERNAME", '')
    my_password = os.environ.get("MKDICT_DB_PASSWORD", '')
    
    conn = MySQLdb.connect(host="localhost", user=my_username, passwd=my_password,
                           db='mkdictionary', charset='utf8')
    cursor = conn.cursor()
    SQL = cursor.execute

    SQL("SELECT Id, POJ_numbers FROM " + table + " WHERE BINARY Code=%s", [code])
    data = cursor.fetchone()

    my_id = data[0]
    if len(code) == 3:
        my_id = 'm' + str(my_id)
    poj_string = data[1]

    # Clean up

    cursor.close()
    conn.close()

    # Check if it exists already

    here = os.path.dirname(__file__)
    filename = '%s/audio/%s.mp3' % (here, my_id)
    if os.path.isfile(filename):
        return str(my_id) + ".mp3"

    # Build URL

    poj_string = poj_string.replace('1', '')
    poj_string = poj_string.replace('4', '')
    poj_string = poj_string.replace('oo', 'ou')

    url = 'http://www.taibun.tw/SoundPlayerAction.do?content=' + poj_string

    # Scrape

    try:
        page = requests.get(url, timeout=7)
    except requests.exceptions.ConnectTimeout:
        return "0unavailable.mp3"

    page.encoding = 'utf-8'
    tree = html.fromstring(page.text)
    element = tree.xpath('//source')
    link = element[0].attrib['src']
    mp3 = requests.get(link)
    with open(filename, 'wb') as f:
        f.write(mp3.content)

    return str(my_id) + ".mp3"
