"""
Copyright (c) 2016 Mobily.ws
Code by Lucas Thompson

Class wrapping the Mobily API methods for adding senders

"""
from ..mobily.utilities import MobilyApiJsonRequestHandler, MobilyApiError


class MobilySender(object):
    def __init__(self, auth):
        self.auth = auth

    def request_mobile_number_license(self, mobile_number):
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('addSender')
        request_handler.add_parameter('sender', mobile_number)
        response = request_handler.handle()
        return response.get('senderId')

    def activate_mobile_number_license(self, sender_id, activation_code):
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('activeSender')
        request_handler.add_parameter('senderId', sender_id.strip('#'))
        request_handler.add_parameter('activeKey', activation_code)
        return request_handler.handle()

    def is_mobile_number_license_active(self, sender_id):
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('checkSender')
        request_handler.add_parameter('senderId', sender_id.strip('#'))
        try:
            response = request_handler.handle()
        except MobilyApiError:
            return False
        else:
            return response.get('result') == '1'

    def request_alphabetical_license(self, sender):
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('addAlphaSender')
        request_handler.add_parameter('sender', sender)
        return request_handler.handle()

    def get_activation_status_for_all_senders(self):
        request_handler = MobilyApiJsonRequestHandler(self.auth)
        request_handler.set_api_method('checkAlphasSender')
        return request_handler.handle().data
