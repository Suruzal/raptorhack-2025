import os
import secrets
from pathlib import Path

# Create base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True, parents=True)

# Database configuration
DB_FILE = INSTANCE_DIR / 'forum.db'
SQLALCHEMY_DATABASE_URI = (f'sqlite:///{DB_FILE}')
SECRET_KEY = secrets.token_hex(32)

# Site configuration
SITE_NAME = "BarterBoard"
SITE_DESCRIPTION = "A simple forum application"

