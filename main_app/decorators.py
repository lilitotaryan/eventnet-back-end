from functools import wraps

from authentication.errors import AuthException, ValidationError
from authentication.utils import response
from user_crud.errors import UserCrudException


def error_handler(func):
    @wraps(func)
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (AuthException, UserCrudException, ValidationError) as e:
            return response(errors=[e.serialize()], success=False)
    return inner_function
