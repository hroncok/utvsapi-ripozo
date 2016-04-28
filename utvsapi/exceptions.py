from ripozo.exceptions import *


class UnauthorizedException(RestException):
    '''
    This exception is raised when the request equires user authentication
    but it was not provided
    '''
    def __init__(self, message, status_code=401, *args, **kwargs):
        super().__init__(message, status_code=status_code, *args, **kwargs)


class ForbiddenException(RestException):
    '''
    This exception is raised when the request is not authorized to see the data
    '''
    def __init__(self, message, status_code=403, *args, **kwargs):
        super().__init__(message, status_code=status_code, *args, **kwargs)
