# -*- coding: utf-8 -*-

from odoo import fields, models, api
import random
'''
Created on Jan 31, 2018

@author: iheb
'''

class Product(models.Model):
    _inherit = 'product.template'

    def _generate_auto_barcode(self):
    
        s = "0123456789"
        p = "".join(random.SystemRandom().choice(s) for _ in range(13))
        product = self.env['product.template'].search([])
        bcd = []
        for prd in product:
            bcd.append(prd.barcode) 
        while p in bcd:
            p = "".join(random.SystemRandom().choice(s) for _ in range(13))

        return p

       

    policy_id = fields.Many2one('freight_sys.policy')
    payee = fields.Selection([
        ('sender', "Sender"),
        ('recipient', "Recipient")],default='sender', string="Payee")
    list_price = fields.Float(default=0.0)
    name = fields.Char(required=False, readonly=True)
    content_ids = fields.Many2many('freight_sys.policy.content',string='Contents')
    barcode = fields.Char(default=_generate_auto_barcode)
    num_freight = fields.Integer('Num', default=1)

  
       
    @api.onchange('policy_id')
    def get_context_1(self):
        policy = self.env['freight_sys.policy'].search([('id','=',self._context.get('active_id'))])
        self.num_freight = policy.freight_count

    
#     @api.multi
#     def write(self, vals):
#         for freight in self:
#             if vals.get('list_price'):
#                 freight.policy_id.goods_value += vals.get('list_price')
#         res = super(Product, self).write(vals)
# 
#         return res
    
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('freight.name')
        vals['barcode'] = self._generate_auto_barcode()
        line = super(Product, self).create(vals)
#         route = self.env['stock.location.route'].search([('place_from','=',line.policy_id.place_from.id),('place_dest','=',line.policy_id.place_dest.id)], limit=1)
#         if route:
#             line.route_ids = [(6, 0, [route.id])]
# #             line.route_ids = [(4,route.id,None)]
        if line.policy_id:
            line.policy_id.order_line.create({
                'name': line.name,
                'product_id': line.id,
                'product_qty': 1.0,
                'date_planned': line.policy_id.date_expected,
                'product_uom': line.uom_id.id,
                'price_unit' : 0.0,
                'policy_id': line.policy_id.id,
                'date_order': line.policy_id.date_order,
                'partner_id': line.policy_id.sender_id.id,
                'qty_received': 0.0,
                'qty_invoiced': 0.0
                })
            
        return line
    
    