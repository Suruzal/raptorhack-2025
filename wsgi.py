from forum import create_app, init_db, db
from forum.setup import init_site
from forum.database import Subforum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
init_db(app)

with app.app_context():
    try:
        # Check if main subforum exists
        subforum = Subforum.query.filter_by(id=1).first()
        if not subforum:
            logger.info("Main subforum not found, initializing site...")
            init_site()
            db.session.commit()
            logger.info("Site initialization complete")
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        db.session.rollback()
        raise
            
if __name__ == '__main__':
    app.run()