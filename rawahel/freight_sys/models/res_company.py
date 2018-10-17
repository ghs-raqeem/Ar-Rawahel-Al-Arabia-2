# -*- coding: utf-8 -*-
from odoo import fields, models

class Company (models.Model):
    _inherit = "res.company"
    
    riadh_tel = fields.Char('Al Riyadh')
    jeddah_tel = fields.Char('Jeddah')
    dammam_tel = fields.Char("Al Damam")
    hfr_baten_tel = fields.Char('Hafer Al Batel')
    aniza_tel = fields.Char("Ounaiza")
    brida_tel = fields.Char("Brida")
    hail_tel = fields.Char("Hail")
    Medina_tel = fields.Char("Al medina")
    
    