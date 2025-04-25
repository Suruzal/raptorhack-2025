from forum import create_app, db
from forum.database import User

def update_existing_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.karma is None:
                user.karma = 10
            if user.rating is None:
                user.rating = 5.0
        db.session.commit()

if __name__ == '__main__':
    update_existing_users()
