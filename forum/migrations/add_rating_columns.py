from flask import current_app
from flask_migrate import Migrate
from forum import db

def upgrade():
    # Add rating columns if they don't exist
    with current_app.app_context():
        db.engine.execute('''
            ALTER TABLE user 
            ADD COLUMN rating_numerator INTEGER DEFAULT 0;
        ''')
        db.engine.execute('''
            ALTER TABLE user 
            ADD COLUMN rating_denominator INTEGER DEFAULT 0;
        ''')

def downgrade():
    with current_app.app_context():
        db.engine.execute('ALTER TABLE user DROP COLUMN rating_numerator;')
        db.engine.execute('ALTER TABLE user DROP COLUMN rating_denominator;')
