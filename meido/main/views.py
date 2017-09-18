from flask import current_app, render_template, send_from_directory

from meido.database import db
from meido.main import main
from meido.models import Build, Project
from meido.utils import commit_or_rollback


@main.route('/')
def index():
    """Main page for Meido. Serves a list of all projects."""
    projects = Project.query.all()
    return render_template('main/index.html', projects=projects)


@main.route('/<stub>/download/<build_number>')
def project_download(stub, build_number):
    """Serves the build file to the client based on the project stub and build number.
    When the download link is fetched, the download counter on a build is updated
    atomically.
    """
    build = Build.query.join(Project)\
                       .filter(Project.stub == stub, Build.number == build_number)\
                       .first_or_404()
    build.downloads = Build.downloads + 1
    commit_or_rollback()
    return send_from_directory(current_app.config['BUILD_DIRECTORY'], build.filename,
                               as_attachment=True)


@main.route('/<stub>')
def project_index(stub):
    """Index page for an individual project. Lists basic project details and list of all
    builds.
    """
    project = Project.query.filter_by(stub=stub).first_or_404()
    builds = project.builds.order_by(Build.number.desc()).all()
    context = {'builds': builds, 'project': project}
    return render_template('main/project.html', **context)
