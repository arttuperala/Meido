from io import BytesIO
from meido.database import db
from meido.factories import BuildFactory, ProjectFactory, UserFactory
from meido.models import Build, Project
from tests.base import MeidoTestCase
from unittest.mock import DEFAULT, patch
from werkzeug.exceptions import InternalServerError


def fake_abort(code, message=''):
    pass


class ProjectManagementAPIBuildTest(MeidoTestCase):
    def setUp(self):
        super().setUp()
        self.create_and_login()
        with self.context():
            self.project = self.factory(ProjectFactory, name='Test Project', stub='test')

    def request_data(self, build_number=1, commit_message='Initial commit',
                     commit='1c66a45bb77d90f50f258d6bad89ee196d98971b'):
        return {
            'build_number': build_number,
            'commit': commit,
            'commit_message': commit_message,
            'file': (BytesIO(b'file content'), 'build.txt'),
        }

    def request_headers(self, key=None):
        return {
            'Authorization': self.project.api_key if not key else key,
        }

    def test_api_build_upload(self):
        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers())
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '"success": true')

    @patch('meido.management.notifications.post')
    def test_api_build_upload_notification(self, mock_post):
        MAILGUN_KEY = 'key-test123'
        MAILGUN_SENDER = 'meido@example.com'
        MAILGUN_URL = 'https://api.mailgun.net/v3/meido.example.com/messages'
        self.app.config['MAILGUN_ENABLED'] = True
        self.app.config['MAILGUN_KEY'] = MAILGUN_KEY
        self.app.config['MAILGUN_SENDER'] = MAILGUN_SENDER
        self.app.config['MAILGUN_URL'] = MAILGUN_URL

        with self.context():
            user = self.factory(UserFactory, username='test_user', email='test@example.com')
            project = Project.query.get(self.project.id)
            project.subscribed_users.append(user)
            db.session.commit()

        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers())
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '"success": true')

        data = {'from': 'Meido <{}>'.format(MAILGUN_SENDER),
                'to': ['test@example.com'],
                'subject': 'Test Project: upload successful',
                'text': 'Build #1 was successfully uploaded for project Test Project.'}
        mock_post.assert_called_with(MAILGUN_URL, auth=('api', MAILGUN_KEY), data=data)

    @patch('meido.management.notifications.post')
    def test_api_build_upload_notification_no_subscriptions(self, mock_post):
        self.app.config['MAILGUN_ENABLED'] = True

        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers())
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '"success": true')
        mock_post.assert_not_called()

    def test_api_build_upload_tar_gz(self):
        data = self.request_data()
        data['file'] = (BytesIO(b'file content'), 'build.tar.gz')
        response = self.client.post('/management/api/build', data=data,
                                    headers=self.request_headers(), errors_stream=None)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, '"success": true')

        with self.context():
            build = Build.query.filter_by(project_id=self.project.id, number=1).one()
        self.assertEquals(build.filename, 'test-1.tar.gz')

    @patch.multiple('meido.management.resources',
                    abort=DEFAULT, commit_or_rollback=DEFAULT)
    def test_api_build_database_error(self, abort, commit_or_rollback):
        commit_or_rollback.return_value = False
        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers())
        abort.assert_called_with(500, message='Database error')

    def test_api_build_upload_duplicate_build(self):
        with self.context():
            self.factory(BuildFactory, number=1, project=self.project)
            project = Project.query.get(self.project.id)
            self.assertEquals(project.builds.count(), 1)

        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers())
        self.assertEquals(response.status_code, 409)
        self.assertContains(response, 'same build number already exists')

        with self.context():
            project = Project.query.get(self.project.id)
            self.assertEquals(project.builds.count(), 1)

    def test_api_build_upload_no_authorization(self):
        response = self.client.post('/management/api/build', data=self.request_data())
        self.assertEquals(response.status_code, 401)
        self.assertContains(response, 'wrong credentials')

    def test_api_build_upload_wrong_authorization(self):
        response = self.client.post('/management/api/build', data=self.request_data(),
                                    headers=self.request_headers('ABC123DEF456'))
        self.assertEquals(response.status_code, 401)
        self.assertContains(response, 'wrong credentials')
