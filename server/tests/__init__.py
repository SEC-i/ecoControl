from django.test.runner import DiscoverRunner


class CustomTestSuiteRunner(DiscoverRunner):

    def teardown_databases(self, old_config, **kwargs):
        """
        Don't destroy test database
        """
        pass



class NoDbTestRunner(DiscoverRunner):
    """ A test runner to test without database creation/deletion. 
        An example, testing a single file:
        $ python manage.py test server.forecasting.tests.test_extensions --testrunner=server.tests.NoDbTestRunner
    """
    def setup_databases(self, **kwargs):
        pass
    def teardown_databases(self, old_config, **kwargs):
        pass