# -*- coding: utf-8 -*-

from ..mobily.utilities import MobilyApiAuth
from ..mobily.account import MobilyAccount
from ..mobily.sms import MobilySMS, MobilyFormattedSMS
from ..mobily.sender import MobilySender
from ..mobily.utilities import MobilyApiError


def example_01_check_can_send():
    if MobilySMS.can_send():
        print ('Service is available!')
    else:
        print ('Service is not available!')


def example_02_change_pass(mobile, old_pass, new_pass):
    account = MobilyAccount(MobilyApiAuth(mobile, old_pass))
    account.change_password(new_pass)


def example_03_forgot_pass_email(mobile, password):
    account = MobilyAccount(MobilyApiAuth(mobile, password))
    account.forgot_password()


def example_04_forgot_pass_mobile(mobile, password):
    account = MobilyAccount(MobilyApiAuth(mobile, password))
    account.forgot_password(send_to_email=False)


def example_05_check_balance(mobile, password):
    account = MobilyAccount(MobilyApiAuth(mobile, password))
    balance = account.check_balance()
    print ('{0} credits available, total {1}').format(balance['current'], balance['total'])


def example_06_send_sms(mobile, password, recipient_mobile):
    sms = MobilySMS(MobilyApiAuth(mobile, password))
    sms.add_number(recipient_mobile)
    sms.sender = 'PYTHON'
    sms.msg = 'Testing تجريب ^&**\nFrom Python!'
    sms.send()


def example_07_scheduled_sms(mobile, password, recipient_mobile):
    sms = MobilySMS(MobilyApiAuth(mobile, password))
    sms.add_number(recipient_mobile)
    sms.sender = 'PYTHON'
    sms.msg = 'Testing Scheduling تجريب ^&**\nFrom Python!'
    sms.schedule_to_send_on(25, 12, 2020, 12, 0, 0)
    sms.delete_key = '666'
    sms.send()


def example_08_delete_sms(mobile, password):
    sms = MobilySMS(MobilyApiAuth(mobile, password))
    sms.delete_key = '666'
    sms.delete()


def example_09_send_formatted_sms(mobile, password, recipient_one, recipient_two):
    auth = MobilyApiAuth(mobile, password)
    msg = 'Hi (1), your subscription will end on (2).'
    sms = MobilyFormattedSMS(auth, [recipient_one, recipient_two], 'PYTHON', msg)
    sms.add_variable_for_number(recipient_one, '(1)', 'Martin')
    sms.add_variable_for_number(recipient_one, '(2)', '31/12/2017')
    sms.add_variable_for_number(recipient_two, '(1)', 'Tim')
    sms.add_variable_for_number(recipient_two, '(2)', '01/11/2020')
    sms.send()


def example_10_send_scheduled_formatted_sms(mobile, password, recipient_one, recipient_two):
    auth = MobilyApiAuth(mobile, password)
    msg = 'Hi (1), your subscription will end on (2).'
    sms = MobilyFormattedSMS(auth, [recipient_one, recipient_two], 'PYTHON', msg)
    sms.add_variable_for_number(recipient_one, '(1)', 'Grace')
    sms.add_variable_for_number(recipient_one, '(2)', '31/11/2019')
    sms.add_variable_for_number(recipient_two, '(1)', 'Mo')
    sms.add_variable_for_number(recipient_two, '(2)', '03/10/2017')
    sms.delete_key = '666'
    sms.schedule_to_send_on(25, 12, 2020, 12, 0, 0)
    sms.send()


def example_11_add_alpha_sender(mobile, password, alpha_sender):
    sender = MobilySender(MobilyApiAuth(mobile, password))
    sender.request_alphabetical_license(alpha_sender)


def example_12_list_senders(mobile, password):
    sender = MobilySender(MobilyApiAuth(mobile, password))
    senders_by_status = sender.get_activation_status_for_all_senders()
    print ('Active Senders:', [alpha_sender for alpha_sender in senders_by_status['active']])
    print ('Pending Senders:', [alpha_sender for alpha_sender in senders_by_status['pending']])
    print ('Inactive Senders:', [alpha_sender for alpha_sender in senders_by_status['notActive']])


def example_13_add_mobile_sender(mobile, password, mobile_sender):
    sender = MobilySender(MobilyApiAuth(mobile, password))
    try:
        return sender.request_mobile_number_license(mobile_sender)
    except MobilyApiError as e:
        print (e.msg_english, e.msg_arabic)


def example_14_activate_mobile_sender(mobile, password, sender_id, activation_code):
    sender = MobilySender(MobilyApiAuth(mobile, password))
    sender.activate_mobile_number_license(sender_id, activation_code)


def example_15_check_activation_status(mobile, password, sender_id):
    sender = MobilySender(MobilyApiAuth(mobile, password))
    if sender.is_mobile_number_license_active(sender_id):
        print ('Activated!')
    else:
        print ('Not activated!')
