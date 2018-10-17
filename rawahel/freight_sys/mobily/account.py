"""
Copyright (c) 2016 Mobily.ws
Code by Lucas Thompson

Class wrapping the Mobily API methods for managing account details

"""
from ..mobily.utilities import MobilyApiJsonRequestHandler



class MobilyAccount(object):
    def __init__(self, auth):
        self.auth = auth

    def change_password(self, new_password):
        # changePassword api method wrapper
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('changePassword')
        request_handler.add_parameter('newPassword', new_password)
        return request_handler.handle()

    def forgot_password(self, send_to_email=True):
        # forgotPassword api method wrapper
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_type = 2 if send_to_email else 1
        request_handler.set_api_method('forgetPassword')
        request_handler.add_parameter('type', request_type)
        return request_handler.handle()

    def check_balance(self):
        # balance api method wrapper
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('balance')
        return request_handler.handle().get('balance')
