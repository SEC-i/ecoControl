import sys

from django.db.models.signals import post_syncdb

from server.management import defaults


def initialize_defaults(**kwargs):
    defaults.initialize_default_user()
    defaults.initialize_default_scenario()
    defaults.initialize_views()


post_syncdb.connect(initialize_defaults)
