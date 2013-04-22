import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

from marimo_comments import constants

COMMENT_MAX_LENGTH = 3000


class MarimoCommentBucket(models.Model):
    """
    A container for organizing comments which links to the content object for a particular site
    """

    # Content-object field
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")

    # Metadata about the comment
    originating_site = models.ForeignKey(Site)

    class Meta:
        ordering = ('originating_site', 'content_type',)
        unique_together = (('originating_site', 'content_type', 'object_id'),)
        verbose_name = _('bucket')
        verbose_name_plural = _('buckets')

    def __unicode__(self):
        """ human readable name """
        return u'{0}:{1}'.format(self.content_type, self.object_id)


class MarimoComment(models.Model):
    """ A user comment. It lives in a bucket. """

    bucket = models.ForeignKey(MarimoCommentBucket, verbose_name=_('bucket'),
                               related_name="marimocomments")

    # Who posted this comment?
    user = models.ForeignKey(User, verbose_name=_('user'),
                             blank=True, null=True, related_name="marimocomments")

    text = models.TextField(max_length=COMMENT_MAX_LENGTH)

    # Metadata about the comment
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    ip_address = models.IPAddressField(_('IP address'), blank=True, null=True)
    is_edited = models.BooleanField(_('is edited'), default=False)

    class Meta:
        ordering = ('submit_date', 'bucket')
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __unicode__(self):
        """ human readable name """
        return u'{0} {1}'.format(self.bucket, self.user)

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = datetime.datetime.now()
        super(MarimoComment, self).save(*args, **kwargs)

    @property
    def originating_site(self):
        return self.bucket.originating_site

    def _get_userinfo(self):
        """
        Get a dictionary that pulls together information about the poster
        safely

        This dict will have ``name`` and possibly ``email`` fields.
        """
        if not hasattr(self, "_userinfo"):
            self._userinfo = {}
            if self.user is not None:
                u = self.user
                if u.email:
                    self._userinfo["email"] = u.email

                # If the user has a full name, use that for the user name.
                if u.get_full_name():
                    self._userinfo["name"] = self.user.get_full_name()
                else:
                    self._userinfo["name"] = u.username
        return self._userinfo
    userinfo = property(_get_userinfo, doc=_get_userinfo.__doc__)

    def _get_name(self):
        return self.userinfo["name"]
    name = property(_get_name, doc="The name of the user who posted this comment")

    def _get_email(self):
        return self.userinfo["email"]
    email = property(_get_email, doc="The email of the user who posted this comment")

    def get_page_number(self):
        """Return the 1-based page # that this comment is displayed on"""
        comments_before_this_one = MarimoComment.objects.filter(bucket=self.bucket,
                                                                submit_date__lt=self.submit_date)
        return 1 + (comments_before_this_one.count() / constants.COMMENTS_PER_PAGE)
