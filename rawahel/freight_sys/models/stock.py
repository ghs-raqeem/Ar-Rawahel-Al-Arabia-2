# -*- coding: utf-8 -*-
from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
from datetime import datetime


'''
Created on Mar 6, 2018

@author: iheb 
'''

class PickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    code = fields.Selection([('incoming', 'Vendors'), ('to_delivery', 'To delivery'), ('outgoing', 'Customers'), ('internal', 'Internal')], 'Type of Operation', required=True)

class Route(models.Model):
    _inherit = 'stock.location.route'
    
    place_from = fields.Many2one('stock.warehouse', 'From')
    place_dest = fields.Many2one('stock.warehouse', 'To')
    reception_type = fields.Selection([('direct', 'Direct'), ('delivery', 'Delivery')], string="Reception type")
    hours = fields.Integer('Hours')
    minutes = fields.Integer('Minutes')
    duration = fields.Char('Duration', compute='calc_duration')
    
    @api.multi 
    def calc_duration(self):
        for program in self:
            if program.hours and program.minutes:
                program.duration = "{}س : {}دق".format(program.hours, program.minutes)


class StockPickingBatch(models.Model):
    _name = 'stock.picking.batch'
    _inherit = ['stock.picking.batch', 'barcodes.barcode_events_mixin']
    _order = 'id asc'



    driver_id = fields.Many2one('hr.employee', string="Driver")
    trip_id = fields.Many2one('freight_sys.trips', string='Trip')
    type = fields.Selection([('loading', 'Loading'),
                               ('downloading', 'Downloading')], string='Type')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], default='draft',
        copy=False, track_visibility='onchange', required=True)
#     scan_float = fields.Float()
#     barcode_nomenclature_id = fields.Many2one(
#         'barcode.nomenclature', 'Barcode Nomenclature')

    
    @api.multi
    def done(self):
        pickings_todo = self.mapped('picking_ids')
        pickings_todo.action_assign()
        done_batch = super(StockPickingBatch, self).done()
        for batch in self:
            for pick in batch.picking_ids:
                for policy in pick.policy_id:
                    policy.current_location = pick.location_dest_id.id
                    if policy.is_returned == False:
                        if pick.picking_type_id.warehouse_id == policy.place_from and pick.picking_type_id.code == 'incoming':
                            policy.state = 'source'
                        elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'incoming':
                            policy.state = 'destination'
                        elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'to_delivery':
                            policy.state = 'to_delivery'
                        elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'outgoing':
                            policy.state = 'received'
                        else: 
                            policy.state = 'in_way'
                    if policy.trip_id:
                        if policy.route_id.place_dest.lot_stock_id.id == policy.trip_id.route_id.place_dest.lot_stock_id.id and batch.type == 'downloading':
                            policy.is_routed = False
                            policy.trip_id.write({
                                'policy_ids': [(3, policy.id, False)]
                                })
                    
        return done_batch
    
    def on_barcode_scanned(self, barcode):
        for pick in self.picking_ids:
            for move in pick.move_line_ids:
                if barcode == move.product_barcode:
                    if move.qty_done == 0.0:
                        pick.done_freights += 1
                    move.write({
                        'qty_done': 1.0
                        })

                    pick.compute_lines_pick()
                    
            pick.compute_is_done()
                
            

                     



    
class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _order = 'id asc'



    @api.depends('move_lines')
    def compute_lines_pick(self):
        for item in self:
            freights_name=""
            qty_freights_done=""
            for rev in item.move_lines:
                freights_name = freights_name + rev.product_id.name + '\n'
                qty_freights_done = qty_freights_done + str(rev.quantity_done) + '\n'
                item.freights_name =  freights_name
                item.qty_freights_done = qty_freights_done
                
    policy_id = fields.Many2one('freight_sys.policy', string="policy Orders", readonly=True)
    is__return = fields.Boolean('Is return', default=False, readonly=True)
    location_dest_load = fields.Many2one('stock.location', string='Location Dest Load')
    location_dest_download = fields.Many2one('stock.location', string='Location Dest Download')
    freights_name = fields.Text('Freights', compute='compute_lines_pick')
    qty_freights_done = fields.Text('Done Quantity', compute='compute_lines_pick')
    done_freights = fields.Float('Freights Quantity Done')
    is__done = fields.Boolean(compute='compute_is_done')
    trip_id = fields.Many2one('freight_sys.trips', 'Trip')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")  
    driver_id = fields.Many2one('hr.employee', sring="Driver")
    date_validation = fields.Datetime("Validation Date")
    def compute_is_done(self):
        for pick in self:
            pick.is__done = True
            for move in pick.move_lines:
                if move.quantity_done == 0:
                    pick.is__done = False
            
                
                
                
                
    
    @api.model
    def create(self, vals):
        line = super(StockPicking, self).create(vals)
        for pick in line:
            policy = line.env['freight_sys.policy'].search([('name','like',line.origin)],limit=1)
            if policy:
                pick.policy_id = policy.id
            if pick.policy_id.is_returned == True:
                line.is__return = True
        return line

    @api.multi
    def button_validate(self):
        valid_pick = super(StockPicking, self).button_validate()
        
        for pick in self:
            pick.date_validation = datetime.now()
            for policy in pick.policy_id:
                policy.current_location = pick.location_dest_id.id
                if pick.is__return == False:
                    if pick.picking_type_id.warehouse_id == policy.place_from and pick.picking_type_id.code == 'incoming':
                        policy.state = 'source'
                    elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'incoming':
                        policy.state = 'destination'
                    elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'to_delivery':
                            policy.state = 'to_delivery'
                    elif pick.picking_type_id.warehouse_id == policy.place_dest and pick.picking_type_id.code == 'outgoing':
                            policy.state = 'received'
                    else: 
                        policy.state = 'in_way'
#                 if policy.trip_id:
#                     if policy.route_id.place_dest.lot_stock_id.id == policy.trip_id.line_id.place_to.lot_stock_id.id:
#                         policy.is_routed = False
#                         policy.trip_id.write({
#                             'policy_ids': [(3, policy.id, False)]
#                             })
        return valid_pick
    @api.model
    def _create_backorder(self, backorder_moves=[]):
        res = super(StockPicking, self)._create_backorder(backorder_moves)
        
        return res
    
    

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    barcode = fields.Char(related="product_id.barcode", readonly=True)
    policy_line_id = fields.Many2one('freight_sys.policy.line',
        'Purchase Order Line', ondelete='set null', index=True, readonly=True, copy=False)
    created_policy_line_id = fields.Many2one('freight_sys.policy.line',
        'Created policy Order Line', ondelete='set null', readonly=True, copy=False)


    def _action_confirm(self, merge=True):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc = self.env['stock.move']
        move_to_confirm = self.env['stock.move']
        move_waiting = self.env['stock.move']

        to_assign = {}
        for move in self:
            # if the move is preceeded, then it's waiting (if preceeding move is done, then action_assign has been called already and its state is already available)
            if move.move_orig_ids:
                move_waiting |= move
            else:
                if move.procure_method == 'make_to_order':
                    move_create_proc |= move
                else:
                    move_to_confirm |= move
            if not move.picking_id and move.picking_type_id:
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                if key not in to_assign:
                    to_assign[key] = self.env['stock.move']
                to_assign[key] |= move

        # create procurements for make to order moves
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = (move.group_id and move.group_id.name or (move.rule_id and move.rule_id.name or move.origin or move.picking_id.name or "/"))
            self.env['procurement.group'].run(move.product_id, move.product_uom_qty, move.product_uom, move.location_id, move.rule_id and move.rule_id.name or "/", origin,
                                              values)

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})

        # assign picking in batch for all confirmed move that share the same details
        for moves in to_assign.values():
            moves._assign_picking()
        self._push_apply()
        if merge:
            return self._merge_moves()
        return self
    
    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('policy_line_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.policy_line_id.id)
        return keys_sorted

    @api.multi
    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.policy_line_id and self.product_id.id == self.policy_line_id.product_id.id:
            line = self.policy_line_id
            price_unit = line.price_unit
            return price_unit
        return super(StockMove, self)._get_price_unit()

    def _prepare_extra_move_vals(self, qty):
        vals = super(StockMove, self)._prepare_extra_move_vals(qty)
        vals['policy_line_id'] = self.policy_line_id.id
        return vals

    def _prepare_move_split_vals(self, uom_qty):
        vals = super(StockMove, self)._prepare_move_split_vals(uom_qty)
        vals['policy_line_id'] = self.policy_line_id.id
        return vals

    def _merge_moves(self):
        vals = super(StockMove, self)._merge_moves()
        for move in vals:
            
            for dest in move.move_dest_ids:
                move.picking_id.location_dest_load = dest.location_dest_id
                break
            for orig in move.move_orig_ids:
                move.picking_id.location_dest_download = orig.location_id
                break
        return vals
        


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    vehicle_ids = fields.One2many('fleet.vehicle','warehouse_id', string="Vehicles")


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super(ReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        vals['policy_line_id'] = return_line.move_id.policy_line_id.id
        return vals


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        res = super(Orderpoint, self)._quantity_in_progress()
        for poline in self.env['freight_sys.policy.line'].search([('state','in',('draft','sent','to approve')),('orderpoint_id','in',self.ids)]):
            res[poline.orderpoint_id.id] += poline.product_uom._compute_quantity(poline.product_qty, poline.orderpoint_id.product_uom, round=False)
        return res

    
    
    
    
    
    
    
