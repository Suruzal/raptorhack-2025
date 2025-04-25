from . import db
from .database import Subforum

def init_site():
    # Create main forum if it doesn't exist
    main = Subforum.query.filter_by(id=1).first()
    if not main:
        main = Subforum(
            id=1,
            name="BarterBoard",
            description="All tutoring and learning exchange posts"
        )
        db.session.add(main)
        db.session.flush()  # Flush to get the ID without committing
    return main

