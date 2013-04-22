"""
Helpful data
"""

COMMENTS_DISABLED_STATUS = 1
COMMENTS_FROZEN_STATUS = 2
COMMENTS_DEFAULT_STATUS = 3
COMMENTS_ENABLED_STATUS = 4
COMMENTS_DEFERRED_STATUS = 5

comment_choices = (
    (COMMENTS_DEFAULT_STATUS, 'Default'),
    (COMMENTS_DISABLED_STATUS, 'Disabled'),
    (COMMENTS_FROZEN_STATUS, 'Frozen'),
    (COMMENTS_ENABLED_STATUS, 'Enabled'),
)

comment_help_text = """ "Default" will defer to the the medley comment rules<br />
                        "Disabled" will not allow comments for this content.<br />
                        "Frozen" will display existing comments, but disallow new comments.<br />
                        "Enabled" will allow new comments and disregard any rules."""

COMMENTS_PER_PAGE = 20
