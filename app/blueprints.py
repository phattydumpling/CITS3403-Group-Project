from flask import Blueprint

main = Blueprint('main', __name__)

# Import routes after blueprint creation to avoid circular imports
from app import routes 