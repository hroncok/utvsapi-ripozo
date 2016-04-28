from utvsapitoken import TokenClient

from utvsapi import exceptions


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
    c = TokenClient(check_token_uri='http://localhost:8080/token',
                    usermap_uri='http://localhost:8080/user')
    info = None
    try:
        info = c.token_to_info(token)
    except:
        raise exceptions.UnauthorizedException('Token not valid. '
                                               'Please provide a valid token.')

    # default behavior for all of our resources
    if 'cvut:utvs:general:read' not in info['scope']:
        raise exceptions.ForbiddenException('Permission denied. '
                                            'You need '
                                            'cvut:utvs:general:read scope.')

    # add the information to the request, for further pre/postprocessors
    request.client_info = info
