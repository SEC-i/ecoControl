from django.test.runner import DiscoverRunner


class CustomTestSuiteRunner(DiscoverRunner):

    def teardown_databases(self, old_config, **kwargs):
        """
        Don't destroy test database
        """
        pass
