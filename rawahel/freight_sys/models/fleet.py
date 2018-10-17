# -*- coding: utf-8 -*-

from odoo import fields, models
import random

'''
Created on Mar 5, 2018

@author: iheb
'''

class Fleet(models.Model):
    _inherit = 'fleet.vehicle'
    
    def _generate_auto_code(self):
    
        s = "0123456789"
        p = "".join(random.SystemRandom().choice(s) for _ in range(5))
        vehicule = self.env['fleet.vehicle'].search([])
        bcd = []
        for vhd in vehicule:
            bcd.append(vhd.code) 
        print (bcd)
        while p in bcd:
            p = "".join(random.SystemRandom().choice(s) for _ in range(5))
        print (p)
        return p
    
    def _generate_auto_barcode(self):
    
        s = "0123456789"
        p = "".join(random.SystemRandom().choice(s) for _ in range(13))
        vehicule = self.env['fleet.vehicle'].search([])
        bcd = []
        for vhd in vehicule:
            bcd.append(vhd.barcode) 
        print (bcd)
        while p in bcd:
            p = "".join(random.SystemRandom().choice(s) for _ in range(13))

        print (p)
        return p

                    

    code = fields.Char('Code', default=_generate_auto_code)
    barcode = fields.Char(default=_generate_auto_barcode)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")
    
    
    
    