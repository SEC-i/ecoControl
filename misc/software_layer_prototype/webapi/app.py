from flask import Flask

# flask-peewee bindings
from flask_peewee.db import Database

# instantiate and configure flask instance
app = Flask(__name__)
app.config.from_object('config.Configuration')

# instantiate database wrapper
db = Database(app)

