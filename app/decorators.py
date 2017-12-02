from flask import abort
from flask_login import current_user

from .models import Permission

from functools import wraps


def permission_required(permission):
    """
    a permission check decorator
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
