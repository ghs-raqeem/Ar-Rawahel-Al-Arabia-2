# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ValidatePolicy(models.TransientModel):
    _name = 'freight_sys.validate_policy_wizard'
    
    policy_id = fields.Many2one('freight_sys.policy', 
                                default=lambda self: self.env['freight_sys.policy'].search([('id', '=', self._context.get('active_id'))]))
    place_from = fields.Char('From', related='policy_id.place_from.name')
    place_dest = fields.Char('To', related='policy_id.place_dest.name')
    
    # Sender informations
    sender_id = fields.Char(related='policy_id.sender_id.name')    
    sender_street = fields.Char('Address', related='policy_id.sender_id.street')
    sender_street2 = fields.Char(related='policy_id.sender_id.street2')
    sender_zip = fields.Char(related='policy_id.sender_id.zip')
    sender_city = fields.Char(related='policy_id.sender_id.zip')
    sender_state_id = fields.Char(string='State',related='policy_id.sender_id.state_id.name')
    sender_country_id = fields.Char(string='Country', related='policy_id.sender_id.country_id.name')
    sender_email = fields.Char(related='policy_id.sender_id.email')
    sender_phone = fields.Char(related='policy_id.sender_id.phone', string="Phone")
    sender_mobile = fields.Char(related='policy_id.sender_id.mobile')
    sender_identif = fields.Char(related='policy_id.sender_id.identification_nbr')
    #recipient informations
    recipient_id = fields.Char(string='recipient', related='policy_id.recipient_id.name')
    recipient_street = fields.Char('Address', related='policy_id.recipient_id.street')
    recipient_street2 = fields.Char(related='policy_id.recipient_id.street2')
    recipient_zip = fields.Char(change_default=True, related='policy_id.recipient_id.zip')
    recipient_city = fields.Char(related='policy_id.recipient_id.city')
    recipient_state_id = fields.Char(string='State', related='policy_id.recipient_id.state_id.name')
    recipient_country_id = fields.Char(string='Country', related='policy_id.recipient_id.country_id.name')
    recipient_email = fields.Char(related='policy_id.recipient_id.email')
    recipient_phone = fields.Char(related='policy_id.recipient_id.phone')
    recipient_mobile = fields.Char(related='policy_id.recipient_id.mobile')
    recipient_identif = fields.Char(related='policy_id.recipient_id.identification_nbr')

    
    #freights


    freight_count = fields.Integer("Freight Nbr", related='policy_id.freight_count', readonly=True)
    goods_value = fields.Float('Goods Value', related='policy_id.goods_value', readonly=True)
    content_ids = fields.Many2many(relation='freight_sys.policy.content', related='policy_id.content_ids', string='Contents', readonly=True)
    charge_line_ids = fields.Many2many(relation='freight_sys.policy.charges.line', related='policy_id.charge_line_ids', string='Charges')
    sender_signature = fields.Binary('Signature', related='policy_id.sender_signature', required=True)


    

    def accept_policy(self):
        if not self.sender_signature:
            raise UserError ('You need to sign first Plz')
        picking = self.policy_id._create_picking() 
        for line in picking.move_line_ids:
            line.qty_done = 1.0
        picking.button_validate()
        self.policy_id.create_invoices()   
        self.policy_id.state = 'source'            
                    
                
                
        
        
        
        