from datetime import datetime, timedelta
from meido.factories import BuildFactory, ProjectFactory
from meido.models import Build, Project
from os.path import join as pathjoin
from tempfile import TemporaryDirectory
from tests.base import MeidoTestCase


class MeidoMainTest(MeidoTestCase):
    def setUp(self):
        super().setUp()
        with self.context():
            self.project = self.factory(ProjectFactory)

    def test_download(self):
        temp_directory = TemporaryDirectory()
        self.app.config['BUILD_DIRECTORY'] = temp_directory.name

        with self.context():
            self.factory(BuildFactory, project=self.project, number=1)
            build = Build.query.get(1)
            self.project = Project.query.get(self.project.id)
        self.assertEquals(build.downloads, 0)

        with open(pathjoin(temp_directory.name, build.filename), 'w') as file:
            file.write('test content')
        response = self.client.get('/{}/download/1'.format(self.project.stub))
        self.assert200(response)
        self.assertEquals(response.headers['Content-Disposition'],
                          'attachment; filename=build-1.txt')
        self.assertContains(response, 'test content')

        with self.context():
            build = Build.query.get(1)
        self.assertEquals(build.downloads, 1)
        temp_directory.cleanup()

    def test_index_load(self):
        response = self.client.get('/')
        self.assert200(response)
        self.assertContains(response, self.project.name)
        self.assertContains(response, 'Never updated')

    def test_index_load_with_updates(self):
        with self.context():
            date = datetime.utcnow() - timedelta(days=4)
            self.factory(BuildFactory, project=self.project, number=1, date=date)
            self.project = Project.query.get(self.project.id)

        response = self.client.get('/')
        self.assert200(response)
        self.assertContains(response, self.project.name)
        self.assertContains(response, 'Last updated 4 days ago')

    def test_project_load(self):
        response = self.client.get('/{}'.format(self.project.stub))
        self.assert200(response)
        self.assertContains(response, self.project.name)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.color)

    def test_project_load_with_builds(self):
        with self.context():
            self.factory(BuildFactory, project=self.project, number=1, )
            self.factory(BuildFactory, project=self.project, number=2, )
            self.factory(BuildFactory, project=self.project, number=3, )
            self.factory(BuildFactory, project=self.project, number=4, )
            self.project = Project.query.get(self.project.id)

        response = self.client.get('/{}'.format(self.project.stub))
        self.assert200(response)
        with self.context():
            self.assertContains(response, self.project.name)
            self.assertContains(response, self.project.description)
            self.assertContains(response, self.project.color)

    def test_project_badge(self):
        with self.context():
            self.factory(BuildFactory, project=self.project, number=1, )
            self.factory(BuildFactory, project=self.project, number=12, )
            self.factory(BuildFactory, project=self.project, number=108, )
            self.factory(BuildFactory, project=self.project, number=4951, )
            self.project = Project.query.get(self.project.id)

        response = self.client.get('/{}/badge.svg'.format(self.project.stub))
        self.assert200(response)
        with self.context():
            self.assertContains(response, 'latest build')
            self.assertContains(response, '#4951')
