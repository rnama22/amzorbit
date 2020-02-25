"""
    This file contains all the custom exceptions.
    All custom exceptions are inherited from BaseError
"""


class BaseError(Exception):
    """ Base class for all Fullcast custom exceptions"""

    def __init__(self, message):
        super(BaseError, self).__init__(message)
        self.message = message


class ValidationError(BaseError):
    """ Class for all validation related exceptions"""

    def __init__(self, message='Validation Error'):
        super(ValidationError, self).__init__(message)


class AuthenticationError(BaseError):
    """ Class for all authentication related exceptions"""

    def __init__(self, message='Authentication Error'):
        super(AuthenticationError, self).__init__(message)


class AuthorizationError(BaseError):
    """ Class for all authorization related exceptions"""

    def __init__(self, message='AuthorizationError Error'):
        super(AuthorizationError, self).__init__(message)


class NotFoundError(BaseError):
    """ Class for objects not found exceptions"""

    def __init__(self, message='Not Found Error'):
        super(NotFoundError, self).__init__(message)


class MissingFieldError(BaseError):
    """ Class for fields missing exceptions"""

    def __init__(self, message='Not Found Error'):
        super(MissingFieldError, self).__init__(message)


class IllegalAssignmentError(BaseError):
    """ Class for illegal assignments exceptions"""

    def __init__(self, message='Illegal Assignment Error'):
        super(IllegalAssignmentError, self).__init__(message)


class IllegalArgumentError(BaseError):
    """ Class for illegal argument exceptions"""

    def __init__(self, message='Illegal Argument Error'):
        super(IllegalArgumentError, self).__init__(message)


class SparkError(BaseError):
    """ Class for all spark related exceptions"""

    def __init__(self, message='Spark Error'):
        super(SparkError, self).__init__(message)


class PackageNotFound(Exception):
    pass
