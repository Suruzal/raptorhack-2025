from forum import create_app, db
from forum.database import User

def update_sigma_karma():
    app = create_app()
    with app.app_context():
        try:
            # Find Sigma user
            sigma = User.query.filter_by(username="Sigma").first()
            if sigma:
                sigma.karma = 300
                sigma.total_karma = 300
                db.session.commit()
                print(f"Successfully updated Sigma's karma to 300")
            else:
                print("Sigma user not found")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating karma: {e}")

if __name__ == '__main__':
    update_sigma_karma()
