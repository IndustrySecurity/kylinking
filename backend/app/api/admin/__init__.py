from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from app.api.admin import routes 