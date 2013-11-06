class Configuration(object):
	# PostgreSQL settings
	DATABASE = {
		'engine': 'peewee.PostgresqlDatabase',
		'name': "protodb",
		'user': "bp2013h1",
		'password': "hirsch",
		'host': "172.16.22.247",
		'port': "5432",
	}
	DEBUG = True
	SECRET_KEY = 'bp2013h1'