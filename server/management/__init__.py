import sys
import logging

from django.db.models.signals import post_syncdb

from server.management import defaults

logger = logging.getLogger('ecocontrol')

def initialize_defaults(**kwargs):
    # keep in mind that this function can be called multiple times
    defaults.initialize_default_user()
    defaults.initialize_default_scenario()
    defaults.initialize_views()
    defaults.initialize_weathervalues()

post_syncdb.connect(initialize_defaults)