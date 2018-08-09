'''Get various lds.org information in JSON.

This module provides several nicities that can help. The `Client` class is
useful to hit the endpoints directly. The `session` function provides a
context mananger capable way of using the `Client` class. It cleans up
resources on finish.
'''
from typing import Optional
from functools import lru_cache
from contextlib import contextmanager

import requests


ENDPOINTS_URL = 'https://tech.lds.org/mobile/ldstools/config.json'


class Error(Exception):
    '''Exceptions for module logic.'''


class Client:
    '''Client to get various lds.org information in JSON.

    There are a series of named endpoints which map directly to a URL.
    Some of these URLs expect to have a value such as the local unit
    number, which are handled silently behind the scenes.

    The list of available endpoints are dynamically generated. This is
    explained in `Client._retrieve_endpoints()`.
    '''

    def __init__(self, username=None, password=None):
        '''Initialize LDS client.

        Signing in can be accomplished immediately by providing the username
        and password args. If not, signing in can be accomplished by calling
        sign_in.

        Args:
            username (str): LDS.org username
            password (str): LDS.org password
        '''
        self.signed_in = False

        self._session = requests.Session()
        self._endpoints: Optional[dict] = None

        self._retrieve_endpoints()

        if username and password:
            self.sign_in(username, password)

    def _retrieve_endpoints(self):
        '''Retrieve the currently supported endpoints provided by LDS Tools.

        Also replaces endpoint parameters where appropiate.

        See https://tech.lds.org/wiki/LDS_Tools_Web_Services for details.
        '''
        res = self._session.get(ENDPOINTS_URL)
        assert res.status_code == 200

        self._endpoints = {}
        endpoints = self._endpoints
        for key, url in res.json().items():
            if not url.startswith('http'):
                continue

            endpoints[key] = url

            # Fix unit parameter
            if 'unit/%@' in url:
                url = endpoints[key] = url.replace('unit/%@', 'unit/{unit}')
            elif 'unitNumber=%@' in url:
                url = endpoints[key] = url.replace('=%@', '={unit}')
            elif key.startswith('unit-') and url.endswith('/%@'):
                url = endpoints[key] = url[:-2] + '{unit}'

            # Fix member parameter
            if 'membership-record/%@' in url:
                url = endpoints[key] = url.replace('%@', '{member}')
            elif 'photo/url/%@' in url:
                url = endpoints[key] = url.replace('url/%@', 'url/{member}')

            # Fix misc
            for pattern in ('%@', '%d', '%.0f'):
                if pattern in url:
                    url = endpoints[key] = url.replace(pattern, '{}')

    @lru_cache(maxsize=None)
    def get_unit(self):
        '''Retrieves or returns the cached unit number of the
        currently logged in user.

        Returns: (str) unit number
        '''
        assert self.signed_in

        res = self._session.get(self._endpoints['current-user-unit'])

        return res.json()['message']

    def sign_in(self, username, password):
        '''Sign in to LDS.org using a member username and password.

        Args:
            username (str): LDS.org username
            password (str): LDS.org password

        Exceptions:
            Error for invalid login

        Side effects:
            self.signed_in = True
        '''
        assert self._endpoints is not None

        url = self._endpoints['auth-url']
        res = self._session.post(url, {
            'username': username,
            'password': password
        })

        if 'etag' not in res.headers:
            raise Error('Invalid credentials')

        self.signed_in = True

    def sign_out(self):
        '''Signs out of the current session.

        Side effects:
            self.signed_out = False
        '''
        assert self.signed_in

        self.get('signout-url')

        self.signed_in = False

    def get(self, endpoint, *args, **kwargs):
        '''Get an HTTP response from endpoint a known endpoint.

        Some endpoints need substitution to create a valid URL. Usually,
        this appears as '{}' in the endpoint. By default this method will
        replace any '{unit}' with the current user's unit number.

        Args:
            endpoint (str): endpoint or URL
            args (tuple): substituation for any '{}' in the endpoint
            kwargs (dict): unit, paramaters for :meth:`requests.Session.get`
                member: member number

        Returns:
            :class: requests.Response

        Exceptions:
            Error for unknown endpoint
            KeyError for missing endpoint keyword arguments
        '''
        if endpoint not in self._endpoints:
            raise Error('Unknown endpoint', endpoint)

        kwargs['unit'] = self.get_unit()

        url: str = self._endpoints[endpoint]
        url = url.format(*args, **kwargs)

        return self._session.get(url)


@contextmanager
def session(username=None, password=None):
    '''Provides class `Client` as a context managed resource.

    If `username` and `password` are not provided, `Client.sign_in()` must
    be called before using the client.

    Example:
    >>> with session('user', 'pass') as lds_client:
    ...     res = lds.get(....)

    or

    >>> with session() as lds_client:
    ...     lds_client.sign_in('user', 'pass')
    ...     res = lds.get(....)
    '''
    client = Client(username, password)
    try:
        yield client
    finally:
        client.sign_out()


# This module can be used from the command line to collect and examine
# the returned data in either a pretty printed format or JSON by using
# the commandline option '-j'.

# Examples:
#     See all the published endpoints.
#     $ python -m lds_org

#     See callings with peoples names
#     $ python -m lds_org -e callings-with-dates

#     Export username and password to the environment to prevent system
#     from asking for them.
#     $ export LDSORG_USERNAME = your username
#     $ export LDSORG_PASSWORD = 'your password'

#     List of members who have moved in within the last X months.  This is
#     a case where we need to provide extra information, the number of
#     months.  Simply add it to the command line.
#     $ python -m lds_org -e members-moved-in 2

#     Get the URL to a members photo.  First you need to know the members
#     ID number.  Get your current membership number
#     $ python -m lds_org -e current-user-id
#     $ python -m lds_org -e photo-url -m memberID individual
# if __name__ == '__main__':  # pragma: no cover
#     import sys
#     import argparse
#     import getpass
#     import json

#     def main():
#         '''Remove module execution variables from globals.'''
#         parser = argparse.ArgumentParser()
#         parser.add_argument('-e', metavar='ENDPOINT',
#                             help='Endpoint to pretty print')
#         parser.add_argument('-m', metavar='MEMBER', default=None,
#                             help='Member number')
#         parser.add_argument('-u', metavar='UNIT', default=None,
#                             help='Unit number other than authorized users')
#         parser.add_argument('-j', action='store_true', help='output as JSON')
#         parser.add_argument('args', nargs='*',
#                             help='Arguments for endpoint URLs')
#         parser.add_argument('--log', help='Filename for log, - for stdout')
#         args = parser.parse_args()

#         if args.log:
#             if args.log == '-':
#                 h = logging.StreamHandler(sys.stdout)
#             else:
#                 h = logging.FileHandler(args.log, 'wt')
#             logger.addHandler(h)
#             logger.setLevel(logging.DEBUG)

#         lds = LDSOrg()

#         if not args.e:
#             # pprint available endoints
#             for k, v in sorted((_ for _ in lds.endpoints.items()
#                                 if _[-1].startswith('http'))):
#                 print('[{:25s}] {}'.format(k, v))
#         else:
#             username = os.getenv(ENV_USERNAME)
#             password = os.getenv(ENV_PASSWORD)
#             if not all((username, password)):
#                 logger.info('Asking for username and password.')
#                 asking = raw_input if sys.version_info.major < 3 else input
#                 username = asking('LDS.org username:')
#                 password = getpass.getpass('LDS.org password:')
#                 if not all((username, password)):
#                     print('Give username and password at input or set environment'
#                         ' %s and %s.' % (ENV_USERNAME, ENV_PASSWORD))
#                     sys.exit(1)

#             lds.signin(username, password)
#             rv = lds.get(args.e, member=args.m, unit=args.u, *args.args)
#             if rv.status_code != 200:
#                 print('Error: %d %s' % (rv.status_code, str(rv)))
#             content_type = rv.headers['content-type']
#             if 'html' in content_type:
#                 print('<!-- %s -->' % str(rv))
#                 print('<!-- %s -->' % rv.url)
#                 print(rv.text)
#             elif 'json' in content_type:
#                 if not args.j:
#                     pprint.pprint(rv.json())
#                 else:
#                     print(json.dumps(rv.json(), sort_keys=True))
#     main()
