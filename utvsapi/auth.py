from utvsapi import exceptions


def token_to_info(token, credentials=None):
    '''
    This is a placeholder function that mimics
    a soon to be made oauth2 token validation and
    a request to userpmap api for personal number.

    If the token is a number, it will pretend
    the token is valid and belongs to an user with such personal number.

    If the token is GODGODGOD, it will pretend the token is valid
    and belongs to a client that can read everything.

    If the token is anything different, it will pretend it is not valid.
    '''
    info = {}
    scopes = ['cvut:utvs:general:read']
    try:
        info['personal_number'] = int(token)
        info['scopes'] = scopes + ['cvut:utvs:enrollments:by-role']
    except ValueError:
        if token == 'GODGODGOD':
            info['scopes'] = scopes + ['cvut:utvs:enrollments:all']
    return info


def headers_to_token(headers, *, authorization='authorization',
                     bearer='Bearer '):
    '''
    Get the auth token form the headers

    Returns None if not found
    '''
    if authorization in headers:
        header = headers[authorization]
        if header.startswith(bearer):
            return header[len(bearer):].strip()


def preprocessor(cls, function_name, request):
    if getattr(request, 'bypass_auth', False):
        return
    token = headers_to_token(request.headers)
    if not token:
        raise exceptions.UnauthorizedException('Token not provided. '
                                               'Use the following header: '
                                               'Authorization: Bearer {token}')
    info = token_to_info(token)
    if not info:
        raise exceptions.UnauthorizedException('Token not valid. '
                                               'Please provide a valid token.')

    # add the information to the request
    request.client_info = info


def postprocessor(cls, function_name, request, resource):
    if getattr(request, 'bypass_auth', False):
        return
    if not cls.permission_func(function_name, request, resource):
        raise exceptions.ForbiddenException('Permission denied.')
