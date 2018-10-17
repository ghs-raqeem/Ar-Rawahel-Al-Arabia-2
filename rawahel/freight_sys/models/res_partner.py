# -*- coding: utf-8 -*-

from odoo import fields, models, api
'''
Created on Jan 30, 2018

@author: iheb
'''
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    identification_nbr = fields.Char('Identification N°')
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|','|','|',('phone', operator, name),('name', operator, name),('identification_nbr', operator, name),('mobile', operator, name)] + args, limit=limit)
        return recs.name_get()