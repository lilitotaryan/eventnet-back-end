from main_app.errors import MainAppException


class UserCrudException(MainAppException):
    default_code = "user_crud_errors"


class UserAlreadyExists(UserCrudException):
    def __init__(self):
        super().__init__(code=5,
                         message='User already exists.',
                         default_code='user_exists')


class UserDataNotValid(UserCrudException):
    def __init__(self):
        super().__init__(code=6,
                         message='User Data is not Valid.',
                         default_code='user_data_not_valid')


class CompanyUserShouldHaveName(UserCrudException):
    def __init__(self):
        super().__init__(code=7,
                         message='CompanyUser should have name specified.',
                         default_code='company_user_should_have_name')


class AddressAlreadyExists(UserCrudException):
    def __init__(self):
        super().__init__(code=8,
                         message='Address already exists.',
                         default_code='address_exists')


class AddressDataNotValid(UserCrudException):
    def __init__(self):
        super().__init__(code=9,
                         message='Address data is not valid.',
                         default_code='address_data_not_valid')


class UserHasNoAddress(UserCrudException):
    def __init__(self):
        super().__init__(code=10,
                         message='User has no added address.',
                         default_code='user_has_no_address')


class UserHasAddress(UserCrudException):
    def __init__(self):
        super().__init__(code=11,
                         message='User already have registered the address.',
                         default_code='user_has_address')


class CategoryDataNotValid(UserCrudException):
    def __init__(self):
        super().__init__(code=12,
                         message='Category data is not valid.',
                         default_code='category_data_not_valid')


class CategoryNotFound(UserCrudException):
    def __init__(self):
        super().__init__(code=13,
                         message='Specified category is not found.',
                         default_code='category_is_not_found')


class UserHasNoCategory(UserCrudException):
    def __init__(self):
        super().__init__(code=14,
                         message='User has no selected categories.',
                         default_code='user_has_no_categories')


class CategoriesNotFound(UserCrudException):
    def __init__(self):
        super().__init__(code=15,
                         message='No categories found.',
                         default_code='no_categories_found')

class CannotDeleteUserHavingEvents(UserCrudException):
    def __init__(self):
        super().__init__(code=16,
                         message='Cannot delete user that has non responsible event.',
                         default_code='cannot_delete_user_having_events')