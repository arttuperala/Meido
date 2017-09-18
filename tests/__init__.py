from tests.base import MeidoTestCase
from meido.factories import UserFactory
from meido.models import Project


class ProjectManagementTest(MeidoTestCase):
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
            'color': 'efghij',
            'description': 'This is a test project.',
        }
        response = self.client.post('/management/project/add', data=data)
        self.assertContains(response, 'not a valid hexadecimal color code')
