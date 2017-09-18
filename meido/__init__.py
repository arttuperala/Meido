#!/usr/bin/env python3

from flask import Flask
from os import environ

from meido import filters
from meido.database import db
from meido.extensions import (
    debug_toolbar,
    login_manager,
    migrate,
    sentry,
)
from meido.main import main
from meido.management import _management


def create_app(object_name: str) -> Flask:
    """An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Args:
        object_name: the python path of the config object,
                     e.g. meido.settings.ProdConfig
    """

    app = Flask(__name__)
    app.config.from_object(object_name)
    if environ.get('MEIDO_SETTINGS', None):  # pragma: no cover
        app.config.from_envvar('MEIDO_SETTINGS')

    debug_toolbar.init_app(app)

    db.init_app(app)

    login_manager.init_app(app)

    migrate.init_app(app)

    sentry.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(_management, url_prefix='/management')

    for jinja_filter in filters.__all__:
        app.jinja_env.filters[jinja_filter.__name__] = jinja_filter

    return app
