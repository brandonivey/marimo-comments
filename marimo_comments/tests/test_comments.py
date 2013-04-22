""" test_comments.py """
import datetime
from unittest import TestCase

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from example.models import Entry
from marimo_comments.models import MarimoCommentBucket, MarimoComment


class MarimoCommentTest(TestCase):

    def setUp(self):
        self.user_data = {
            'username': 'bharo',
            'email': 'bob@haro.com',
        }
        self.user = User(**self.user_data)
        self.site = Site(name='foo', domain='www.foo.com')
        self.datetime = datetime.datetime(2010, 12, 13, 10, 15, 0)
        self.entry = Entry(title='test', content='my entry blah blah blah')
        self.bucket = MarimoCommentBucket(content_object=self.entry, originating_site=self.site)
        self.comment = MarimoComment(text='Test Comment', bucket=self.bucket, user=self.user,
                                     submit_date=self.datetime)

    def test_bucket_content_type(self):
        ct = ContentType.objects.get_for_model(self.entry)
        assert self.bucket.content_type_id is ct.id

    def test_comment_userinfo(self):
        assert self.comment.userinfo['name'] == self.user_data['username']

    def test_comment_userinfo_email(self):
        assert self.comment.userinfo['email'] == self.user_data['email']
        assert self.comment.email == self.user_data['email']

    def test_comment_userinfo_with_first_last(self):
        self.user.first_name = 'Bob'
        self.user.last_name = 'Haro'
        assert self.comment.userinfo['name'] == 'Bob Haro'
        assert self.comment.name == 'Bob Haro'

    def test_get_page_number(self):
        from mockito import mock, when
        mock_objects = mock()
        mock_query_set = mock()
        MarimoComment.objects = mock_objects
        when(mock_objects).filter(bucket=self.bucket, submit_date__lt=self.datetime).thenReturn(mock_query_set)
        when(mock_query_set).count().thenReturn(19)

        assert self.comment.get_page_number() == 1
