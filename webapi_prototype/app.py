from flask import Flask

# flask-peewee bindings
from flask_peewee.db import Database


app = Flask(__name__)
app.config.from_object('config.Configuration')

db = Database(app)


def create_tables():
    Measurement.create_table()
