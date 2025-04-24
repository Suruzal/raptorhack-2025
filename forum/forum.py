from flask import render_template, request, redirect, Blueprint, url_for
from flask_login import login_required, current_user, logout_user, login_user
import datetime
from . import db, login_manager
from .database import *
import os
from .setup import init_site
import hashlib

bp = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

def simple_hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@bp.app_context_processor
def inject_user():
    return dict(current_user=current_user)

@bp.route('/')
def index():
    subforums = Subforum.query.filter(Subforum.parent_id == None).order_by(Subforum.id)
    return render_template("subforums.html", subforums=subforums)

@bp.route('/subforum')
def subforum():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")
    posts = Post.query.filter(Post.subforum_id == subforum_id).order_by(Post.id.desc()).limit(50)
    path = generateLinkPath(subforum.id)
    subforums = Subforum.query.filter(Subforum.parent_id == subforum_id).all()
    return render_template("subforum.html", subforum=subforum, posts=posts, subforums=subforums, path=path)

@bp.route('/loginform')
def loginform():
    return render_template("login.html")

@bp.route('/addpost')
def addpost():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return error("That subforum does not exist!")
    if not current_user.is_authenticated:
        return redirect(url_for('main.loginform'))
    return render_template("createpost.html", subforum=subforum)

@login_required
@bp.route('/viewpost')
def viewpost():
    postid = int(request.args.get("post"))
    post = Post.query.filter(Post.id == postid).first()
    if not post:
        return error("That post does not exist!")
    # Compute path as a local variable
    path = generateLinkPath(post.subforum.id)
    comments = Comment.query.filter(Comment.post_id == postid).order_by(Comment.id.desc())
    return render_template("viewpost.html", post=post, path=path, comments=comments)

@login_required
@bp.route('/action_comment', methods=['POST', 'GET'])
def comment():
    post_id = int(request.args.get("post"))
    post = Post.query.filter(Post.id == post_id).first()
    if not post:
        return error("That post does not exist!")
    content = request.form['content']
    postdate = datetime.datetime.now()
    comment = Comment(
        content=content,
        created_at=postdate,
        user_id=current_user.id,
        post_id=post.id
    )
    db.session.add(comment)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post_id))

@login_required
@bp.route('/action_post', methods=['POST'])
def action_post():
    subforum_id = int(request.args.get("sub"))
    subforum = Subforum.query.filter(Subforum.id == subforum_id).first()
    if not subforum:
        return redirect(url_for("subforums"))

    user = current_user
    title = request.form['title']
    content = request.form['content']
    #check for valid posting
    errors = []
    retry = False
    if not valid_title(title):
        errors.append("Title must be between 4 and 140 characters long!")
        retry = True
    if not valid_content(content):
        errors.append("Post must be between 10 and 5000 characters long!")
        retry = True
    if retry:
        return render_template("createpost.html",subforum=subforum,  errors=errors)
    post = Post(
        title=title,
        content=content,
        user_id=user.id,
        subforum_id=subforum.id,
        created_at=datetime.datetime.now()
    )
    db.session.add(post)
    db.session.commit()
    return redirect("/viewpost?post=" + str(post.id))

@bp.route('/action_login', methods=['POST'])
def action_login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter(User.username == username).first()
    if user and user.check_password(password):
        login_user(user)
    else:
        errors = []
        errors.append("Username or password is incorrect!")
        return render_template("login.html", errors=errors)
    return redirect("/")

@login_required
@bp.route('/action_logout')
def action_logout():
    logout_user()
    return redirect("/")

@bp.route('/action_createaccount', methods=['POST'])
def action_createaccount():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    errors = []
    retry = False
    if username_taken(username):
        errors.append("Username is already taken!")
        retry=True
    if email_taken(email):
        errors.append("An account already exists with this email!")
        retry = True
    if not valid_username(username):
        errors.append("Username is not valid!")
        retry = True
    if not valid_password(password):
        errors.append("Password is not valid!")
        retry = True
    if retry:
        return render_template("login.html", errors=errors)
    user = User(username=username, email=email, password=password)  # pass raw password
    if user.username == "admin":
        user.is_admin = True
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect("/")

def error(errormessage):
    return "<b style=\"color: red;\">" + errormessage + "</b>"

def generateLinkPath(subforumid):
    links = []
    subforum = Subforum.query.filter(Subforum.id == subforumid).first()
    parent = Subforum.query.filter(Subforum.id == subforum.parent_id).first()
    # Use 'name' if 'title' does not exist on Subforum
    links.append("<a href=\"/subforum?sub=" + str(subforum.id) + "\">" + getattr(subforum, 'title', getattr(subforum, 'name', '')) + "</a>")
    while parent is not None:
        links.append("<a href=\"/subforum?sub=" + str(parent.id) + "\">" + getattr(parent, 'title', getattr(parent, 'name', '')) + "</a>")
        parent = Subforum.query.filter(Subforum.id == parent.parent_id).first()
    links.append("<a href=\"/\">Forum Index</a>")
    link = ""
    for l in reversed(links):
        link = link + " / " + l
    return link
