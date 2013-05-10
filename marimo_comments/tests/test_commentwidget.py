import datetime
import json
from unittest import TestCase

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.http import HttpRequest

from mockito import mock, when

from marimo_comments.models import MarimoCommentBucket, MarimoComment
from marimo_comments.util.mocks import MockCache
from marimo_comments.views import update_count_cache, post, get_page_and_comment_counts


class CommentsWidgetTest(TestCase):

    def setUp(self):
        self.user_data = {
            'pk': 1,
            'username': 'bharo',
            'email': 'bob@haro.com',
        }
        self.user = User(**self.user_data)
        self.site = Site(pk=1, name='foo', domain='www.foo.com')
        self.datetime = datetime.datetime(2010, 12, 13, 10, 15, 0)
        self.flatpage = FlatPage(pk=1, title='test', content='my entry blah blah blah')
        self.test_content_type = ContentType(pk=101, name='Entry', app_label='example', model='entry')
        self.bucket = MarimoCommentBucket(pk=1, content_type=self.test_content_type,
                                          object_id=self.flatpage.pk, originating_site=self.site)
        self.comment = MarimoComment(pk=1, text='Test Comment', bucket=self.bucket, user=self.user,
                                     submit_date=self.datetime)

        self.ajax_req = HttpRequest()
        self.ajax_req.method = 'POST'
        self.ajax_req.is_ajax = lambda: True

        self.mc = MockCache()

    def test_update_count_cache(self):
        when(MarimoCommentBucket.objects).get(content_type__id=self.test_content_type.pk,
                                              object_id=self.flatpage.pk,
                                              originating_site__id=self.site.pk).thenReturn(self.bucket)

        qs = mock()
        when(qs).count().thenReturn(1)
        when(MarimoComment.objects).filter(bucket=self.bucket).thenReturn(qs)

        (total_comments, total_pages) = update_count_cache(self.bucket.content_type_id, self.bucket.object_id, self.site.id)

        assert total_comments == 1 and total_pages == 1

    def test_posting(self):
        """
        Use the view as a standalone function by passing it a bare-minimum
        HttpRequest object. Check that the comment's data is returned as json
        and that the cache was refreshed.
        """
        self.mc.set = mock()
        with mock('marimo.views.base.cache') as self.mc:
            comment_text = '''First: The Library exists ab aeterno. This truth,
            whose immediate corollary is the future eternity of the world, cannot
            be placed in doubt by any reasonable mind.'''
            self.ajax_req.user = self.user
            self.ajax_req.POST['content_type_id'] = self.bucket.content_type_id
            self.ajax_req.POST['object_id'] = self.bucket.object_id
            self.ajax_req.POST['site_id'] = self.site.id
            self.ajax_req.POST['text'] = comment_text

            when(MarimoCommentBucket.objects).get(content_type__id=self.test_content_type.pk,
                                                  object_id=self.flatpage.pk,
                                                  originating_site__id=self.site.pk).thenReturn(self.bucket)

            qs = mock()
            when(qs).count().thenReturn(1)
            when(MarimoComment.objects).filter(bucket=self.bucket).thenReturn(qs)

            resp = post(self.ajax_req)
            result = json.loads(resp.content)

            self.assertEquals(resp.status_code, 200)
            comment_id = result['cid']
            comment = MarimoComment.objects.get(id=comment_id)
            self.assertEquals(comment.text, comment_text)

            (total_comments, total_pages) = get_page_and_comment_counts(self.bucket.content_type_id, self.bucket.object_id, self.site.id)
            self.assertEquals(total_comments, 1)
