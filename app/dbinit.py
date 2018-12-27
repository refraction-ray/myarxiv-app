"""
initialize database via sqlalchemy
"""

from .models import db
from .main import create_app

if __name__ == "__main__":
    create_app(False, True)
