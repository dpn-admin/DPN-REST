import json
from os.path import normpath
from http.client import HTTPSConnection, HTTPConnection
from urllib.parse import urlencode, urlparse

class APIException(Exception):
    pass

class APIClient:
    """
    A basic client to query the DPN REST API.
    """

    def __init__(self, url, api_token):
        self.set_token(api_token)
        self.headers = {
            'Authorization': "Token %s" % self.api_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self._set_conn(url)

    def _set_conn(self, url):
        """
        Parses the url and sets connection details and path information for the
        client.

        :param url: String of the url to use as the root for API calls.
        :return: None
        """
        url = urlparse(url)
        self.baseurl = url.netloc
        self.basepath = url.path
        if url.scheme == 'https':
            conn = HTTPSConnection
        elif url.scheme == 'http':
            conn = HTTPConnection
        else:
            raise APIException("Unsupported protocol %s" % url.scheme)

        self.conn = conn(self.baseurl)

    def set_token(self, token):
        self.api_token = token

    def _get_path(self, path):
        url = normpath("%s%s" % (self.basepath, path))
        url = url.replace('//', '/')
        if path.endswith('/'):
            url += '/'
        return url

    def _request(self, method, path, data=None, params=None):
        url = self._get_path(path)
        if params:
            url = "%s?%s" % (url, urlencode(params))
        self.conn.request(method, url, body=json.dumps(data), headers=self.headers)
        return self.conn.getresponse()

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def post(self, path, data=None):
        return self._request('POST', path, data=data)

    def put(self, path, data=None):
        return self._request('PUT', path, data=data)

    def patch(self, path, data=None):
        return self._request('PATCH', path, data=data)

    def delete(self, path):
        return self._request('DELETE', path)
