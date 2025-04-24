from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from forum.config import SQLALCHEMY_DATABASE_URI, SECRET_KEY

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .forum import bp
    app.register_blueprint(bp)
    return app

def init_db(app):
    with app.app_context():
        db.create_all()