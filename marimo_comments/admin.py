"""
Admin action for marimo comments
"""
from django.contrib import admin

from marimo_comments.models import MarimoComment, MarimoCommentBucket


class MarimoCommentBucketAdmin(admin.ModelAdmin):

    list_display = ('content_object', 'content_type', 'object_id', 'originating_site',)
    list_filter = ('originating_site', 'content_type',)

admin.site.register(MarimoCommentBucket, MarimoCommentBucketAdmin)


class MarimoCommentAdmin(admin.ModelAdmin):

    list_display = ('bucket', 'user', 'text', 'submit_date', 'originating_site',)
    list_filter = ('submit_date',)

    raw_id_fields = ('bucket', 'user',)

admin.site.register(MarimoComment, MarimoCommentAdmin)
