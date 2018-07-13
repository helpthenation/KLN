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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class sale_advance_payment_order(osv.osv_memory):
    _name = "sale.advance.payment.order"
    _description = "Sales Advance Payment Invoice"

    _columns = {
        'advance_payment_method':fields.selection(
            [('all', 'Ordered The Whole Quotation Lines'), ('lines', 'Some Quotation Lines')],
            'What do you want to order?', required=True,
            help="""Use Ordered the whole sale order to create the final sale order.
                Use Some Quotation Lines to order a selection of the sales order lines."""),
    }


    _defaults = {
        'advance_payment_method': 'all',
    }

    def create_invoices(self, cr, uid, ids, context=None):
        """ create invoices for the active sales orders """
        sale_obj = self.pool.get('sale.order')
        act_window = self.pool.get('ir.actions.act_window')
        wizard = self.browse(cr, uid, ids[0], context)
        sale_ids = context.get('active_ids', [])
        if wizard.advance_payment_method == 'all':
            # create the final invoices of the active sales orders
            res = sale_obj.manual_invoice(cr, uid, sale_ids, context)
            if context.get('open_invoices', False):
                sales_order_line_obj = self.pool.get('sale.order.line')
                sales_order_obj = self.pool.get('sale.order')
                so_create = []
                get_id=[]
                line_id=[]
                for line in sales_order_obj.browse(cr, uid, sale_ids[0]).order_line:
                    line.write({'ordered':True})
                    cr.execute("""update sale_order_line set ordered=True where id=%d"""%(line.id))
                    create_obt = {
                        'product_id': line.product_id.id,
                        'name': line.name,
                        'product_uom_qty': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'tax_id': [(6, 0, [x.id for x in line.tax_id])],
                        'product_uom': line.product_uom.id,
                        'price_subtotal': line.price_subtotal,                
                        'item_no':line.item_no,
                        'uom':line.uom,
                        'part_no': line.part_no,
                        'make_no': line.make_no,
                        'offer_id': line.offer_id.id,
                        'sale_call_id': line.sale_call_id.id,
                        'purchase_id': line.purchase_id.id,
                        'order_code':line.order_code,
                    }
                    so_create.append((0, 0, create_obt))
                    get_id.append(line.order_id.id) 
                    line_id.append(line.id) 
                sale_obj=sales_order_obj.browse(cr,uid,sale_ids[0])
                res=self.pool.get('sale.order').create(cr,uid, {
                    'origin': sale_obj.name,
                    #~ 'name': self.pool.get('ir.sequence').next_by_code(cr, uid, 'sale.order'),
                    'partner_id': sale_obj.partner_id.id,
                    'order_line': so_create,
                    'pricelist_id': sale_obj.pricelist_id.id,
                    'state':'draft_so',
                    'date_order': sale_obj.date_order,
                    'client_order_ref': sale_obj.client_order_ref,
                    'lpo_no': sale_obj.lpo_no,
                    'currency_id':sale_obj.currency_id and sale_obj.currency_id.id or False,
                    'user_id': sale_obj.user_id.id,
                    'section_id': sale_obj.section_id and sale_obj.section_id.id or False,
                    'payment_term':sale_obj.payment_term and sale_obj.payment_term.id or False,
                    'fiscal_position':sale_obj.fiscal_position and sale_obj.fiscal_position.id or False,
                    'company_id': sale_obj.company_id and sale_obj.company_id.id or False, 
                    'lead_id': sale_obj.lead_id and sale_obj.lead_id.id or False,            
                    'request_id': sale_obj.request_id and sale_obj.request_id.id or False,            
                    'project_id': sale_obj.project_id and sale_obj.project_id.id or False,   
                    'parent_so': sale_obj and sale_obj.id or False, 
                    })     
                for val in line_id:
                    #~ cr.execute('insert into salequote_saleorder_rel (quote_line_id,new_so_id) values (%s,%s)', (val, res))
                    cr.execute('insert into sale_quotation_line_order_rel (quotation_line_id,ordered_id) values (%s,%s)', (val, res))                         
                return self.open_invoices(cr, uid, ids, res, context=context)
            return {'type': 'ir.actions.act_window_close'}

        if wizard.advance_payment_method == 'lines':
            # open the list view of sales order lines to invoice
            res = act_window.for_xml_id(cr, uid, 'fnet_mline_crm_inherit', 'action_order_line_tree22222', context)
            res['context'] = {
                'search_default_unordered': 1,
                'search_default_order_id': sale_ids and sale_ids[0] or False,
            }
            return res

        if context.get('open_invoices', False):
            return self.open_invoices( cr, uid, ids, inv_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def open_invoices(self, cr, uid, ids, invoice_ids, context=None):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_order_form')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(cr, uid, 'sale', 'view_order_tree')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Sale Order'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'sale.order',
            'res_id': invoice_ids,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'context': {'type': 'out_invoice'},
            'type': 'ir.actions.act_window',
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
