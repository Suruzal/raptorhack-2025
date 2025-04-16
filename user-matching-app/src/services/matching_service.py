class MatchingService:
    def __init__(self, user_service, gemini_api):
        self.user_service = user_service
        self.gemini_api = gemini_api

    def find_study_partners(self, user_id):
        user = self.user_service.get_user(user_id)
        if not user:
            return []

        potential_partners = self.user_service.get_all_users()
        matches = []

        for partner in potential_partners:
            if partner.id != user.id:
                shared_classes = self.compare_classes(user.classes, partner.classes)
                complementary_strengths = self.compare_strengths(user.strengths, partner.weaknesses)

                if shared_classes or complementary_strengths:
                    matches.append({
                        'partner_id': partner.id,
                        'shared_classes': shared_classes,
                        'complementary_strengths': complementary_strengths
                    })

        return matches

    def compare_classes(self, user_classes, partner_classes):
        return set(user_classes).intersection(set(partner_classes))

    def compare_strengths(self, user_strengths, partner_weaknesses):
        return set(user_strengths).intersection(set(partner_weaknesses))