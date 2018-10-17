# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, Warning

'''
Created on Mar 5, 2018

@author: iheb
'''

# class PolicyLine(models.Model):
#     _name = 'freight_sys.policy.line'
#      
#     policy_id = fields.Many2one('freight_sys.policy', string='Policy')
#     place_from = fields.Many2one('stock.warehouse', 'From', related='policy_id.place_from')
#     place_dest = fields.Many2one('stock.warehouse', 'To', related='policy_id.place_dest')
#     sender_id = fields.Many2one('res.partner', string='Sender', related='policy_id.sender_id')
#     recipient_id = fields.Many2one('res.partner', string='Recipient', related='policy_id.recipient_id')
#     path_id = fields.Many2one('freight_sys.trips.path')

class VehicleCode(models.Model):

    _name = "freight_sys.trips.path.code"
    _description = "content's policy"

    code_vehicle = fields.Char('Vehicle Code')
    path_id = fields.Many2one('freight_sys.trips.path')


class Path(models.Model):
    _name = 'freight_sys.trips.path'
     
#     sequence = fields.Integer(string='Sequence')
    name = fields.Char('Name')
    route_id = fields.Many2one('stock.location.route', sring='Line')
    c_line_id = fields.Many2one('stock.location.route', string='Line')
    duration = fields.Char(related='route_id.duration')
    hours_program = fields.Integer(related='route_id.hours')
    minutes_program = fields.Integer(related='route_id.minutes')
    trip_id = fields.Many2one('freight_sys.trips')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    code_vehicle_ids = fields.One2many('freight_sys.trips.path.code', 'path_id', 'Vehicle_code')
    driver_id = fields.Many2one('hr.employee', sring="Driver")
#     policy_line_ids = fields.One2many('freight_sys.policy.line', 'Policies')
    policy_ids = fields.One2many('freight_sys.policy', 'path_id', string='Policies')
    

    @api.model
    def create(self, vals):
        line = super(Path, self).create(vals)
        print (line.trip_id)
        code = self.env['ir.sequence'].next_by_code('trips.path')
        line.name = 'TL-{}'.format(code )
        return line

class Trips(models.Model):
    _name = 'freight_sys.trips'
    _order = 'create_date desc'
    
    
    name = fields.Char(string='Trip', readonly=True)
    type = fields.Selection([('transfert', 'Transfert'),('delivery', 'Delivery')])
    code = fields.Char()
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    code_vehicle = fields.Char('Vehicle Code')
    route_id = fields.Many2one('stock.location.route', string='Current Line')
    driver_id = fields.Many2one('hr.employee', sring="Driver")
    place_from = fields.Many2one('stock.warehouse', "From", related="route_id.place_from", readonly=True)
    place_to = fields.Many2one('stock.warehouse', "To", related="route_id.place_dest", readonly=True)
    warehouse_load_ids = fields.Many2many('freight_sys.trips.warehouse_load', string="Destination place for policy must be:")
    warehouse_download_ids = fields.Many2many('freight_sys.trips.warehouse_download', string="Policies with these destinations places will be downoading in the next warehouse")
    with_distribution = fields.Boolean('With Distribution')
#     type = fields.Selection([('go', 'Going'),
#                            ('return', 'Return')], default='go', string="Type", required=True)
    leaving_time = fields.Datetime("Leaving Time")
    arrival_time = fields.Datetime("Arrival Time")
    state = fields.Selection([('draft', 'Draft'),
                               ('running', 'Running'), 
                               ('arrived', 'Arrived')], string='Status', required=True, readonly=True, default='draft')
    
    hours_program = fields.Integer(related='route_id.hours')
    minutes_program = fields.Integer(related='route_id.minutes')
    count_batchs_load = fields.Integer(compute='_compute_batchs_loading')
    count_batchs_download = fields.Integer(compute='_compute_batchs_downloading')
    batch_picking_ids = fields.One2many(
        'stock.picking.batch', 'trip_id', string='Batch Pickings',
        help='List of Batch picking associated to this trip')
#     route_id = fields.Many2one('stock.location.route', 'Program', required=True)
    policy_ids = fields.One2many('freight_sys.policy', 'trip_id', string='Policies')
    current_location = fields.Many2one('stock.location')
    path_ids = fields.One2many('freight_sys.trips.path', 'trip_id', string="Path")
    count_pick_load =  fields.Integer(compute='_get_pick_load_len' ,default=0, readonly=True)
    count_pick_download = fields.Integer(compute='_get_pick_download_len' ,default=0, readonly=True)
    path_count = fields.Integer(compute='compute_path_count')
#     route_ids = fields.One2many('stock.location.route', 'trip_id')
    _sql_constraints = [
        ('code_vehicle_uniq', 'unique (code_vehicle)', 'The Vehicle code must be unique')
    ]
#          
#     @api.onchange('route_id')
#     def onchange_program(self):
#         for trip in self:
#             if trip.route_id:
#                 for policy in trip.policy_ids:
#                     policy.route_id = trip.route_id

    
    def compute_path_count(self):
        for trip in self:
            paths = self.mapped('path_ids')
            trip.update({
                'path_count': len(paths)
    
                }) 
            
    def update_policies(self):
        warehouses1 = self.warehouse_load_ids.mapped('warehouse_id')
        paths = self.path_ids.ids
        policies = self.env['freight_sys.policy'].search([('trip_id','=',False),('place_dest','in',warehouses1.ids),('current_location','=',self.current_location.id),'|','|',('state','=','source'),('state','=','in_way'),('state','=','return')])
        for trip in self:
            for path in trip.path_ids:
                path.c_line_id = trip.route_id.id
            current_path = trip.path_ids.filtered(lambda p: p.route_id.id == trip.route_id.id)
            if current_path.vehicle_id and current_path.driver_id:
                trip.vehicle_id = current_path.vehicle_id.id
                trip.driver_id = current_path.driver_id.id
#                 trip.code_vehicle = current_path.code_vehicle
        if policies:
            warehouses2 = self.warehouse_download_ids.mapped('warehouse_id')
            for policy in policies.filtered(lambda x: x.place_dest.id in warehouses2.ids):
                policy.route_id = self.route_id.id
            for policy in policies.filtered(lambda x: x.place_dest.id not in warehouses2.ids):
                path = self.env['freight_sys.trips.path'].search([('trip_id','=',self.id),('route_id','=',self.route_id.id)],limit=1).ids
                i = paths.index(path[0])
                if i+1 < len(paths):
                    route_next = self.path_ids.browse(paths[i+1]).mapped('route_id')
                    if route_next:
                        route_policy = self.env['stock.location.route'].search([('place_from','=',self.route_id.place_from.id),('place_dest','=',route_next.place_dest.id)],limit=1)
                        if route_policy:
                            policy.route_id = route_policy.id
                        elif i+2 < len(paths):
                            route_next1 = self.path_ids.browse(paths[i+2]).mapped('route_id')
                            if route_next1:
                                route_policy1 = self.env['stock.location.route'].search([('place_from','=',self.route_id.place_from.id),('place_dest','=',route_next1.place_dest.id)],limit=1)
                                if route_policy1:
                                    policy.route_id = route_policy1.id
                                else:
                                    policy.route_id = False
                        else:
                            raise Warning(_('You should verify The path or downloading destination policies'))
                else:
                    raise Warning(_('Be carrefull ! This is the last route'))
                    
                    
                    
            self.policy_ids = [(4, x) for x in policies.ids]

    
    @api.onchange('route_id')
    def onchange_line(self):
        for trip in self:
            if trip.route_id.place_from:
                trip.current_location = trip.route_id.place_from.lot_stock_id.id
            if trip.route_id.place_dest:
                warehouse = self.env['freight_sys.trips.warehouse_download'].search([('warehouse_id','=',trip.route_id.place_dest.id)])
                trip.update({
                    'warehouse_download_ids': [(6, 0, [warehouse.id])],
                    'warehouse_load_ids': [(6, 0, [warehouse.id])]
                    })



                
    def terminate_trip(self):
        self.state = 'arrived'  
    
    def confirm_route(self):
        for trip in self:
            trip.state = 'running'
            types = self.env['stock.picking.type'].search([('code', '=', 'internal'), ('warehouse_id','=', trip.route_id.place_from.id)], limit=1)
            current_path = trip.path_ids.filtered(lambda p: p.route_id.id == trip.route_id.id)
#             for policy in trip.policy_ids:
            current_path.policy_ids = [(6,0,trip.policy_ids.ids)]
            for policy in trip.policy_ids.filtered(lambda p: p.is_routed == False):
                policy.is_routed = True
                for freight in policy.freight_ids:
                    freight.route_ids = [(6, 0, [policy.route_id.id])]
                policy.picking_type_id = types  
                policy._create_picking()
    
    def confirm_delivery_route(self):
        for trip in self:
            trip.state = 'running'
            types = self.env['stock.picking.type'].search([('code', '=', 'to_delivery'), ('warehouse_id','=', trip.route_id.place_from.id)], limit=1)
            for policy in trip.policy_ids.filtered(lambda p: p.is_routed == False):
                if types:
                    policy.picking_type_id = types.id
                else:
                    raise UserError('You need to configure picking type correctly')
                policy.is_routed = True
                for freight in policy.freight_ids:
                    freight.route_ids = [(6, 0, [trip.route_id.id])]

                policy._create_picking()
#                 policy.delivery = True
    
    @api.model
    def create(self, vals):
        line = super(Trips, self).create(vals)
#         if line.type == 'go':
        line.code = self.env['ir.sequence'].next_by_code('trips.name')
        line.name = 'TR-{}'.format(line.code)
        return line
    
    def action_view_twins_trip(self):
        action = self.env.ref('freight_sys.trips_action')
        result = action.read()[0]
        
        if self.type == 'go':
            trip = self.env['freight_sys.trips'].search([('code','=',self.code),('type','=','return')],limit=1)
            res = self.env.ref('freight_sys.trips_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = trip.id
        elif self.type == 'return':
            trip = self.env['freight_sys.trips'].search([('code','=',self.code),('type','=','go')])
            res = self.env.ref('freight_sys.trips_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = trip.id
        return result
            
            
        
        
        
    @api.onchange('leaving_time','route_id')
    def calc_arrival_time(self):
        for item in self:
            if item.leaving_time and item.route_id:
                leav_date = datetime.strptime(self.leaving_time,DEFAULT_SERVER_DATETIME_FORMAT)
                item.arrival_time = leav_date + timedelta(hours=item.hours_program, minutes=item.minutes_program)

                
                    
        
        
    def _compute_batchs_loading(self):
        for trip in self:
            batchs = self.batch_picking_ids.filtered(lambda batch: batch.type == 'loading')
            trip.update({
                'count_batchs_load': len(batchs)})
            
    def _compute_batchs_downloading(self):
        for trip in self:
            batchs = self.batch_picking_ids.filtered(lambda batch: batch.type == 'downloading')
            trip.update({
                'count_batchs_download': len(batchs)})

    @api.multi
    def action_view_batchs_loading(self):
        batchs = self.batch_picking_ids.filtered(lambda batch: batch.type == 'loading')
        action = self.env.ref('stock_picking_batch.stock_picking_batch_action')
        result = action.read()[0]
        result['domain'] = [('id','in', batchs.ids)]

        return result
    
    @api.multi
    def action_view_batchs_downloading(self):
        batchs = self.batch_picking_ids.filtered(lambda batch: batch.type == 'downloading')
        action = self.env.ref('stock_picking_batch.stock_picking_batch_action')
        result = action.read()[0]
        result['domain'] = [('id','in', batchs.ids)]

        return result
    @api.multi
    def _get_pick_load_len(self):
        for trip in self:
            policies = self.policy_ids.filtered(lambda p: p.batch_load == False) 
            pickings = self.env['stock.picking'].search([('policy_id','in', policies.ids),('state','=', 'assigned'),('location_id','=', trip.route_id.place_from.lot_stock_id.id)])

            trip.update({
                'count_pick_load': len(pickings)
                
                }) 
    def _prepare_batch_picking_load(self):
        policies = self.policy_ids.filtered(lambda p: p.batch_load == False)
#         pickings = self.env['stock.picking'].search([('policy_id','in', policies),('state','=', 'assigned'),('location_id','=', self.place_from.lot_stock_id.id),('location_dest_load','=', self.place_to.lot_stock_id.id)])
        if policies:
            pickings = self.env['stock.picking'].search([('policy_id','in', policies.ids),('state','=', 'assigned'),('location_id','=', self.route_id.place_from.lot_stock_id.id)])
            if pickings:
                for pick in pickings:
                    pick.trip_id = self.id
                    pick.vehicle_id = self.vehicle_id.id
                    pick.driver_id = self.driver_id.id
                    if pick.policy_id:
                        pick.policy_id.batch_load = True
                        pick.policy_id.batch_download = False
                    
                return {
                    'user_id': self.env.user.id,
                    'driver_id': self.driver_id.id or False,
                    'type': 'loading',
                    'trip_id': self.id,
                    'picking_ids': [(6, 0, [x.id for x in pickings])] or []
                    }
            else:
                raise UserError(_("You dont have any picking accessible to adding for loading. Maybe you have to confirm route first !"))
        else:
            raise UserError(_("There is no policy must be downloading in this batch related with this destination route"))

    @api.multi
    def _get_pick_download_len(self):
        for trip in self:
            policies = self.policy_ids.filtered(lambda p: p.batch_download == False and p.route_id.place_dest.lot_stock_id.id == trip.route_id.place_dest.lot_stock_id.id ) 
            if policies:
                pickings = self.env['stock.picking'].search([('policy_id','in', policies.ids),('state','=', 'assigned'),('location_dest_id','=', trip.route_id.place_dest.lot_stock_id.id)])
                trip.update({
                    'count_pick_download': len(pickings)
                    
                    })    
    def _prepare_batch_picking_download(self):
        policies = self.policy_ids.filtered(lambda p: p.batch_download == False and p.route_id.place_dest.lot_stock_id.id == self.route_id.place_dest.lot_stock_id.id ) 
#         policies = self.policy_ids.filtered(lambda p: p.batch_download == False)

        if policies:
            pickings = self.env['stock.picking'].search([('policy_id','in', policies.ids),('state','=', 'assigned'),('location_dest_id','=', self.route_id.place_dest.lot_stock_id.id)])
            if pickings:
                for pick in pickings:
                    pick.trip_id = self.id
                    pick.vehicle_id = self.vehicle_id.id
                    pick.driver_id = self.driver_id.id
                    if pick.policy_id:
                        pick.policy_id.batch_load = False
                        pick.policy_id.batch_download = True
#                         pick.policy_id.is_routed = False
                return {
                    'driver_id': self.driver_id.id or False,
                    'type': 'downloading',
                    'trip_id': self.id,
                    'picking_ids': [(6, 0, [x.id for x in pickings])] or []
                    }
            else:
                raise UserError(_("You dont have any picking accessible to adding for downloading. Maybe you have to confirm route first !"))
        else:
            raise UserError(_("There is no policy must be downloading in this batch related with this destination route"))

    @api.multi
    def create_batch_load(self):
        for trip in self:
            res = trip._prepare_batch_picking_load()
            trip.batch_picking_ids.create(res)


     
    @api.multi
    def create_batch_download(self):
        for trip in self:
            res1 = trip._prepare_batch_picking_download()
            trip.batch_picking_ids.create(res1)
            
    @api.multi
    def button_confirm(self): 
#         BatchPickings = self.env['stock.picking.batch'] 
        for trip in self:
            trip.state = 'validated'
            if trip.type == 'go':
                vals = {
                        'code':self.code,
                        'name':'RT-{}'.format(self.code),
                        'vehicle_id':self.vehicle_id.id,
                        'place_from':self.place_to.id,
                        'place_to':self.place_from.id,
                        'type':'return',
                    }
                self.create(vals)
            res = trip._prepare_batch_picking_load()
            res1 = trip._prepare_batch_picking_download()
            batch = trip.batch_picking_ids.create(res)
            trip.batch_picking_ids.create(res1)
            
            return batch
            

        