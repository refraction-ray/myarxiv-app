"""
initialize database via sqlalchemy
"""

from .models import db
from .main import create_app

app = create_app(False)
with app.app_context():
    db.create_all()
