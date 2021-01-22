import uuid
from enum import Enum

def id_generator():
    return uuid.uuid4().int // pow(10,30)

# class BaseEnum(Enum):
#     @classmethod
#     def members(cls):
#         for i in cls:
#             return i.value, i.name
#
#     @classmethod
#     def format(cls, value):
#         return cls(value).name


# class PaymentStateEnum(BaseEnum):
#     FAIL = 0
#     PENDING = 1
#     DONE = 2


class PaymentReason(Enum):
    BUY_TICKET = 0
    PAY_FOR_FREE_EVENT = 1

    @classmethod
    def members(cls):
        return [(e.value, e.name) for e in cls]

    @classmethod
    def format(cls, value):
        return cls(value).name

