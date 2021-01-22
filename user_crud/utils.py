import uuid
from enum import Enum

def uuid_hash(address1, city, address2, state, country):
    return uuid.uuid3(uuid.NAMESPACE_DNS, address1 + city + address2 + state + country)
