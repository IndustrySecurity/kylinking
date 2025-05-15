from flask import Blueprint

tenant_bp = Blueprint('tenant', __name__)

from app.api.tenant import routes 