from os.path import join as pathjoin

from flask import current_app
from flask_restful import abort, Resource, reqparse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from meido import models
from meido.database import db
from meido.management import notifications
from meido.utils import commit_or_rollback


class Builds(Resource):
    def get_build(self, project) -> models.Build:
        """Initializes and returns a Build model object from resource args."""
        build = models.Build()
        build.number = self.args.get('build_number')
        build.commit = self.args.get('commit', None)
        build.commit_message = self.args.get('commit_message', None)
        build.project = project
        return build

    def get_project(self) -> models.Project:
        """Gets a project based on the Authorization header string. If the authorization
        code does not match any project, HTTP 401 is returned.
        """
        api_key = self.args.get('Authorization', None)
        try:
            return models.Project.query.filter_by(api_key=api_key).one()
        except NoResultFound:
            abort(401)

    def post(self):
        """Adds a new build into Meido. Requires an authorization header, a build number
        and a file. Also accepts commit hash and message.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')
        parser.add_argument('build_number', required=True, type=int)
        parser.add_argument('commit')
        parser.add_argument('commit_message')
        parser.add_argument('file', required=True, type=FileStorage, location='files')
        self.args = parser.parse_args()

        project = self.get_project()
        filters = {
            'number': self.args.get('build_number'),
            'project': project,
        }
        if models.Build.query.filter_by(**filters).first() is not None:
            message = 'Build with same build number already exists'
            notifications.upload_failed(project, filters['number'], message)
            abort(409, message=message)

        build = self.get_build(project)
        build_file = self.args.get('file')
        destination = pathjoin(current_app.config['BUILD_DIRECTORY'],
                               build.generate_filename(build_file.filename))
        db.session.add(build)
        if commit_or_rollback():
            build_file.save(destination)
        else:
            message = 'Database error'
            notifications.upload_failed(project, build.number, message)
            abort(500, message=message)
        notifications.upload_successful(project, build.number)
        return {'success': True}
