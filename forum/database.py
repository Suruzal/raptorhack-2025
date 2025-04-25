# NOTE: If you get "no such table: subforum", make sure to run db.create_all() after importing all models.
# This is usually handled in your app's __init__.py or app.py.

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import datetime
import re

# --- Validation regex ---
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")
PASSWORD_RE = re.compile(r"^[\S]{6,64}$")

# --- User model ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Changed from password
    major = db.Column(db.String(64))  # Made nullable by removing nullable=False
    is_admin = db.Column(db.Boolean, default=False)
    karma = db.Column(db.Integer, default=10)
    total_karma = db.Column(db.Integer, default=10)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# --- Subforum model (supports hierarchy) ---
class Subforum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(256))
    parent_id = db.Column(db.Integer, db.ForeignKey('subforum.id'))
    children = db.relationship("Subforum", backref=db.backref("parent", remote_side=[id]), lazy="dynamic")
    posts = db.relationship("Post", backref="subforum", lazy="dynamic")
    is_hidden = db.Column(db.Boolean, default=False)

# --- Post model ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subforum_id = db.Column(db.Integer, db.ForeignKey('subforum.id'), nullable=False)
    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def get_time_string(self):
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M")
        return ""

# --- Comment model ---
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    # For comment threads: parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # replies = db.relationship("Comment", ...)

    def get_time_string(self):
        if self.created_at:
            return self.created_at.strftime("%Y-%m-%d %H:%M")
        return ""

# --- Validation helpers ---
def username_taken(username):
    return db.session.query(User.id).filter_by(username=username).first() is not None

def email_taken(email):
    return db.session.query(User.id).filter_by(email=email).first() is not None

def valid_username(username):
    return USERNAME_RE.match(username) is not None

def valid_password(password):
    return PASSWORD_RE.match(password) is not None

def valid_title(title):
    return 4 < len(title) < 140

def valid_content(content):
    return 10 < len(content) < 5000

# --- Utility for time display ---
def time_ago(dt):
    now = datetime.datetime.utcnow()
    diff = now - dt
    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    elif seconds < 86400:
        return f"{int(seconds // 3600)} hours ago"
    elif seconds < 2592000:
        return f"{int(seconds // 86400)} days ago"
    else:
        return f"{int(seconds // 2592000)} months ago"