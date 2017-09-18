from tests.base import MeidoTestCase
from meido.factories import UserFactory


class LoginTest(MeidoTestCase):
    def send_login(self, username, password):
        return self.client.post('/management/login', data={
            'username': username,
            'password': password,
        })

    def test_login_load(self):
        response = self.client.get('/management/login')
        self.assert200(response)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')

    def test_login_post(self):
        with self.context():
            user = self.factory(UserFactory)

        response = self.send_login('admin', 'pretender')
        self.assertRedirects(response, '/management/')

    def test_login_post_blank(self):
        with self.context():
            user = self.factory(UserFactory)

        response = self.send_login('', '')
        self.assertContains(response, 'Username is required')

    def test_login_post_wrong_password(self):
        with self.context():
            user = self.factory(UserFactory)

        response = self.send_login('admin', 'password')
        self.assertContains(response, 'Invalid username or password')

    def test_login_post_wrong_username(self):
        with self.context():
            user = self.factory(UserFactory)

        response = self.send_login('user', 'pretender')
        self.assertContains(response, 'Invalid username or password')

    def test_logout(self):
        self.create_and_login()
        response = self.client.get('/management/')
        self.assert200(response)

        response = self.client.get('/management/logout')
        self.assertRedirects(response, '/management/login')

        response = self.client.get('/management/')
        self.assertRedirects(response, '/management/login?next=%2Fmanagement%2F')
