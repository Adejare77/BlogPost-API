from django.test import TestCase
from django.contrib.auth import get_user_model

class CommentModelTests(TestCase):
    def setUp(self):
        """set up user, post, and comments
        """
        self.user1 = get_user_model().objects.create_user(
            full_name="ABCD",
            email="testing1@gmail.com",
            password="testing123"
        )
        self.user2 = get_user_model().objects.create_user(
            full_name="RSTU",
            email="testing2@gmail.com",
            password="testing456"
        )

