# -*- coding: utf-8 -*-
'''
Created on May 15, 2018

@author: iheb
'''
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ReceiptPolicy(models.TransientModel):
    _name = 'freight_sys.receipt_policy_wizard'
    
    policy_id = fields.Many2one('freight_sys.policy', 
                                default=lambda self: self.env['freight_sys.policy'].search([('id', '=', self._context.get('active_id'))]))
    place_from = fields.Char('From', related='policy_id.place_from.name')
    place_dest = fields.Char('To', related='policy_id.place_dest.name')
    delivery = fields.Boolean('Delivery', readonly=True, related='policy_id.delivery')

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
    

    
    #freights


    freight_count = fields.Integer("Freight Nbr", related='policy_id.freight_count', readonly=True)
    goods_value = fields.Float('Goods Value', related='policy_id.goods_value')
    content_ids = fields.Many2many(relation='freight_sys.policy.content', related='policy_id.content_ids', string='Contents', readonly=True)
    charge_line_ids = fields.Many2many(relation='freight_sys.policy.charges.line', related='policy_id.charge_line_ids', string='Charges')
    recipient_signature = fields.Binary('Recipient Signature', related='policy_id.recipient_signature', required=True)


    def confirm_reception(self): 
        pick_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id','=', self.policy_id.place_dest.id)], limit=1)
        print (pick_type)
        if pick_type:
            self.policy_id.picking_type_id = pick_type.id
            print (self.policy_id.picking_type_id)
        else:
            raise UserError('You need to configure pick type correctly')
        route = self.env['stock.location.route'].search([('reception_type', '=', 'direct'), ('place_from','=', self.policy_id.place_dest.id)], limit=1)
        print (route)
        if route:
            for freight in self.policy_id.freight_ids:
                freight.route_ids = [(6, 0, [route.id])]
        else:
            raise UserError('You need to configure your route correctly')
        self.policy_id._create_picking()
        self.policy_id.state = 'received'  
    
    def confirm_delivery_reception(self): 
        if not self.recipient_signature:
            raise UserError ('You need to sign first Plz')
        for policy in self.policy_id:
            picking = policy.picking_ids.filtered(lambda x:x.picking_type_id.warehouse_id == policy.place_dest.id and x.picking_type_id.code == 'outgoing' and x.state == 'assigned')
            for trip in policy.trip_id:
                res1 = {
                    'driver_id': trip.driver_id.id or False,
                    'type': 'downloading',
                    'trip_id': trip.id,
                    'picking_ids': [(6, 0, [x.id for x in picking])] or []
                    }
                trip.batch_picking_ids.create(res1)
            
        self.policy_id.state = 'received'  

        
        
        
        