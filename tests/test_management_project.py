from meido.database import db
from meido.factories import ProjectFactory
from meido.models import Project, User
from tests.base import MeidoTestCase


class ProjectManagementAddTest(MeidoTestCase):
    def setUp(self):
        super().setUp()
        self.create_and_login()

    def test_project_add_load(self):
        response = self.client.get('/management/project/add')
        self.assert200(response)

    def test_project_add_post(self):
        data = {
            'name': 'Test Project',
            'stub': '',
            'color': 'ffffff',
            'description': 'This is a test project.',
        }
        response = self.client.post('/management/project/add', data=data)
        self.assertRedirects(response, '/management/')

        with self.context():
            project = Project.query.filter_by(name=data['name']).one()
        self.assertEquals(project.stub, 'test-project')
        self.assertEquals(project.color, data['color'])
        self.assertEquals(project.description, data['description'])

    def test_project_add_post_with_stub(self):
        data = {
            'name': 'Test Project',
            'stub': 'test',
        }
        response = self.client.post('/management/project/add', data=data)
        self.assertRedirects(response, '/management/')

        with self.context():
            project = Project.query.filter_by(name=data['name']).one()
        self.assertEquals(project.stub, 'test')

    def test_project_add_post_invalid_color_code(self):
        data = {
            'name': 'Test Project',
            'stub': '',
            'color': '#efghij',
            'description': 'This is a test project.',
        }
        response = self.client.post('/management/project/add', data=data)
        self.assertContains(response, 'not a valid hexadecimal color code')


class ProjectManagementEditTest(MeidoTestCase):
    def setUp(self):
        super().setUp()
        self.create_and_login()
        with self.context():
            self.project = self.factory(ProjectFactory, name='Test Project', stub='test')

    def test_project_edit_post(self):
        data = {
            'name': 'Test Project',
            'stub': 'test-project',
            'color': 'f0f0f0',
            'description': 'This is a test project.',
        }
        response = self.client.post('/management/project/test/edit', data=data)
        self.assertRedirects(response, '/management/')

        with self.context():
            project = Project.query.get(self.project.id)
        self.assertEquals(project.name, data['name'])
        self.assertEquals(project.stub, data['stub'])
        self.assertEquals(project.color, data['color'])
        self.assertEquals(project.description, data['description'])

    def test_project_edit_view(self):
        response = self.client.get('/management/project/test/edit')
        self.assert200(response)
        self.assertContains(response, self.project.name)

    def test_project_edit_view_404(self):
        response = self.client.get('/management/project/test-project/edit')
        self.assert404(response)


class ProjectManagementViewTest(MeidoTestCase):
    def setUp(self):
        super().setUp()
        self.create_and_login()
        with self.context():
            self.project = self.factory(ProjectFactory, name='Test Project', stub='test')

    def test_project_generated_api_key(self):
        with self.context():
            project = Project.query.get(self.project.id)
        old_key = project.api_key

        response = self.client.get('/management/project/test/generate-key')
        self.assertRedirects(response, '/management/project/test')

        with self.context():
            project = Project.query.get(self.project.id)
        new_key = project.api_key
        self.assertNotEquals(old_key, new_key)

    def test_project_subscribe(self):
        with self.context():
            project = Project.query.get(self.project.id)
            self.assertEquals(len(project.subscribed_users), 0)

        response = self.client.get('/management/project/test/subscribe')

        with self.context():
            project = Project.query.get(self.project.id)
            self.assertEquals(len(project.subscribed_users), 1)

    def test_project_subscribe_reverse(self):
        with self.context():
            user = User.query.get(1)
            project = Project.query.get(self.project.id)
            project.subscribed_users.append(user)
            db.session.commit()
            self.assertEquals(len(project.subscribed_users), 1)

        response = self.client.get('/management/project/test/subscribe')

        with self.context():
            project = Project.query.get(self.project.id)
            self.assertEquals(len(project.subscribed_users), 0)

    def test_project_view(self):
        response = self.client.get('/management/project/test')
        self.assert200(response)
        self.assertContains(response, self.project.name)

    def test_project_view_404(self):
        response = self.client.get('/management/project/test-project')
        self.assert404(response)
