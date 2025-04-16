class UserService:
    def __init__(self, db_session):
        self.db_session = db_session

    def add_user(self, user_data):
        new_user = User(**user_data)
        self.db_session.add(new_user)
        self.db_session.commit()
        return new_user

    def get_user(self, user_id):
        return self.db_session.query(User).filter_by(id=user_id).first()

    def update_user(self, user_id, updated_data):
        user = self.get_user(user_id)
        if user:
            for key, value in updated_data.items():
                setattr(user, key, value)
            self.db_session.commit()
        return user

    def get_all_users(self):
        return self.db_session.query(User).all()