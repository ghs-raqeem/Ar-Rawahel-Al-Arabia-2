"""
Copyright (c) 2016 Mobily.ws
Code by Lucas Thompson

Utility functions to support the Mobily API.
"""
import sys
import http.client
import json


class MobilyApiUnicodeConverter(object):
    @staticmethod
    def convert(message):
        return ''.join(['{:04x}'.format(ord(byte)).upper() for byte in u(message)])


def u(s):
    if sys.version_info < (3,) and type(s) is str:
        return unicode(s, 'utf-8')
    else:
        return s


class MobilyApiAuth(object):
    def __init__(self, mobile_number, password):
        self.mobile_number = mobile_number
        self.password = password


class MobilyApiResponse(object):
    def __init__(self, status, response_status):
        self.status = status
        self.response_status = response_status.lower()
        self.data = {}

    def add_data(self, key, value):
        self.data.update({u(key): u(value)})

    def get(self, key):
        return self.data[key] if key in self.data else None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class MobilyApiError(Exception):
    """Exception raised when an a RequestHandler indicates the request failed.

    Attributes:
        code         -- the error code returned from the API
        msg_arabic   -- explanation of the error in Arabic
        msg_english  -- explanation of the error in English
    """

    def __init__(self, code, msg_arabic, msg_english):
        super(MobilyApiError, self).__init__(msg_english, )
        self.code = code
        self.msg_arabic = msg_arabic
        self.msg_english = msg_english


class MobilyApiRequest(object):
    def __init__(self, api_host='www.mobily.ws', api_end_point='/api/'):
        self.api_host = api_host
        self.api_end_point = api_end_point

    def send(self, request_data, content_type):
        headers = {'Content-type': 'application/{0}; charset=utf-8'.format(content_type)}
        conn = http.client.HTTPConnection(self.api_host)
        conn.request('POST', self.api_end_point, request_data, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data


class MobilyApiJsonRequestHandler(object):
    def __init__(self, auth=None, request=MobilyApiRequest(api_end_point='/api/json/')):
        self.request = request
        self.params = {}
        self.content_type = 'json'
        self.json_dict = {'Data': {}}
        self.auth = auth

    def add_auth(self, auth):
        if isinstance(auth, MobilyApiAuth):
            self.json_dict['Data'].update({'Auth': {'mobile': auth.mobile_number, 'password': auth.password}})

    def set_api_method(self, method_name):
        self.json_dict['Data'].update({'Method': method_name})

    def add_parameter(self, key, value):
        if value is not None:
            self.params.update({key: value})

    def get_request_data(self):
        if len(self.params) > 0:
            self.json_dict['Data'].update({'Params': self.params})
        self.add_auth(self.auth)
        return json.dumps(self.json_dict)

    def handle(self):
        return self._parse_response(self.request.send(self.get_request_data(), self.content_type))

    @staticmethod
    def _parse_response(data):
        json_dict = json.loads(data.decode('utf-8'))
        is_error = json_dict['Error'] is not None
        if is_error:
            error = json_dict['Error']
            raise MobilyApiError(error['ErrorCode'], error['MessageAr'], error['MessageEn'])
        response = MobilyApiResponse(json_dict['status'], json_dict['ResponseStatus'])
        for key, value in json_dict['Data'].items():
            response.add_data(key, value)
        return response
