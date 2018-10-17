# -*- coding: utf-8 -*-

from odoo import fields, models, api

'''
Created on Mar 7, 2018

@author: iheb
'''
class Warehouse_load(models.Model):
    _name = 'freight_sys.trips.warehouse_load'
    _rec_name = 'warehouse_id'

    warehouse_id = fields.Many2one('stock.warehouse', sring='Warehouse load')
    
class Warehouse_download(models.Model):
    _name = 'freight_sys.trips.warehouse_download'
    _rec_name = 'warehouse_id'

    warehouse_id = fields.Many2one('stock.warehouse', sring='Warehouse download')
    