"""
    Marimo Comments App

    A 'buckets' based approach to organizing comments

    With standard django comments each comment instance has a GFK to an object for a particular site. This makes
    querying for them hard to do efficiently and perform well. Instead of that, for each content object, by site,
    you'll have one 'bucket' which has the GFK back to the content object. Then each comment instance will simply have a
    regular foreign key back to the bucket. This allow us to gather up all the comments for a particular piece of content
    on a site with a lot less queries.

"""