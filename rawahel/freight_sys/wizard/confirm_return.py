# -*- coding: utf-8 -*-
'''
Created on May 15, 2018

@author: iheb
'''
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ConfirmReturn(models.TransientModel):
    _name = 'freight_sys.confirm_return'
    
    reason = fields.Text('Reason')
    policy_id = fields.Many2one('freight_sys.policy', 
                                default=lambda self: self.env['freight_sys.policy'].search([('id', '=', self._context.get('active_id'))]))
    def confirm_return(self):
        self.policy_id.is_returned = True
        self.policy_id.state = 'return'
        if self.reason:
            self.policy_id.reason = self.reason