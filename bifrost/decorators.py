from graphql_jwt.decorators import *  # noqa
from graphql_jwt.decorators import context
from graphql_jwt import exceptions
from functools import wraps
from graphql.execution.base import ResolveInfo


def operation_passes_test(test_func, exc=exceptions.PermissionDenied):
    def decorator(f):
        @wraps(f)
        @context(f)
        def wrapper(context, root, info, input, *args, **kwargs):
            if test_func(context.user, input):
                return f(root, info, input, *args, **kwargs)
            raise exc

        return wrapper

    return decorator
