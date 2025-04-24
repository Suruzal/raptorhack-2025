from forum import create_app, init_db, db
from forum.setup import init_site
from forum.database import Subforum

app = create_app()
init_db(app)

if __name__ == '__main__':
    with app.app_context():
        if not db.session.query(db.exists().where(Subforum.id == 1)).scalar():
            init_site()
        app.run()