from flask import render_template, request, redirect, Blueprint, url_for, jsonify, current_app, flash
from flask_login import login_required, current_user, logout_user, login_user
import datetime
from . import db, login_manager
from .database import *
import os
from .setup import init_site
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash

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
def landing():
    return render_template("landing.html")

@bp.route('/addpost')
def addpost():
    if not current_user.is_authenticated:
        return redirect(url_for('main.loginform'))
    
    try:
        subforum = Subforum.query.filter_by(id=1).first()
        if not subforum:
            # Initialize if missing
            subforum = init_site()
            db.session.commit()
            
        if not subforum:
            raise Exception("Failed to initialize main subforum")
            
        return render_template("createpost.html", subforum=subforum)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in addpost: {e}")
        return error("System error. Please contact administrator.")

@bp.route('/home')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("allposts.html", posts=posts)

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

@bp.route('/action_post', methods=['POST'])
@login_required
def action_post():
    try:
        # Always use the main forum (id=1) for posts
        subforum = Subforum.query.filter_by(id=1).first()
        if not subforum:
            return error("System is not properly initialized!")

        title = request.form['title']
        content = request.form['content']
        
        # Validation checks
        if not title or len(title) < 4 or len(title) > 140:
            flash('Title must be between 4 and 140 characters.')
            return redirect(url_for('main.addpost'))
            
        if not content or len(content) < 10 or len(content) > 5000:
            flash('Content must be between 10 and 5000 characters.')
            return redirect(url_for('main.addpost'))

        post = Post(
            title=title,
            content=content,
            user_id=current_user.id,
            subforum_id=subforum.id,
            created_at=datetime.datetime.now()
        )
        
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('main.viewpost', post=post.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating post: {e}")
        flash('An error occurred while creating your post.')
        return redirect(url_for('main.addpost'))

@bp.route('/action_login', methods=['POST'])
def action_login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter(User.username == username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect("/home")
    errors = []
    errors.append("Username or password is incorrect!")
    return render_template("login.html", errors=errors)

@login_required
@bp.route('/action_logout')
def action_logout():
    logout_user()
    return redirect("/home")

@bp.route('/action_createaccount', methods=['POST'])
def action_createaccount():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    major = request.form['major']
    errors = []
    retry = False
    
    if not major:
        errors.append("You must provide a major!")
        retry = True
    if username_taken(username):
        errors.append("Username is already taken!")
        retry = True
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
    
    user = User(username=username, email=email, major=major)
    user.set_password(password)  # Use the set_password method instead of direct assignment
    
    if user.username == "admin":
        user.is_admin = True
        
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect("/home")

@bp.route('/transfer')
@login_required
def transfer():
    return render_template('transfer.html')

@bp.route('/process_transfer', methods=['POST'])
@login_required
def process_transfer():
    try:
        username = request.form.get('username')
        karma_amount = request.form.get('karma_amount')
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        errors = []
        
        # Input validation
        if not all([username, karma_amount, rating, comment]):
            errors.append("All fields are required")
            return render_template('transfer.html', errors=errors)
            
        try:
            karma_amount = int(karma_amount)
            rating = float(rating)  # Keep as float instead of converting to int
        except (TypeError, ValueError):
            errors.append("Invalid karma amount or rating value")
            return render_template('transfer.html', errors=errors)
            
        if karma_amount <= 0:
            errors.append("Karma amount must be positive")
            return render_template('transfer.html', errors=errors)
            
        if rating < 1.0 or rating > 5.0:
            errors.append("Rating must be between 1 and 5")
            return render_template('transfer.html', errors=errors)

        # Validate recipient exists
        recipient = User.query.filter_by(username=username).first()
        if not recipient:
            errors.append("Recipient username not found")
            return render_template('transfer.html', errors=errors)
        
        if recipient.id == current_user.id:
            errors.append("Cannot transfer karma to yourself")
            return render_template('transfer.html', errors=errors)
            
        # Check karma amount
        if karma_amount > current_user.karma:
            errors.append("Insufficient karma balance")
            return render_template('transfer.html', errors=errors)

        # Start transaction block
        try:
            # Update sender's karma (current only)
            current_user.karma -= karma_amount
            
            # Update recipient's karma (both current and total)
            recipient.karma += karma_amount
            recipient.total_karma += karma_amount
            
            # Update recipient's rating - calculate weighted average
            if recipient.rating is None:
                recipient.rating = float(rating)
            else:
                # Get current total stars and count
                current_total = recipient.rating * 5  # Assuming rating is out of 5
                # Add new rating
                new_total = current_total + rating
                # Update to new average
                recipient.rating = new_total / 6  # (5 + 1 new rating)
            
            # Create transaction record
            transaction = Transaction(
                sender_id=current_user.id,
                recipient_id=recipient.id,
                amount=karma_amount,
                rating=rating,
                comment=comment,
                created_at=datetime.datetime.now()  # Add timestamp
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            return redirect('/home')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Transfer failed: {str(e)}")
            errors.append("Transaction failed, please try again")
            return render_template('transfer.html', errors=errors)
            
    except Exception as e:
        current_app.logger.error(f"Transfer error: {str(e)}")
        return render_template('transfer.html', errors=["An unexpected error occurred"])

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

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@bp.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form.get('new_email')
    errors = []
    
    if not new_email:
        errors.append("Email cannot be empty")
    elif email_taken(new_email) and new_email != current_user.email:
        errors.append("Email is already in use")
        
    if errors:
        return render_template('profile.html', errors=errors)
        
    current_user.email = new_email
    db.session.commit()
    return redirect('/profile')

@bp.route('/update_password', methods=['POST'])
@login_required
def update_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    errors = []
    
    if not current_user.check_password(current_password):
        errors.append("Current password is incorrect")
    elif not valid_password(new_password):
        errors.append("New password is not valid")
        
    if errors:
        return render_template('profile.html', errors=errors)
        
    current_user.set_password(new_password)
    db.session.commit()
    return redirect('/profile')
