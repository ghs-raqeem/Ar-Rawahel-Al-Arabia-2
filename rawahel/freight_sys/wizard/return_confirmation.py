# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class SignatureWizard(models.TransientModel):
    _name = 'freight_sys.confirm_return_policy'
    
    yes_no = fields.Char(default=_('Are you sure to return this policy !!!'))

    @api.multi
    def yes(self):
        return True

    @api.multi
    def no(self):
        return False
                        
                    
                
                
        
        
        
        