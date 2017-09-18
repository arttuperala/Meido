from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_migrate import Migrate
from raven.contrib.flask import Sentry

debug_toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.login_view = "management.login"
login_manager.login_message_category = "warning"

migrate = Migrate()

sentry = Sentry()


@login_manager.user_loader
def load_user(userid):
    from meido.models import User
    return User.query.get(userid)
