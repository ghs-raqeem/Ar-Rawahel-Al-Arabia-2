# -*- coding: utf-8 -*-

from odoo import fields, models

'''
Created on Mar 6, 2018

@author: iheb 
'''

class ResUser(models.Model):
    _inherit = 'res.users'
    
    warehouse_id = fields.Many2one('stock.warehouse', string="Work place")
    
    
    
