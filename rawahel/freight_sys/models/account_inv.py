# -*- coding: utf-8 -*-

from odoo import fields, models, api

'''
Created on May 22, 2018

@author: iheb
'''
class AccountInvoiveLine(models.Model):
    _inherit = 'account.invoice.line'
    
    policy_line_id = fields.Many2one('freight_sys.policy.line')
