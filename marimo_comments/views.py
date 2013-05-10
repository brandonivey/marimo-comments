"""
Comment Widget Views
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage

from marimo.views.base import BaseWidget
from marimo.template_loader import template_loader

from marimo_comments import constants
from marimo_comments.models import MarimoCommentBucket, MarimoComment
from marimo_comments.util.ajax import ajax_auth_required, ajax_error, ajax_only, ajax_required_data, ajax_resp

from sanitizer.templatetags.sanitizer import allowtags


class CommentsWidget(BaseWidget):
    template = template_loader.load('marimo_comments.html')

    def cache_key(self, *args, **kwargs):
        """
        There is nothing cacheable here: the content is either generated
        from in memory variables or dependent on request.user.
        """
        return None

    def cacheable(self, response, *args, **kwargs):
        """
        There is nothing cacheable here: the content is either generated
        from in memory variables or dependent on request.user.
        """
        return response

    def uncacheable(self, request, response, *args, **kwargs):
        """
        Given a request for a page of comments for some object, collect all the
        information needed to render a marimo comments widget.

        Expects to find mandatory args ``[content_type_id, object_id]``
        and an optional kwargs ``{site_id:123, page:321}``

        This results in response's context dictionary getting the following
        keys::

            content_type_id
            object_id
            site_id
            page
            comments (being a list, containing dicts with:
                comment_href
                poster
                submit_date
                submitted_ts
                text
                comment_id
            )

        Results in `total_comments` and `num_pages` being added to response's
        context dictionary.
        """

        content_type_id = args[0]
        object_id = args[1]
        site_id = kwargs.get('site_id', settings.SITE_ID)
        page = kwargs.get('page', 1)

        ct = ContentType.objects.get(pk=content_type_id)
        site = Site.objects.get(pk=site_id)

        try:
            bucket = MarimoCommentBucket.objects.get(content_type=ct, object_id=object_id, originating_site=site)
            comments = MarimoComment.objects.select_related('user').filter(bucket=bucket)
            pages = Paginator(comments, constants.COMMENTS_PER_PAGE)
            try:
                comments = pages.page(page).object_list
            except EmptyPage:
                # fall back to last page if page past end requested
                comments = pages.page(pages.num_pages).object_list
        except ObjectDoesNotExist:
            bucket = None
            comments = []

        response['context']['comments'] = [{
            # href of permalink to comment
            'comment_href': c.get_absolute_url(page),
            # screen_name or username of poster.
            'poster': c.user.username,
            # date comment was submitted
            'submit_date': c.submit_date.strftime("%l:%M %p %b. %e, %Y").replace('AM', 'a.m.').replace('PM', 'p.m.'),
            # date comment was submitted in timestamp
            'submitted_ts': int(c.submit_date.strftime('%s')),
            # text of comment
            'text': c.text,
            # comment's id for permalinking and other targeting
            'comment_id': c.pk,
        } for c in comments]

        # comment edit expiration (minutes)
        response['context']['edit_expiration'] = int(constants.EDIT_EXPIRATION)
        # number of comments per page
        response['context']['comments_per_page'] = int(constants.COMMENTS_PER_PAGE)
        # current page, 1-indexed
        response['context']['page'] = int(page)
        # used to reference in comment post form
        response['context']['content_type_id'] = content_type_id
        response['context']['object_id'] = object_id
        response['context']['site_id'] = site_id
        # url to redirect to signin
        response['context']['redirect'] = settings.LOGIN_URL

        (total_comments, total_pages) = get_page_and_comment_counts(content_type_id, object_id, site_id)

        # total number of comments
        response['context']['total_comments'] = total_comments
        # total pages (also last page since 1 indexed)
        response['context']['num_pages'] = total_pages

        return response


@ajax_only
@ajax_auth_required
@ajax_required_data(['text', 'content_type_id', 'object_id', 'site_id'])
def post(request):
    """
    Add comment for current user. Update and recache
    comments. Response contains new comment's id and page.
    """

    text = request.POST['text']
    content_type_id = int(request.POST['content_type_id'])
    object_id = int(request.POST['object_id'])
    site_id = int(request.POST['site_id'])
    ip_address = request.META.get('REMOTE_ADDR', None)

    bucket, created = MarimoCommentBucket.objects.get_or_create(
        content_type_id=content_type_id, object_id=object_id, originating_site_id=site_id)

    text = allowtags(text, 'b br')
    text = text.replace('<br />', '\n')

    comment = MarimoComment.objects.create(bucket=bucket, user=request.user, text=text, ip_address=ip_address)

    update_count_cache(content_type_id, object_id, site_id)

    comments = MarimoComment.objects.filter(bucket=bucket)
    num_pages = Paginator(comments, constants.COMMENTS_PER_PAGE).num_pages

    return ajax_resp(200, {
        'cid': comment.id,
        'cpage': num_pages,
    })


def get_page_and_comment_counts(content_type_id, object_id, site_id):
    """ reusable method to get the total comment count and page count """
    cache_key = 'medley_comments:%s:%s:%s' % (content_type_id, object_id, site_id)
    packed = cache.get(cache_key)
    if not packed:
        packed = update_count_cache(content_type_id, object_id, site_id)

    return packed


def update_count_cache(content_type_id, object_id, site_id):
    """ update the comment and page counts in cache """
    try:
        bucket = MarimoCommentBucket.objects.get(content_type__id=content_type_id, object_id=object_id, originating_site__id=site_id)
        comments = MarimoComment.objects.filter(bucket=bucket)
        pages = Paginator(comments, constants.COMMENTS_PER_PAGE)

        total_comments = comments.count()
        total_pages = pages.num_pages
    except ObjectDoesNotExist:
        total_comments = 0
        total_pages = 1

    packed = (total_comments, total_pages)
    cache_key = 'marimo_comments:%s:%s:%s' % (content_type_id, object_id, site_id)
    cache.set(cache_key, packed, settings.SHORT_CACHE_TIMEOUT)
    return packed
