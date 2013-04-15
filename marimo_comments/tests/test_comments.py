""" test_comments.py """
from unittest import TestCase

from django.contrib.auth.models import User


class MarimoCommentTest(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'Bob',
            'email': 'bob@haro.com',
        }
        self.user = User(**self.user_data)

    def test_comment_model(self):
        assert self.user.username == self.user_data['username']
