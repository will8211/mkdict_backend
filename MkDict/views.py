#!/usr/bin/env python3

from MkDict import APP
import flask
from MkDict.search_dict import search_dict
from MkDict.search_examples import search_examples
from MkDict.get_audio import get_audio

@APP.route('/')
def search():
    """ Displays a simple search page at '/'
    """
    return flask.render_template('search.html')

@APP.route('/results')
def results():
    """ Displays the results of the search query
    """
    GET = flask.request.args.get
    roman = GET('roman')
    query = GET('query')
    page = GET('page')
    q_type = GET('q_type')
    t_dict = GET('t_dict')
        
    try:
        cached = APP.cache[(query, roman, page, q_type, t_dict)]
        results = cached[0]
        links = cached[1]
    except KeyError:
        results, links = search_dict(query, roman, page, q_type, t_dict)
        
    return flask.render_template('results.html', query=query, roman=roman, 
                                 page=page, q_type=q_type, t_dict=t_dict, 
                                 results=results, links=links)

@APP.route('/examples')
def examples():
    """ Displays phrases and combinations using the headword
    """
    GET = flask.request.args.get
    roman = GET('roman')
    head_id = GET('head_id')
    t_dict = GET('t_dict')
    headword = GET('headword')
    referring_page = GET('referring_page')
    results = search_examples(head_id, roman, t_dict)
    return flask.render_template('examples.html', roman=roman, t_dict=t_dict, 
                                 headword=headword, results=results, 
                                 referring_page=referring_page)

@APP.route('/audio/<sound_file>')
def audio(sound_file):
    """ Serves audio files
    """
    real_name = get_audio(sound_file)
    path_to_file = "audio/" + real_name
    return flask.send_file(path_to_file, 
                           mimetype="audio/mpeg", 
                           as_attachment=True, 
                           attachment_filename=sound_file)

@APP.route('/admin/cache')
def show_cache():
    s = ''
    for n, i in enumerate(APP.cache_list):
        s = s + str(n) + '<br>' + str(i) + '<br>'
    s = s + '<br><br>Contents:<br><br>'
    for k, v in sorted(APP.cache.items()):
        s = s + str(k) + '<br>' # + '<br>' + str(v) + '<br><br>'
    if len(s) == 25:
        s = 'Empty'
    return s

# Favicons

@APP.route('/favicon.ico')
def favicon_1():
    return flask.send_file('static/favicons/favicon.ico', 
                           mimetype='image/vnd.microsoft.icon')

@APP.route('/android-chrome-192x192.png')
def favicon_2():
    return flask.send_file('static/favicons/android-chrome-192x192.png', 
                           mimetype='image/png')

@APP.route('/android-chrome-512x512.png')
def favicon_3():
    return flask.send_file('static/favicons/android-chrome-512x512.png', 
                           mimetype='image/png')

@APP.route('/browserconfig.xml')
def favicon_4():
    return flask.send_file('static/favicons/browserconfig.xml',
                            mimetype='text/xml')

@APP.route('/mstile-150x150.png')
def favicon_5():
    return flask.send_file('static/favicons/mstile-150x150.png',
                            mimetype='image/png')
