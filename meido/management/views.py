from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask.views import View

from meido.management import forms, _management as management
from meido.models import db, Project, User
from meido.utils import commit_or_rollback, is_safe_url


@management.route('/')
@login_required
def index():
    projects = Project.query.all()
    return render_template('management/index.html', projects=projects)


@management.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)
        next_page = request.args.get('next', url_for('.index'))
        return redirect(next_page if is_safe_url(next_page) else url_for('.index'))

    return render_template('management/login.html', form=form)


@management.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('management.login'))


@management.route('/project/<stub>')
@login_required
def project(stub):
    project = Project.query.filter_by(stub=stub).first_or_404()
    return render_template('management/project.html', project=project)


@management.route('/project/add', methods=['GET', 'POST'])
@login_required
def project_add():
    form = forms.ProjectForm()

    if form.validate_on_submit():
        project = Project(**form.data)
        db.session.add(project)
        if commit_or_rollback():
            return redirect(url_for('.index'))

    return render_template('management/project_form.html', form=form)


@management.route('/project/<stub>/edit', methods=['GET', 'POST'])
@login_required
def project_edit(stub):
    project = Project.query.filter_by(stub=stub).first_or_404()
    form = forms.ProjectForm(obj=project)

    if form.validate_on_submit():
        form.populate_obj(project)
        if commit_or_rollback():
            return redirect(url_for('.index'))

    return render_template('management/project_form.html', form=form, project=project)


@management.route('/project/<stub>/generate-key')
@login_required
def project_generate_api_key(stub):
    project = Project.query.filter_by(stub=stub).first_or_404()
    project.generate_api_key()
    commit_or_rollback()
    return redirect(url_for('.project', stub=project.stub))


@management.route('/project/<stub>/subscribe')
@login_required
def project_subscribe(stub):
    project = Project.query.filter_by(stub=stub).first_or_404()
    if current_user in project.subscribed_users:
        project.subscribed_users.remove(current_user)
    else:
        project.subscribed_users.append(current_user)
    commit_or_rollback()
    return redirect(url_for('.project', stub=project.stub))
