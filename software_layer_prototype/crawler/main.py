#!/usr/bin/env python

from flask import Flask
from flask_peewee.db import Database
from peewee import *

from crawler.thread import Crawler


# instantiate and configure flask instance
app = Flask(__name__)
app.config.from_object('config.Configuration')

# instantiate database wrapper
db = Database(app)