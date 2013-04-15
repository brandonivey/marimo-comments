marimo-comments
=============

fast, efficient commenting application which can be used on high volume sites
-----------------------------------------------------------------------------

Marimo Comments is a replacement for Django's comments application. Regular django comments
are slow and inefficient to search for because they rely on individual generic foreign keys
to point to the content object. Marimo Comments uses a 'bucket' object which has the gfk to
the content object and the 'comment' objects just have a hard foreign key to the 'bucket'.
This makes queries much faster. 

For the front-end, Marimo Comments uses the Marimo widget framework/tools here

https://github.com/coxmediagroup/marimo

and django-marimo to wire marimo into the django views

https://github.com/coxmediagroup/django-marimo
