# -*- coding: utf-8 -*-

'''
Created on Apr 6, 2017

@author: iheb
'''
from odoo import models, fields


class Invoice(models.Model):
    _inherit = 'account.invoice' 
     
    policy_id = fields.Many2one ('freight_sys.policy','Policy')

    
    
#     @api.multi
#     def action_invoice_open(self):
#         cons = self.env['medical_system.consultation'].search([('invoice_id','=',self.id)])
#         for line in cons:
#             line.state = 'a'
#         hos = self.env['medical_system.hospitalization'].search([('invoice_id','=',self.id)])
#         for line in hos:
#             line.state = 'a'
#         lab = self.env['medical_system.labtest'].search([('invoice_id','=',self.id)])
#         for line in lab:
#             line.state = 'a'
#         f = super(Invoice,self).action_invoice_open()
#         return f
    

    

    
    
    