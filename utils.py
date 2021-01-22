import uuid

import jwt

from authentication.utils import get_current_time
from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):
    payload = {
        'user_id': user.pk,
        'date': str(get_current_time())
    }
    if isinstance(user.pk, uuid.UUID):
        payload['user_id'] = str(user.pk)
    return payload
