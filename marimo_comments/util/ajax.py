""" functions and decorators that are useful for responding to ajax requests.
"""

import json

from django.http import HttpResponse

def ajax_resp(status, content):
    """
    Convenience wrapper around HttpResponse that serializes a passed in array
    or dictionary into json and sets the mime type accordingly.

    :param status: numerical HTTP status code
    :param content: a collection that can be serialized as json
    :returns: HttpResponse
    """
    return HttpResponse(status=status, content=json.dumps(content), content_type="application/json")

def ajax_error(status, error_msg):
    """
    Wrapper around ajax_resp. Returns JSON that represents an error. Intended
    to be consumed by javascript that will react to the error in a useful way.

    :param status: a numerical HTTP status code
    :param error_msg: a string used to create an object like {'error':error_msg}
    :returns: HttpResponse
    """
    return ajax_resp(status, {'error':error_msg})

def ajax_only(fun):
    """
    View decorator that will require a view to be accessed only via ajax. Uses
    ajax_error to respond to nonajax request.
    """
    def wrapper(request, *args, **kwargs):
        if not request.is_ajax():
            return ajax_error(404, 'ajax_only')
        return fun(request, *args, **kwargs)

    return wrapper


def ajax_auth_required(fun):
    """
    View decorator that will require a view to be accessed by an authenticated
    user. Uses ajax_error to respond to nonauthenticated requests.
    """
    def wrapper(*args, **kwargs):
        if not args[0].user.is_authenticated():
            return ajax_error(403, 'login_required')
        return fun(*args, **kwargs)

    return wrapper

def ajax_method(method):
    """
    View decorator that will require a view to be accessed only by the
    specified method. Uses ajax_error to respond to noncomplying requests.

    :param method: a string like 'GET' or 'POST'
    """
    def decorator(fun):
        def wrapper(*args, **kwargs):
            if args[0].method.lower() != method.lower():
                return ajax_error(404, 'bad_method')
            return fun(*args, **kwargs)
        return wrapper

    return decorator

def ajax_required_data(keys):
    """
    View decorator that will check a request's POST dictionary for the
    existence of the specified keys.

    :param keys: list of keys like ['content_type_id', 'object_id']
    """
    def decorator(fun):
        def wrapper(*args, **kwargs):
            req = args[0]
            for key in keys:
                if not key in req.POST:
                    return ajax_error(400, 'missing_data')
            return fun(*args, **kwargs)
        return wrapper

    return decorator
