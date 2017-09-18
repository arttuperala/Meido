#!/usr/bin/env python

import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server
from flask_script.commands import ShowUrls, Clean

from meido import create_app
from meido.models import db, User


env = os.environ.get('MEIDO_ENV', 'development')
app = create_app('meido.config.%sConfig' % env.capitalize())

migrate = Migrate(app, db, directory='meido/migrations')

manager = Manager(app)
manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)
manager.add_command('show-urls', ShowUrls())
manager.add_command('clean', Clean())


@manager.shell
def make_shell_context():
    """Creates a Python shell with several default imports in the context of the app."""
    return dict(app=app, db=db, User=User)


@manager.command
def dbcreate():
    """Initializes a database from the defined SQLAlchemy models."""
    db.create_all()


if __name__ == '__main__':
    manager.run()
