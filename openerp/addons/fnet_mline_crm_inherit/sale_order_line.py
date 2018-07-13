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

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def _order_exists(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = False
            for line in sale.order_line:
                if line.ordered:
                    res[sale.id] = True
        return res
    def _order_completed(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for sale in self.browse(cursor, user, ids, context=context):
            res[sale.id] = True
            for line in sale.order_line:
                if not line.ordered:
                    res[sale.id] = False
        return res            
    _columns={
        'order_exists': fields.function(_order_exists, string='Ordered',
            type='boolean', help="It indicates that sales quotation has at least one order."),    
        'order_completed': fields.function(_order_completed, string='Ordered',
            type='boolean', help="It indicates that sales quotation has at least one order."),    
        #~ 'sq_ordered_lines': fields.many2many('sale.order.line', 'salequote_saleorder_rel', 'quote_line_id', 'new_so_id', 'New Ordered Lines', readonly=True, copy=False),            
        'state': fields.selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('cancel', 'Cancelled'),
        ('waiting_date', 'Waiting Schedule'),
        ('draft_so', 'Draft Sales Order'),
        ('progress', 'Sales Order'),
        ('manual', 'Sale to Invoice'),
        ('shipping_except', 'Shipping Exception'),
        ('invoice_except', 'Invoice Exception'),
        ('done', 'Done'),
        ], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
          \nThe exception status is automatically set when a cancel operation occurs \
          in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
           but waiting for the scheduler to run on the order date.", select=True),
           
           
    }

    def action_view_orderedsq(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        sale_obj = self.browse(cr,uid,ids)

        result = mod_obj.get_object_reference(cr, uid, 'fnet_mline_crm_inherit', 'action_sq_so_view')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = []
        cr.execute("""SELECT 
                          distinct so_rel.ordered_id as new_id
                        FROM sale_order_line sol
                        JOIN sale_quotation_line_order_rel so_rel ON sol.id = so_rel.quotation_line_id
                        WHERE sol.order_id=%d"""%(sale_obj.id))  
        new_ids = cr.dictfetchall()     
        if  new_ids:
            for i in new_ids:
                if i['new_id'] != None: 
                    inv_ids.append(i['new_id'])
        #choose the view_mode accordingly
        print'IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII',inv_ids
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        print'RESULTTTTT',result
        return result
            
class sale_order_line_inherit(osv.osv):
    _inherit = 'sale.order.line'
    
    def _order_lines_from_sale(self, cr, uid, ids, context=None):
        # direct access to the m2m table is the less convoluted way to achieve this (and is ok ACL-wise)
        cr.execute("""SELECT DISTINCT sol.id FROM sale_quotation_line_order_rel rel JOIN
                                                  sale_order_line sol ON (sol.order_id = rel.ordered_id)
                                    WHERE rel.ordered_id = ANY(%s)""", (list(ids),))
        return [i[0] for i in cr.fetchall()] 
    
    def _fnct_line_ordered(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        for this in self.browse(cr, uid, ids, context=context):
            res[this.id] = this.quotation_lines and \
                all(iline.ordered_id.state != 'cancel' for iline in this.quotation_lines) 
        return res  
        
    _columns = { 
              'quotation_lines': fields.many2many('sale.order.line', 'sale_quotation_line_order_rel', 'quotation_line_id', 'ordered_id', 'Ordered Lines', readonly=True, copy=False),
              'ordered': fields.function(_fnct_line_ordered, string='Ordered', type='boolean',
                    store={
                        'sale.order': (_order_lines_from_sale, ['state'], 10),
                        'sale.order.line': (lambda self,cr,uid,ids,ctx=None: ids, ['invoice_lines'], 10)
                    }),              
              }        

    #~ def _prepare_order_line_ordered_line(self, cr, uid, line,context=None):
        #~ """Prepare the dict of values to create the new invoice line for a
           #~ sales order line. This method may be overridden to implement custom
           #~ invoice generation (making sure to call super() to establish
           #~ a clean extension chain).
#~ 
           #~ :param browse_record line: sale.order.line record to invoice
           #~ :param int account_id: optional ID of a G/L account to force
               #~ (this is used for returning products including service)
           #~ :return: dict of values to create() the invoice line
        #~ """
        #~ res = {}
        #~ if not line.invoiced:
            #~ uosqty = self._get_line_qty(cr, uid, line, context=context)
            #~ uos_id = self._get_line_uom(cr, uid, line, context=context)
            #~ pu = 0.0
            #~ if uosqty:
                #~ pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        #~ self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            #~ fpos = line.order_id.fiscal_position or False
         #~ 
            #~ res = {
                #~ 'name': line.name,
                #~ 'sequence': line.sequence,
                #~ 'origin': line.order_id.name,
                #~ 'price_unit': pu,
                #~ 'product_uom_qty': uosqty,
                #~ 'discount': line.discount,
                #~ 'product_uos': uos_id,
                #~ 'product_id': line.product_id.id or False,
                #~ 'tax_id': [(6, 0, [x.id for x in line.tax_id])],
            #~ }
            #~ so_create.append((0, 0, res))
        #~ return res    
    #~ 
    #~ def ordered_line_create(self, cr, uid, ids, context=None):
        #~ if context is None:
            #~ context = {}
#~ 
        #~ create_ids = []
        #~ sales = set()
        #~ line_obj=self.pool.get('sale.order.line').browse(cr,uid,ids[0])
        #~ print'LINEOBJJJJJJJ',line_obj
        #~ sale_obj=self.pool.get('sale.order').browse(cr,uid,line_obj.order_id.id)
        #~ new_order = self.pool.get('sale.order').create(cr, uid, {
                #~ 'name': self.pool.get('ir.sequence').next_by_code(cr, uid, 'sale.order'),
                #~ 'partner_id': sale_obj.partner_id.id,
                #~ 'origin':sale_obj.name,
                #~ 'validity_date': sale_obj.validity_date,
                #~ 'order_line': so_create,
                #~ 'pricelist_id': sale_obj.pricelist_id.id
            #~ }) 
        #~ print'NEWORDERRRRRRRRRRRRRRRRR',new_order         
        #~ for line in self.browse(cr, uid, ids, context=context):
            #~ vals = self._prepare_order_line_ordered_line(cr, uid, line,context)
            #~ if vals:
                #~ vals.update({'order_id':new_order})
                #~ inv_id = self.pool.get('sale.order.line').create(cr, uid, vals, context=context)
                #~ self.write(cr, uid, [line.id], {'quotation_lines': [(4, inv_id)]}, context=context)
                #~ sales.add(line.order_id.id)
                #~ create_ids.append(inv_id)
        #~ # Trigger workflow events
        #~ for sale_id in sales:
            #~ workflow.trg_write(uid, 'sale.order', sale_id, cr)
        #~ return create_ids  
