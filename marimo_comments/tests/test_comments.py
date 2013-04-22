""" test_comments.py """
import datetime
from unittest import TestCase

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from mockito import mock, when

from example.models import Entry
from marimo_comments import constants
from marimo_comments.models import MarimoCommentBucket, MarimoComment


class MarimoCommentTest(TestCase):

    def setUp(self):
        self.user_data = {
            'pk': 1,
            'username': 'bharo',
            'email': 'bob@haro.com',
        }
        self.user = User(**self.user_data)
        self.site = Site(pk=1, name='foo', domain='www.foo.com')
        self.datetime = datetime.datetime(2010, 12, 13, 10, 15, 0)
        self.entry = Entry(pk=1, title='test', content='my entry blah blah blah')
        self.test_content_type = ContentType(pk=101, name='Entry', app_label='example', model='entry')
        self.bucket = MarimoCommentBucket(pk=1, content_type=self.test_content_type,
                                          object_id=self.entry.pk, originating_site=self.site)
        self.comment = MarimoComment(pk=1, text='Test Comment', bucket=self.bucket, user=self.user,
                                     submit_date=self.datetime)

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

    def test_get_page_number_under_page_limit(self):
        mock_query_set = mock()
        when(MarimoComment.objects).filter(bucket=self.bucket, submit_date__lt=self.datetime).thenReturn(mock_query_set)
        when(mock_query_set).count().thenReturn(constants.COMMENTS_PER_PAGE - 1)

        assert self.comment.get_page_number() == 1

    def test_get_page_number_over_page_limit(self):
        mock_query_set = mock()
        when(MarimoComment.objects).filter(bucket=self.bucket, submit_date__lt=self.datetime).thenReturn(mock_query_set)
        when(mock_query_set).count().thenReturn(constants.COMMENTS_PER_PAGE)

        assert self.comment.get_page_number() == 2

    def test_comment_get_absolute_url(self):
        when(ContentType.objects).get(id=101).thenReturn(self.test_content_type)
        when(ContentType).get_object_for_this_type().thenReturn(self.entry)
        assert '#/comment/p1/c1/' == self.comment.get_absolute_url()
