from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=1000)

    class Meta:
        verbose_name = _('entry')
        verbose_name_plural = _('entries')

    def __unicode__(self):
        return self.title
