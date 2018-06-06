#!/usr/bin/env python3

import flask
APP = flask.Flask(__name__)

# Uncomment to make flask.send_file() use apache's mod_xsendfile
#APP.use_x_sendfile = True

import MkDict.views

APP.cache = {}
APP.cache_list = []
