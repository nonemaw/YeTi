from flask import Blueprint

code = Blueprint('code', __name__)

from . import views
