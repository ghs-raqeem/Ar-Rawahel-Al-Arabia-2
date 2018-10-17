# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, Warning
from datetime import date
from odoo.addons import decimal_precision as dp
from odoo.tools.float_utils import float_is_zero, float_compare

from ..mobily.utilities import MobilyApiAuth
from ..mobily.sms import MobilySMS

import logging
_logger = logging.getLogger(__name__)
'''
Created on Jan 29, 2018

@author: iheb
'''

class Policy(models.Model):
    _name = 'freight_sys.policy'
    
    _order = 'create_date desc'
    
    
    @api.multi
    def default_charges(self):
        IrModelData = self.env['ir.model.data'] 
        if IrModelData.xmlid_to_res_id('product.product_delivery') and IrModelData.xmlid_to_res_id('product.product_ship'):

            return [
                    (0,0, {
                            'charge_id':IrModelData.xmlid_to_res_id('product.product_ship'),
                            'payee': 'sender',
                            'company_id': self.env.user.company_id.id,
                            'company_currency': self.env.user.company_id.currency_id.id
                    }),
                    (0,0, {
                            'charge_id':IrModelData.xmlid_to_res_id('product.product_delivery'),
                            'payee': 'recipient',
                            'company_id': self.env.user.company_id.id,
                            'company_currency': self.env.user.company_id.currency_id.id
                    })


                    ]

    
    
    name = fields.Char(string='Bill No', readonly=True)
    code_track = fields.Char("Tracking Code")
    progress = fields.Float("Policy Progress", compute='_get_completion')
    is_returned = fields.Boolean('Is Returned')
    reason = fields.Text('Reason')
    date_order = fields.Datetime('Policy date', default=datetime.now())
    date_expected = fields.Date('Expected delivery date ', default=fields.Date.context_today)
    state = fields.Selection([('new', 'New'),
                               ('validated', 'Validated'), 
                               ('source', 'Source'), ('in_way', 'In way'), 
                               ('destination', 'Destination'), 
                               ('to_delivery', 'To delivery'),
                               ('received', 'Received'),
                               ('return', 'Return'),
                               ('canceled', 'Canceled')], string='Status', required=True, default='new')
    place_from = fields.Many2one('stock.warehouse', 'From', required=True)
    place_dest = fields.Many2one('stock.warehouse', 'To', required=True)
    freight_ids = fields.One2many('product.template', 'policy_id', ondelete='cascade')
    nbr_freights = fields.Integer("Freights Nbr")
    freights_affect = fields.Boolean(default=False)
    note = fields.Text("Notes")
    freight_count = fields.Integer("Freights", compute='compute_lettre_count', help="Number of freights for this policy.")
    invoice_ids = fields.One2many('account.invoice', 'policy_id', string='Invoices')
    count_invoices = fields.Integer(compute='_compute_invoices')
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable", oldname="property_account_receivable",
        help="This account will be used instead of the default one as the receivable account for the current partner",
        required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', oldname='analytic_account')
    picking_ids = fields.One2many('stock.picking', 'policy_id', string='Receptions')
    group_id = fields.Many2one('procurement.group', string="Procurement group", copy=False)
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')
    current_location = fields.Many2one('stock.location', 'Current Location')
    picking_reception_count = fields.Integer(compute='_compute_reception_picking')
    picking_track_count = fields.Integer(compute='_compute_track_picking')
    picking_return_count = fields.Integer(compute='_compute_return_picking')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    trip_id = fields.Many2one('freight_sys.trips')
    path_id = fields.Many2one('freight_sys.trips.path')
    is_routed = fields.Boolean('Is Routed', default=False)
    route_id = fields.Many2one('stock.location.route', 'Route')
    batch_load = fields.Boolean('Batch Load', default=False)
    batch_download = fields.Boolean('Batch Download', default=False)
    order_line = fields.One2many('freight_sys.policy.line', 'policy_id', string='Policy Order Lines', readonly=True, ondelete='restrict')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position')
    delivery = fields.Boolean('With Delivery', default=False)
    # Sender informations
    sender_id = fields.Many2one('res.partner', string='Sender', required=True, store=True)
    sender_street = fields.Char('Address', related='sender_id.street', store=True)
    sender_street2 = fields.Char(related='sender_id.street2', store=True)
    sender_zip = fields.Char(change_default=True, related='sender_id.zip',store=True)
    sender_city = fields.Char(related='sender_id.city', store=True)
    sender_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related='sender_id.state_id', store=True)
    sender_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='sender_id.country_id', store=True)
    sender_email = fields.Char(related='sender_id.email', store=True)
    sender_phone = fields.Char(related='sender_id.phone', string="Phone", store=True)
    sender_mobile = fields.Char(related='sender_id.mobile', store=True)
    sender_identif = fields.Char(related='sender_id.identification_nbr', store=True)
    partner_id = fields.Many2one(related='sender_id')

    #recipient informations
    recipient_id = fields.Many2one('res.partner', string='Recipient', required=True, store=True)
    recipient_street = fields.Char('Address', related='recipient_id.street', store=True)
    recipient_street2 = fields.Char(related='recipient_id.street2', store=True)
    recipient_zip = fields.Char(change_default=True, related='recipient_id.zip', store=True)
    recipient_city = fields.Char(related="recipient_id.city", store=True)
    recipient_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related='recipient_id.state_id', store=True)
    recipient_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='recipient_id.country_id', store=True)
    recipient_email = fields.Char(related='recipient_id.email', store=True)
    recipient_phone = fields.Char(related='recipient_id.phone', store=True)
    recipient_mobile = fields.Char(related='recipient_id.mobile', store=True)
    recipient_identif = fields.Char(related='recipient_id.identification_nbr', store=True)

    #general info

#     goods_value = fields.Float('Goods Value', compute='_compute_freights_value')
    goods_value = fields.Float('Goods Value')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    charge_line_ids = fields.Many2many('freight_sys.policy.charges.line', 'policy_id', default=default_charges, string='Charges')
    content_ids = fields.Many2many('freight_sys.policy.content', string='Contents')
#     content_ids = fields.Many2many('freight_sys.policy.content', compute='_compute_contents',string='Contents')
    payment_type = fields.Selection([('by_sender', 'By sender (Cash)'),
                               ('by_recipient', 'By recipient (COD)'), 
                               ('both', 'Both')], string='Payment Type', required=True)
    by_sender = fields.Boolean('By sender (Cash)')
    by_recipient = fields.Boolean('By recipient (COD)')
    #Confirmation
    sender_signature = fields.Binary('Signature')
    recipient_signature = fields.Binary('Signature')
    
    def delete_policy_from_trip(self): 
        for policy in self:
            policy.trip_id.write({
            'policy_ids': [(3, policy.id, False)]
            })
    
    
    @api.onchange('payment_type')
    def onchange_payment_type(self):
        if self.payment_type == 'by_sender':
            for charge in self.charge_line_ids:
                charge.payee = 'sender'
            self.by_recipient = False
            self.by_sender = True
        if self.payment_type == 'by_recipient':
            for charge in self.charge_line_ids:
                charge.payee = 'recipient'
            self.by_recipient = True
            self.by_sender = False
        if self.payment_type == 'both':
            self.by_recipient = True
            self.by_sender = True
            
            
        
    
    

    
    @api.model
    def create(self, vals):
        line = super(Policy, self).create(vals)
        line.name = self.env['ir.sequence'].next_by_code('policy.nbr')
        return line
        
    def _get_completion(self):
        """Return the percentage of completeness of the goal, between 0 and 100"""
        for goal in self:
            if goal.state == 'source':
                goal.progress = 25.0
            elif goal.state == 'in_way':
                goal.progress = 50.0
            elif goal.state == 'destination':
                goal.progress = 75.0   
            elif goal.state == 'received':
                goal.progress = 100.0
            else:
                goal.progress = 0.0
                
#     @api.depends('picking_ids.state')
#     def get_state_souce(self):
#         for policy in self:
#             picks = policy.mapped('picking_ids')
#             print ('55555555')
#             if picks[0].state == 'done':
#                 policy.state = 'source'
    
    def return_policy(self):
        action = self.env.ref('freight_sys.action_confirm_return_wizard').read()[0]
        return action
        
    def cancel_return(self):
        for line in self:
            line.is_returned = False
            line.state = 'destination'
            
    def return_reception(self):
        for policy in self:
            pick_type = self.env['stock.picking.type'].search([('code', '=', 'outgoing'), ('warehouse_id','=', policy.place_from.id)], limit=1)
            
            if pick_type:
                policy.picking_type_id = pick_type.id
            else:
                raise UserError('You need to configure pick type correctly')
            route = self.env['stock.location.route'].search([('reception_type', '=', 'direct'), ('place_from','=', policy.place_from.id)], limit=1)
            if route:
                for freight in policy.freight_ids:
                    freight.route_ids = [(6, 0, [route.id])]
            else:
                raise UserError('You need to configure your route correctly')
        self._create_picking()
            
            
            
#     def reserve_return(self):
#         pick_type = self.env['stock.picking.type'].search([('warehouse_id','=',self.place_dest.id),('name','ilike','return')],limit=1)
#         print (pick_type)
#         if pick_type:
#             for policy in self:
#                 policy.state = 'to_return'
#                 policy.picking_type_id = pick_type
#                 picking = self._create_picking()
#                 picking.is__return = True
            
    
#     def confirm_return(self):
#         
#         for policy in self:
#             route = self.env['stock.location.route'].search([('place_from','=',policy.place_dest.id),('place_dest','=',policy.place_from.id)], limit=1)
#             for product in policy.freight_ids:
#                 if route:
#                     product.route_ids = [(6, 0, [route.id])]
#             pick_type = self.env['stock.picking.type'].search([('warehouse_id','=',policy.place_dest.id),('code','=','internal'),('name','ilike','Internal Transfers')],limit=1)
#             print (pick_type)
#             if pick_type:
#                 policy.picking_type_id = pick_type
#                 picking = policy._create_picking() 
#                 picking.is__return = True

    @api.multi
    def _get_destination_location(self):
        self.ensure_one()
        return self.picking_type_id.default_location_dest_id.id
    
    @api.multi
    def _get_location(self):
        self.ensure_one()
        if (self.picking_type_id.code == 'incoming'):
            return self.partner_id.property_stock_supplier.id
        else:
            return self.picking_type_id.default_location_src_id.id
    
    @api.multi
    def _compute_reception_picking(self):
        for policy in self:
            if policy.picking_ids:
                pick = policy.mapped('picking_ids').filtered(lambda x:x.picking_type_id.warehouse_id == self.place_from and x.picking_type_id.code == 'incoming' and x.is__return == False)
                policy.update({
                    'picking_reception_count': len(pick)})
                
    @api.multi
    def _compute_track_picking(self):
        for policy in self:
            if policy.picking_ids:
                pick = policy.mapped('picking_ids').filtered(lambda x:x.is__return == False)
                policy.update({
                    'picking_track_count': len(pick)})
        
    @api.multi
    def _compute_return_picking(self):
        for policy in self:
            if policy.picking_ids:
                pick = policy.mapped('picking_ids').filtered(lambda x:x.is__return == True)
                policy.update({
                    'picking_return_count': len(pick)})
                
    @api.onchange('place_from')
    def _default_picking_type(self):
        type_obj = self.env['stock.picking.type']
        types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id','=', self.place_from.id)])
        if not types:
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])
        self.picking_type_id = types

    
        
    def button_confirm(self): 
        
        msg1 = u" السلام عليكم يسعد إدارة معاهد إبلاغكم أنه تم بفضل اللًه قبولكم "
        msg2 = u" و ستدخل باذن اللًه مبدئيا في فترة تربص"
        msg3 = u"  الرجاء الإلتحاق بنا في أسرع وقت"
        msg = u" ".join((msg1,msg2,msg3)).encode("utf-8")
        auth = MobilyApiAuth(966599700009, "5b7c5c8da44c20af77a0609ebc9819c8")
        sms = MobilySMS(auth, [self.sender_mobile], "Rawahel", msg)
        _logger.debug('=====================================================')
        _logger.debug([self.sender_mobile])
        if MobilySMS.can_send():
            print ('Service is available!')
        else:
            print ('Service is not available!')
        try:    
            sms.send()
        except:
            True
        if self.freights_affect == False: 
            nbr = self.nbr_freights+1
            if self.nbr_freights > 0:
                for i in range(1,nbr):
                    vals = {
                        'policy_id': self.id,
                        'num_freight': i
                        }
                    self.env['product.template'].create(vals)
                self.freights_affect = True
            if self.freight_count == 0:
                raise UserError('You must affect some freights to this policy before validation')
        action = self.env.ref('freight_sys.action_validate_policy_wizard').read()[0]
#         action['view_id'] = [(self.env.ref('freight_sys.policy_validate_form').id, 'form')]
        return action
    
#     def button_reception(self):  
#         action = self.env.ref('freight_sys.action_receipt_policy_wizard').read()[0]
# #         action['view_id'] = [(self.env.ref('freight_sys.policy_validate_form').id, 'form')]
#         return action
    
    def final_reception(self):
#         action = self.env.ref('freight_sys.action_receipt_policy_wizard').read()[0]
# #         action['view_id'] = [(self.env.ref('freight_sys.policy_validate_form').id, 'form')]
#         return action
        for policy in self:
#             picking = policy.picking_ids.filtered(lambda x:x.picking_type_id.warehouse_id == policy.place_dest.id and x.picking_type_id.code == 'outgoing' and x.state == 'assigned')
#             for trip in policy.trip_id:
#                 res1 = {
#                     'driver_id': trip.driver_id.id or False,
#                     'type': 'downloading',
#                     'trip_id': trip.id,
#                     'picking_ids': [(6, 0, [x.id for x in picking])] or []
#                     }
#                 trip.batch_picking_ids.create(res1)
            
            policy.state = 'received'
            picking = self.env['stock.picking'].search([('policy_id','=', policy.id), ('state','=', 'assigned')], limit=1)

#             picking = policy.picking_ids.filtered(lambda x:x.picking_type_id.warehouse_id == policy.place_dest.id and x.picking_type_id.code == 'outgoing' and x.state == 'assigned')
            for line in picking.move_line_ids:
                line.qty_done = 1.0
            picking.button_validate()

       
    def button_delivery(self):
        pick_type = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id','=', self.place_dest.id)], limit=1)
        if pick_type:
            self.picking_type_id = pick_type.id
        else:
            raise UserError('You need to configure picking type correctly')
        route = self.env['stock.location.route'].search([('reception_type', '=', 'delivery'), ('place_from','=', self.place_dest.id)], limit=1)
        if route:
            for freight in self.freight_ids:
                freight.route_ids = [(6, 0, [route.id])]
        else:
            raise UserError('You need to configure your route correctly')
        self._create_picking()
        self.delivery = True
    
    @api.model
    def _prepare_picking(self):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.sender_id.id
            })
        if not self.sender_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.sender_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'policy_id' : self.id,
            'partner_id': self.sender_id.id,
            'date': self.date_expected,
            'owner_id': self.company_id.partner_id.id,
            'origin': self.name,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'company_id': self.company_id.id,
            'is__return' : self.is_returned or False,
        }

    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
#             if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
#                 pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
#                 if not pickings:
#                     res = order._prepare_picking()
#                     picking = StockPicking.create(res)
#                 else:
#                     picking = pickings[0]
                    
                pickings = StockPicking.browse(order.picking_ids.ids)
                res = order._prepare_picking()
                picking = StockPicking.create(res)
                
                moves = order.order_line._create_stock_moves(picking)
#                 moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                moves = moves.filtered(lambda x: x.state not in ('cancel'))._action_confirm()
                seq = 0
                for move in sorted(moves, key=lambda move: move.date_expected):
                    seq += 5
                    move.sequence = seq
                moves._action_assign()
#                 for move1 in moves:
#                     for dest in move1.move_dest_ids:
#                         picking.location_dest_new = dest.location_dest_id
#                 
#                     print ('dest***** {}'.format(picking.location_dest_new))
        return picking


    @api.multi
    def action_view_return_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids').filtered(lambda x:x.is__return == True)
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result

                
    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids').filtered(lambda x:x.picking_type_id.warehouse_id == self.place_from and x.picking_type_id.code == 'incoming' and x.is__return == False)
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result
    
    @api.multi
    def action_view_track_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]

        #override the context to get rid of the default filtering on operation type
        result['context'] = {}
        pick_ids = self.mapped('picking_ids').filtered(lambda x: x.is__return == False)
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids.id
        return result
    
    def _compute_freights_value(self):
        if self.freight_ids:
            s = 0
            for freight in self.freight_ids:
                s += freight.list_price
            self.goods_value = s
        
    def _compute_contents(self):
        if self.freight_ids:            
            for freight in self.freight_ids:
                for content in freight.content_ids:
                    if content not in self.content_ids:
                        self.content_ids += content
                   
    
    def compute_lettre_count(self):
        for policy in self:
            freights = self.mapped('freight_ids')
            policy.update({
                'freight_count': len(freights)
    
                }) 
    
    
    def _compute_invoices(self):
        for policy in self:
            invoices = policy.mapped('invoice_ids')
            policy.update({
                'count_invoices': len(invoices)})

    @api.multi
    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        result['domain'] = [('id','in', invoices.ids)]
        count_invoices = len(invoices)
        #override the context to get rid of the default filtering
        return result
    
    def _prepare_analytic_account(self, line):
        '''This method is designed to be inherited in a custom module'''
        return False

     
    @api.multi
    def create_invoices(self):
        if self.by_sender==True:
            self.create_invoice_sender()

        if self.by_recipient==True:
            self.create_invoice_recipient()
        
     
    # invoice_sender       
        
    def _prepare_invoice_sender(self):
        """
        Prepare the dict of values to create the new invoice for policy.
        """

        return {
            'name': 'INV[{}]'.format(self.name),
            'policy_id': self.id,
            'account_id': self.sender_id.property_account_receivable_id.id,
            'type': 'out_invoice',
#             'reference': "self.name",
            'partner_id': self.sender_id.id,
            'currency_id': self.company_id.currency_id.id,
            'user_id': self.env.uid,
            'date_invoice': date.today(),
        }
         
     
        
    def action_create_charge_line_sender(self, line=False, invoice_id=False, price_t=False):
        InvoiceLine = self.env['account.invoice.line']
        price_unit = line.charge_price/1.05
#         default_analytic_account = self.env['account.analytic.default'].account_get(self.product_id.id, self.order_id.partner_id.id, self.order_id.user_id.id, fields.Date.today())
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.charge_id.id,
            'quantity': 1,
            'price_unit': price_unit,
            'account_analytic_id':  self._prepare_analytic_account(line),
        }
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=price_unit)
    #         inv_line.update(name= 'REF : '+line.ref)
        return InvoiceLine.sudo().create(inv_line)   
   
    @api.multi
    def create_invoice_sender(self):
        Invoice = self.env['account.invoice'] 
        for order in self:
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
             
   
            if not order:
                raise UserError(_('Please provide a partner for the sale.'))
   
            invoice = Invoice.new(order._prepare_invoice_sender())
            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.create(inv)
            message = (
                "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                          order.id, order)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id})
            Invoice += new_invoice
             
            for line in order.charge_line_ids.filtered(lambda line:line.payee == 'sender'):
                self.action_create_charge_line_sender(line, new_invoice.id)
                line.invoice_id = new_invoice.id
            amount_tax = new_invoice.amount_tax
            new_invoice._onchange_invoice_line_ids()
            new_invoice.action_invoice_open()
                         
            
   
        if not Invoice:
            return {}
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': self.env.ref('account.invoice_form').id,
            'target': 'current',
            'context': "{'type':'out_invoice'}",
            'nodestroy': True,
            'res_id': Invoice and Invoice.ids[0] or False,
            }
   
        
    # invoice_recipient      
        
    def _prepare_invoice_recipient(self):
        """
        Prepare the dict of values to create the new invoice for policy.
        """

        return {
            'name': 'INV[{}]'.format(self.name),
            'policy_id': self.id,
            'account_id': self.recipient_id.property_account_receivable_id.id,
            'type': 'out_invoice',
#             'reference': "self.name",
            'partner_id': self.recipient_id.id,
            'currency_id': self.company_id.currency_id.id,
            'user_id': self.env.uid,
            'date_invoice': date.today(),
        }
         
     
        
    def action_create_charge_line_recipient(self, line=False, invoice_id=False, price_t=False):
        InvoiceLine = self.env['account.invoice.line']
#         default_analytic_account = self.env['account.analytic.default'].account_get(self.product_id.id, self.order_id.partner_id.id, self.order_id.user_id.id, fields.Date.today())
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.charge_id.id,
            'quantity': 1,
            'price_unit': line.charge_price,
            'account_analytic_id':  self._prepare_analytic_account(line),
        }
        # Oldlin trick
         
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=line.charge_price)
    #         inv_line.update(name= 'REF : '+line.ref)
        return InvoiceLine.sudo().create(inv_line)   
   
    @api.multi
    def create_invoice_recipient(self):
        Invoice = self.env['account.invoice'] 
        for order in self:
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
             
   
            if not order:
                raise UserError(_('Please provide a partner for the sale.'))
   
            invoice = Invoice.new(order._prepare_invoice_recipient())
            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.create(inv)
            message = (
                "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                          order.id, order)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id})
            Invoice += new_invoice
             
            for line in order.charge_line_ids.filtered(lambda line:line.payee == 'recipient'):
                self.action_create_charge_line_recipient(line, new_invoice.id)
                line.invoice_id = new_invoice.id
                         
            new_invoice.action_invoice_open()
                         
            
   
        if not Invoice:
            return {}
        return {
            'name': 'Customer Invoice',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'view_id': self.env.ref('account.invoice_form').id,
            'target': 'current',
            'context': "{'type':'out_invoice'}",
            'nodestroy': True,
            'res_id': Invoice and Invoice.ids[0] or False,
            }



class Content(models.Model):

    _name = "freight_sys.policy.content"
    _description = "content's policy"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color Index', default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    

        
class ChargesLine(models.Model):
    _name="freight_sys.policy.charges.line"
    
    charge_id = fields.Many2one('product.template', domain=[('type','=','service')], 
                                context={'default_type': 'service'})
    payee = fields.Selection([('sender','Sender'),('recipient','Recipient')],string='Payee', default='sender')
    policy_id = fields.Many2one('freight_sys.policy')
    description = fields.Char('Description')
    sequence = fields.Integer(index=True, default=1)
    company_currency = fields.Many2one(string='Currency', related='company_id.currency_id', readonly=True, relation="res.currency")
    charge_price = fields.Float('Price')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.user.company_id.id)
    invoice_id = fields.Many2one('account.invoice')
    state = fields.Selection([
            ('draft','Draft'),
            ('open', 'Open'),
            ('paid', 'Paid'),
            ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, default='draft', copy=True, related='invoice_id.state')
    
    @api.onchange('charge_id')
    def set_payee(self):
        IrModelData = self.env['ir.model.data'] 
        for line in self:
            if line.charge_id.id == IrModelData.xmlid_to_res_id('product.product_delivery'):
                line.payee = 'recipient'
    
class PolicyOrderLine(models.Model):
    _name = 'freight_sys.policy.line'
    _description = 'Policy Order Line'
    _order = 'policy_id, sequence, id'





    @api.depends('policy_id.state', 'move_ids.state', 'move_ids.product_uom_qty')
    def _compute_qty_received(self):
        for line in self:
            if line.policy_id.state in ['new']:
                line.qty_received = 0.0
                continue
            if line.product_id.type not in ['consu', 'product']:
                line.qty_received = line.product_qty
                continue
            total = 0.0
            for move in line.move_ids:
                if move.state == 'done':
                    if move.location_dest_id.usage == "supplier":
                        if move.to_refund:
                            total -= move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
                    else:
                        total += move.product_uom._compute_quantity(move.product_uom_qty, line.product_uom)
            line.qty_received = total





    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    date_planned = fields.Date(string='Scheduled Date', required=True, index=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True, ondelete='cascade')
    move_ids = fields.One2many('stock.move', 'policy_line_id', string='Reservation', readonly=True, ondelete='set null', copy=False)
    price_unit = fields.Float(string='Unit Price', required=True, digits=dp.get_precision('Product Price'))

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    policy_id = fields.Many2one('freight_sys.policy', string='policy Reference', index=True, ondelete='cascade')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    company_id = fields.Many2one('res.company', related='policy_id.company_id', string='Company', store=True, readonly=True)
    state = fields.Selection(related='policy_id.state', store=True)

    invoice_lines = fields.One2many('account.invoice.line', 'policy_line_id', string="Bill Lines", readonly=True, copy=False)

    # Replace by invoiced Qty
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)
    qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty", digits=dp.get_precision('Product Unit of Measure'), store=True)

    partner_id = fields.Many2one('res.partner', related='policy_id.sender_id', string='Partner', readonly=True, store=True)
    currency_id = fields.Many2one(related='policy_id.currency_id', store=True, string='Currency', readonly=True)
    date_order = fields.Datetime(related='policy_id.date_order', string='Order Date', readonly=True)

    orderpoint_id = fields.Many2one('stock.warehouse.orderpoint', 'Orderpoint')
    move_dest_ids = fields.One2many('stock.move', 'created_policy_line_id', 'Downstream Moves')

  


    @api.multi
    def _prepare_stock_moves(self, picking):
        """ Prepare the stock moves data for one order line. This function returns a list of
        dictionary ready to be used in stock.move's create()
        """
        self.ensure_one()
        res = []
        if self.product_id.type not in ['product', 'consu']:
            return res
        qty = 0.0
        price_unit = 0.0
        for move in self.move_ids.filtered(lambda x: x.state != 'cancel' and not x.location_dest_id.usage == "supplier"):
            qty += move.product_qty
        template = {
            'name': self.name or '',
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': 1.0,
            'date': self.policy_id.date_order,
            'date_expected': self.date_planned,
            'location_id': self.policy_id._get_location(),
            'location_dest_id': self.policy_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.policy_id.sender_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'policy_line_id': self.id,
            'company_id': self.policy_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.policy_id.picking_type_id.id,
            'group_id': self.policy_id.group_id.id,
            'origin': self.policy_id.name,
            'route_ids': self.policy_id.picking_type_id.warehouse_id and [(6, 0, [x.id for x in self.policy_id.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id': self.policy_id.picking_type_id.warehouse_id.id,
        }
        
#         diff_quantity = self.product_qty - qty
#         if float_compare(diff_quantity, 0.0,  precision_rounding=self.product_uom.rounding) > 0:
#             template['product_uom_qty'] = diff_quantity
        res.append(template)
        return res

    @api.multi
    def _create_stock_moves(self, picking):
        moves = self.env['stock.move']
        done = self.env['stock.move'].browse()
        for line in self:
            for val in line._prepare_stock_moves(picking):
                done += moves.create(val)
        return done

    @api.multi
    def unlink(self):
        for line in self:
            if line.policy_id.state in ['validate']:
                raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') %(line.state,))
        return super(PolicyOrderLine, self).unlink()

    @api.model
    def _get_date_planned(self, seller, po=False):
        """Return the datetime value to use as Schedule Date (``date_planned``) for
           PO Lines that correspond to the given product.seller_ids,
           when ordered at `date_order_str`.

           :param Model seller: used to fetch the delivery delay (if no seller
                                is provided, the delay is 0)
           :param Model po: purchase.order, necessary only if the PO line is 
                            not yet attached to a PO.
           :rtype: datetime
           :return: desired Schedule Date for the PO line
        """
        date_order = po.date_order if po else self.policy_id.date_order
        if date_order:
            return datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(days=seller.delay if seller else 0)
        else:
            return datetime.today() + relativedelta(days=seller.delay if seller else 0)

    def _merge_in_existing_line(self, product_id, product_qty, product_uom, location_id, name, origin, values):
        """ This function purpose is to be override with the purpose to forbide _run_buy  method
        to merge a new po line in an existing one.
        """
        return True

    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.policy_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id.id == company_id))
        else:
            self.taxes_id = fpos.map_tax(self.product_id.supplier_taxes_id)

        self._suggest_quantity()
        self._onchange_quantity()

        return result

    @api.onchange('product_id')
    def onchange_product_id_warning(self):
        if not self.product_id:
            return
        warning = {}
        title = False
        message = False

        product_info = self.product_id

        if product_info.purchase_line_warn != 'no-message':
            title = _("Warning for %s") % product_info.name
            message = product_info.purchase_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product_info.purchase_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        return {}

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.policy_id.date_order and self.policy_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return

        price_unit = self.env['account.tax']._fix_tax_included_price_company(seller.price, self.product_id.supplier_taxes_id, self.taxes_id, self.company_id) if seller else 0.0
        if price_unit and seller and self.policy_id.currency_id and seller.currency_id != self.policy_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.policy_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = seller.product_uom._compute_price(price_unit, self.product_uom)

        self.price_unit = price_unit

    def _suggest_quantity(self):
        '''
        Suggest a minimal quantity based on the seller
        '''
        if not self.product_id:
            return

        seller_min_qty = self.product_id.seller_ids\
            .filtered(lambda r: r.name == self.policy_id.partner_id)\
            .sorted(key=lambda r: r.min_qty)
        if seller_min_qty:
            self.product_qty = seller_min_qty[0].min_qty or 1.0
            self.product_uom = seller_min_qty[0].product_uom
        else:
            self.product_qty = 1.0
    