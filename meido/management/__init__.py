from flask import Blueprint
from flask_restful import Api

from meido.management import resources

_management = Blueprint('management', __name__, template_folder='templates')
api = Api(_management)

from . import views

api.add_resource(resources.Builds, '/api/build')
