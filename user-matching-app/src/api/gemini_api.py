class GeminiAPI:
    def __init__(self):
        # Initialize any required API keys or configurations
        self.api_key = "your_gemini_api_key_here"
        self.api_secret = "your_gemini_api_secret_here"

    def get_user_matches(self, user_id, database_connection):
        # Fetch user data from the database
        user = database_connection.get_user_by_id(user_id)
        if not user:
            return []

        # Fetch all users from the database
        all_users = database_connection.get_all_users()
        matches = []

        for potential_match in all_users:
            if potential_match.id != user.id:
                # Compare classes
                shared_classes = set(user.classes).intersection(set(potential_match.classes))
                # Compare strengths and weaknesses
                complementary_strengths = set(user.strengths).intersection(set(potential_match.weaknesses))
                complementary_weaknesses = set(user.weaknesses).intersection(set(potential_match.strengths))

                if shared_classes and (complementary_strengths or complementary_weaknesses):
                    matches.append({
                        'user_id': potential_match.id,
                        'shared_classes': list(shared_classes),
                        'complementary_strengths': list(complementary_strengths),
                        'complementary_weaknesses': list(complementary_weaknesses)
                    })

        return matches

    def compare_users(self, user_id_1, user_id_2, database_connection):
        user_1 = database_connection.get_user_by_id(user_id_1)
        user_2 = database_connection.get_user_by_id(user_id_2)

        if not user_1 or not user_2:
            return None

        comparison = {
            'user_1': {
                'id': user_1.id,
                'classes': user_1.classes,
                'strengths': user_1.strengths,
                'weaknesses': user_1.weaknesses
            },
            'user_2': {
                'id': user_2.id,
                'classes': user_2.classes,
                'strengths': user_2.strengths,
                'weaknesses': user_2.weaknesses
            },
            'shared_classes': list(set(user_1.classes).intersection(set(user_2.classes))),
            'complementary_strengths': list(set(user_1.strengths).intersection(set(user_2.weaknesses))),
            'complementary_weaknesses': list(set(user_1.weaknesses).intersection(set(user_2.strengths)))
        }

        return comparison