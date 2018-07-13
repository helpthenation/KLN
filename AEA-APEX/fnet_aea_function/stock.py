
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from datetime import date, datetime
import datetime


class delivery_method(osv.osv):
    _name = 'delivery.method'
    _rec_name = 'method_type'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
        'method_type': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Type', required=True),
        'partner_id':fields.many2one('res.partner', 'Tranport Co. Name', required=True),
        'company_id': fields.many2one('res.company', 'Company'),
        }
        
    _defaults = {
        'company_id': _get_default_company,
    }
delivery_method()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
    
    'prod_categ_id': fields.many2one('product.category', 'Product Category'),
    'del_method': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Type'),
    'actual_return':fields.boolean('Actual Return'),
    }

    _defaults = {
        'actual_return': False,
    }
       
    def action_invoice_create(self, cr, uid, ids, journal_id, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        context = context or {}
        todo = {}
        for picking in self.browse(cr, uid, ids, context=context):
            partner = self._get_partner_to_invoice(cr, uid, picking, dict(context, type=type))
            #grouping is based on the invoiced partner
            if group:
                key = partner
            else:
                key = picking.id
            for move in picking.move_lines:
                if move.invoice_state == '2binvoiced':
                    if (move.state != 'cancel') and not move.scrapped:
                        todo.setdefault(key, [])
                        todo[key].append(move)
        invoices = []
        for moves in todo.values():
            invoices += self._invoice_create_line(cr, uid, ids, moves, journal_id, type, context=context)
        return invoices

    def _get_invoice_vals(self, cr, uid, ids, key, inv_type, journal_id, move, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids)
        sale = self.pool.get('sale.order').search(cr, uid, [('procurement_group_id', '=', obj.group_id.id)], context=context)
        print sale,obj.group_id.name
        sale_obj = self.pool.get('sale.order').browse(cr, uid, sale[0])
        if obj.picking_type_id.code == 'outgoing':
            #~ pay_sr = self.pool.get('account.payment.term.line').search(cr, uid, [('payment_id', '=', sale_obj.payment_term.id)], context=context)
            #~ pay_obj = self.pool.get('account.payment.term.line').browse(cr, uid, pay_sr[0])
            #~ date_1 = datetime.datetime.strptime(sale_obj.date_order, "%Y-%m-%d")
            #~ end_date = date_1 + datetime.timedelta(days=pay_obj.days)
            partner, currency_id, company_id, user_id = key
            if inv_type in ('out_invoice', 'out_refund'):
                account_id = partner.property_account_receivable.id
                payment_term = partner.property_payment_term.id or False
            else:
                account_id = partner.property_account_payable.id
                payment_term = partner.property_supplier_payment_term.id or False
            return {
                'origin': move.picking_id.name,
                'date_invoice': sale_obj.date_order,
                'user_id': user_id,
                'partner_id': partner.id,
                'account_id': account_id,
                'payment_term': sale_obj.payment_term.id,
                'type': inv_type,
                'fiscal_position': partner.property_account_position.id,
                'company_id': company_id,
                'currency_id': currency_id,
                'journal_id': journal_id,
                'category_id':sale_obj.prod_categ_id.id,
                'del_method':sale_obj.del_method,
                'tpt_name':sale_obj.tpt_name.id,
                'section_id':sale_obj.section_id.id,
                'disc_value':sale_obj.disc_value,
            }
        else:
            partner, currency_id, company_id, user_id = key
            if inv_type in ('out_invoice', 'out_refund'):
                account_id = partner.property_account_receivable.id
                payment_term = partner.property_payment_term.id or False
            else:
                account_id = partner.property_account_payable.id
                payment_term = partner.property_supplier_payment_term.id or False
            return {
                'origin': move.picking_id.name,
                'date_invoice': sale_obj.date_order,
                'user_id': user_id,
                'partner_id': partner.id,
                'account_id': account_id,
                'payment_term': payment_term,
                'type': inv_type,
                'fiscal_position': partner.property_account_position.id,
                'company_id': company_id,
                'currency_id': currency_id,
                'journal_id': journal_id,
                'section_id':sale_obj.section_id.id,
                'disc_value':sale_obj.disc_value,
            }

    def _invoice_create_line(self, cr, uid, ids, moves, journal_id, inv_type='out_invoice', context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids)
        sale = self.pool.get('sale.order').search(cr, uid, [('procurement_group_id', '=', obj.group_id.id)], context=context)
        print sale,obj.group_id.name
        sale_obj = self.pool.get('sale.order').browse(cr, uid, sale[0])
        sale_line_obj = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_obj.id)], context=context)
        invoice_obj = self.pool.get('account.invoice')
        move_obj = self.pool.get('stock.move')
        invoices = {}
        is_extra_move, extra_move_tax = move_obj._get_moves_taxes(cr, uid, moves, inv_type, context=context)
        product_price_unit = {}
        for move in moves:
            #~ sale_lines = [ move.procurement_id.sale_line_id for move in stock_move_obj.browse(cr, uid, move_ids) if move.procurement_id and move.procurement_id.sale_line_id] 
            print move.product_id.mrp_price
            company = move.company_id
            origin = move.picking_id.name
            partner, user_id, currency_id = move_obj._get_master_data(cr, uid, move, company, context=context)

            key = (partner, currency_id, company.id, user_id)
            invoice_vals = self._get_invoice_vals(cr, uid, ids, key, inv_type, journal_id, move, context=context)

            if key not in invoices:
                # Get account and payment terms
                invoice_id = self._create_invoice_from_picking(cr, uid, move.picking_id, invoice_vals, context=context)
                invoices[key] = invoice_id
            else:
                invoice = invoice_obj.browse(cr, uid, invoices[key], context=context)
                merge_vals = {}
                if not invoice.origin or invoice_vals['origin'] not in invoice.origin.split(', '):
                    invoice_origin = filter(None, [invoice.origin, invoice_vals['origin']])
                    merge_vals['origin'] = ', '.join(invoice_origin)
                if invoice_vals.get('name', False) and (not invoice.name or invoice_vals['name'] not in invoice.name.split(', ')):
                    invoice_name = filter(None, [invoice.name, invoice_vals['name']])
                    merge_vals['name'] = ', '.join(invoice_name)
                if merge_vals:
                    invoice.write(merge_vals)
            invoice_line_vals = move_obj._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=dict(context, fp_id=invoice_vals.get('fiscal_position', False)))
            invoice_line_vals['invoice_id'] = invoices[key]
            invoice_line_vals['origin'] = origin
            invoice_line_vals['mrp_price'] = move.product_id.mrp_price
            invoice_line_vals['discounts'] = move.procurement_id.sale_line_id.discounts
            invoice_line_vals['disc_price_unit'] = move.procurement_id.sale_line_id.disc_price_unit
            invoice_line_vals['gross_amount'] = move.procurement_id.sale_line_id.gross_amount
            invoice_line_vals['product_discount'] = move.procurement_id.sale_line_id.product_discount
            if not is_extra_move[move.id]:
                product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']] = invoice_line_vals['price_unit']
            if is_extra_move[move.id] and (invoice_line_vals['product_id'], invoice_line_vals['uos_id']) in product_price_unit:
                invoice_line_vals['price_unit'] = product_price_unit[invoice_line_vals['product_id'], invoice_line_vals['uos_id']]
            if is_extra_move[move.id]:
                desc = (inv_type in ('out_invoice', 'out_refund') and move.product_id.product_tmpl_id.description_sale) or \
                    (inv_type in ('in_invoice','in_refund') and move.product_id.product_tmpl_id.description_purchase)
                invoice_line_vals['name'] += ' ' + desc if desc else ''
                if extra_move_tax[move.picking_id, move.product_id]:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[move.picking_id, move.product_id]
                #the default product taxes
                elif (0, move.product_id) in extra_move_tax:
                    invoice_line_vals['invoice_line_tax_id'] = extra_move_tax[0, move.product_id]

            print'invoice_line_vals',invoice_line_vals
            move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)
            move_obj.write(cr, uid, move.id, {'invoice_state': 'invoiced'}, context=context)

        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoices.values()
        
class stock_return_picking(osv.osv_memory):
    _inherit = 'stock.return.picking'    
    
    _columns={
        'actual_return':fields.boolean('Actual Return'),
    }

    def _create_returns(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.line')
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        returned_lines = 0
        
        # Cancel assignment of existing chained assigned moves
        moves_to_unreserve = []
        for move in pick.move_lines:
            to_check_moves = [move.move_dest_id] if move.move_dest_id.id else []
            while to_check_moves:
                current_move = to_check_moves.pop()
                if current_move.state not in ('done', 'cancel') and current_move.reserved_quant_ids:
                    moves_to_unreserve.append(current_move.id)
                split_move_ids = move_obj.search(cr, uid, [('split_from', '=', current_move.id)], context=context)
                if split_move_ids:
                    to_check_moves += move_obj.browse(cr, uid, split_move_ids, context=context)

        if moves_to_unreserve:
            move_obj.do_unreserve(cr, uid, moves_to_unreserve, context=context)
            #break the link between moves in order to be able to fix them later if needed
            move_obj.write(cr, uid, moves_to_unreserve, {'move_orig_ids': False}, context=context)

        #Create new picking for returned products
        pick_type_id = pick.picking_type_id.return_picking_type_id and pick.picking_type_id.return_picking_type_id.id or pick.picking_type_id.id
        new_picking = pick_obj.copy(cr, uid, pick.id, {
            'move_lines': [],
            'picking_type_id': pick_type_id,
            'state': 'draft',
            'origin': pick.name,
            'actual_return':data['actual_return'],
        }, context=context)

        for data_get in data_obj.browse(cr, uid, data['product_return_moves'], context=context):
            move = data_get.move_id
            if not move:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            if new_qty:
                # The return of a return should be linked with the original's destination move if it was not cancelled
                if move.origin_returned_move_id.move_dest_id.id and move.origin_returned_move_id.move_dest_id.state != 'cancel':
                    move_dest_id = move.origin_returned_move_id.move_dest_id.id
                else:
                    move_dest_id = False

                returned_lines += 1
                move_obj.copy(cr, uid, move.id, {
                    'product_id': data_get.product_id.id,
                    'product_uom_qty': new_qty,
                    'product_uos_qty': new_qty * move.product_uos_qty / move.product_uom_qty,
                    'picking_id': new_picking,
                    'state': 'draft',
                    'location_id': move.location_dest_id.id,
                    'location_dest_id': move.location_id.id,
                    'picking_type_id': pick_type_id,
                    'warehouse_id': pick.picking_type_id.warehouse_id.id,
                    'origin_returned_move_id': move.id,
                    'procure_method': 'make_to_stock',
                    'restrict_lot_id': data_get.lot_id.id,
                    'move_dest_id': move_dest_id,
                })
        pick_obj.write(cr, uid, record_id, {'actual_return': data['actual_return']}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        pick_obj.action_confirm(cr, uid, [new_picking], context=context)
        pick_obj.action_assign(cr, uid, [new_picking], context)
        return new_picking, pick_type_id
