from urllib.parse import urljoin
import meido
import unittest


class MeidoTestCase(unittest.TestCase):
    def setUp(self):
        self.app = meido.create_app('meido.config.TestConfig')
        self.client = self.app.test_client()

        with self.context():
            meido.db.create_all()
        self.addCleanup(self.db_cleanup)

    def assert200(self, response):
        """Assert that the response had the HTTP status code of 200."""
        self.assertEqual(response.status_code, 200)

    def assert404(self, response):
        """Assert that the response had the HTTP status code of 200."""
        self.assertEqual(response.status_code, 404)

    def assertContains(self, response, text):
        """Assert that the given string is found in the response."""
        self.assertIn(text, response.data.decode('utf-8'))

    def assertRedirects(self, response, url):
        """Assert that response redirects to given URL."""
        server_name = self.app.config.get('SERVER_NAME') or 'localhost'
        redirect_url = response.headers.get('Location', None)
        target_url = urljoin('http://{}'.format(server_name), url)
        self.assertEqual(redirect_url, target_url)

    def context(self):
        """Returns current application context."""
        return self.app.app_context()

    def create_and_login(self):
        """Creates a test user and logs in with it."""
        with self.context():
            user = self.factory(meido.factories.UserFactory)
        self.client.post('/management/login', data={
            'username': 'admin', 'password': 'pretender'
        })

    def db_cleanup(self):
        """Removes active session and drops all tables. To be used after each test."""
        with self.context():
            meido.db.session.remove()
            meido.db.drop_all()

    def factory(self, factory_class, *args, **kwargs):
        """Creates an object based on the factory class and adds it to the database.
        Returns the object.
        """
        factory_class._meta.sqlalchemy_session = meido.db.session
        obj = factory_class.build(*args, **kwargs)
        meido.db.session.add(obj)
        meido.db.session.commit()
        meido.db.session.refresh(obj)
        return obj
