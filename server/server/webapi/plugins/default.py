import logging

logger = logging.getLogger('webapi')

def handle_post_data(data):
    logger.debug("Default driver received: " + str(data))
