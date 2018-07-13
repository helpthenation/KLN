# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.exceptions import Warning
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging


_logger = logging.getLogger(__name__)

class stock_move(osv.osv):
    _inherit = 'stock.move'

    def create(self, cr, uid, vals, context=None):
        if vals.get('name') is None and vals.get('product_id') is not None:
           product = self.pool.get('product.product').browse(cr, uid, [vals.get('product_id')], context=context)[0]
           vals.update({'name':product.partner_ref or '/'})     
        if context is None:
            context = {}
        picking_obj = self.pool['stock.picking']
        track = not context.get('mail_notrack') and vals.get('picking_id')
        if track:
            picking = picking_obj.browse(cr, uid, vals['picking_id'], context=context)
            initial_values = {picking.id: {'state': picking.state}}
        res = super(stock_move, self).create(cr, uid, vals, context=context)
        if track:
            picking_obj.message_track(cr, uid, [vals['picking_id']], picking_obj.fields_get(cr, uid, ['state'], context=context), initial_values, context=context)
        return res
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
        (and company). Those attributes are also given as parameters.
        """
        pick_obj = self.pool.get("stock.picking")
        # Use a SQL query as doing with the ORM will split it in different queries with id IN (,,)
        # In the next version, the locations on the picking should be stored again.
        query = """
            SELECT stock_picking.id FROM stock_picking, stock_move
            WHERE
                stock_picking.state in ('draft', 'confirmed', 'waiting') AND
                stock_move.picking_id = stock_picking.id AND
                stock_move.location_id = %s AND
                stock_move.location_dest_id = %s AND
        """
        params = (location_from, location_to)
        if not procurement_group:
            query += "stock_picking.group_id IS NULL LIMIT 1"
        else:
            query += "stock_picking.group_id = %s LIMIT 1"
            params += (procurement_group,)
        cr.execute(query, params)
        [pick] = cr.fetchone() or [None]
        if not pick:
            move = self.browse(cr, uid, move_ids, context=context)[0]
            values = self._prepare_picking_assign(cr, uid, move, context=context)
            pick = pick_obj.create(cr, uid, values, context=context)
        for move_id in move_ids:
            cr.execute("""
                select po.sale_line_id
                FROM stock_move sm
                LEFT JOIN procurement_order po
                ON sm.procurement_id = po.id 
                LEFT JOIN sale_order_line sol
                ON po.sale_line_id = sol.id
                where  sm.id = %d           
            """%(move_id))
            val=cr.dictfetchone()
            if val:
                so=self.pool.get('sale.order.line').browse(cr,uid,val['sale_line_id'],context=context)
                self.write(cr, uid, move_id, {'item_no': so.item_no,'uom':so.uom}, context=context)
        return self.write(cr, uid, move_ids,{'picking_id': pick}, context=context)
