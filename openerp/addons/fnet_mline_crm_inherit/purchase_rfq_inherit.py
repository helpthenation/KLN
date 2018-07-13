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

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import sys;
reload(sys);
sys.setdefaultencoding("utf8")


class purchase_requisition_inherit(osv.osv):
    _inherit = 'purchase.requisition'
    _columns = {
             'lead_seq_id':fields.many2one('crm.lead', 'Enquiry Ref', readonly=True),
             'sale_line': fields.one2many('request.so.line', 'so_id', 'So line'),
             'offer' : fields.float('Offer',digits=(16, 0), readonly = True),
             'date_end': fields.datetime('Date'),
               }
               
    def _get_picking_type(self, cr, uid, context=None):
        obj_data = self.pool.get('ir.model.data')
        type_obj = self.pool.get('stock.picking.type')
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)], context=context)
        if not types:
            types = type_obj.search(cr, uid, [('code', '=', 'incoming'), ('warehouse_id', '=', False)], context=context)
            if not types:
                raise osv.except_osv(_('Error!'), _("Make sure you have at least an incoming picking type defined"))
        return types[0]              

        
    _defaults = {
                'offer': 1,
                'date_end': fields.datetime.now, 
                'picking_type_id': _get_picking_type,
                }
    
    
    def view_income(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        '''
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        dummy, action_id = tuple(mod_obj.get_object_reference(cr, uid, 'stock', 'action_picking_tree'))
        action = self.pool.get('ir.actions.act_window').read(cr, uid, action_id, context=context)

        pick_ids = self.pool.get('stock.picking').search(cr, uid, [('request_id', '=', obj.id)], context=context)

        #override the context to get rid of the default filtering on picking type
        action['context'] = {}
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'stock', 'view_picking_form')
            action['views'] = [(res and res[1] or False, 'form')]
            action['res_id'] = pick_ids and pick_ids[0] or False
        return action
        return result
    
    def view_invoice(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        '''
        This function returns an action that display existing invoices of given Time sheet ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        inv_ids = self.pool.get('account.invoice').search(cr, uid, [('request_id', '=', obj.id)], context=context)
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result
            
    def req_create_multiple(self, cr, uid, ids, context=None):
        req_bro = self.browse(cr, uid, ids)
        for line_bro in req_bro.line_ids:
            print'FFFFFFFFFFFFFFFFFFFFFF',line_bro
            cr.execute(''' select
                                partner_id 
                           from 
                                request_partner_rel
                           where request_id=%s ''' % (line_bro.id))
            sup_ids = cr.fetchall()
            for sup_id in sup_ids:
                sup = self.pool.get('res.partner').browse(cr, uid, sup_id)
                purchase_sr = self.pool.get('purchase.order').search(cr, uid, [('requisition_id', '=', req_bro.id),('partner_id','=',sup.id)], context=context)
                if purchase_sr:
                    vals = {
                           'purchase_history_id':purchase_sr[0],
                           'product_id':line_bro.product_id.id,
                           #~ 'name':'test',
                           'name':line_bro.product_id.product_tmpl_id.description_purchase or line_bro.product_id.description or line_bro.product_id.name,
                           'uom_id':line_bro.product_uom_id.id,
                           'product_qty':line_bro.product_qty,
                           'part_no':line_bro.part_no,
                           'make_no':line_bro.make_no,
                           'item_no':line_bro.item_no,
                           }
                    pur_line2 = self.pool.get('purchase.order.line').create(cr, uid, self._prepare_purchase_order_line(cr, uid, req_bro, line_bro, purchase_sr[0], sup, context=context), context=context)
                    self.pool.get('purchase.order.line').write(cr, uid, [pur_line2], {'part_no':line_bro.part_no, 'make_no':line_bro.make_no, 'item_no':line_bro.item_no,'color':True})
                    self.pool.get('history.order.line').create(cr, uid, vals, context=context)
                else:
                    context.update({'mail_create_nolog': True})
                    purchase_id = self.pool.get('purchase.order').create(cr, uid, self._prepare_purchase_order(cr, uid, req_bro, sup, context=context), context=context)
                    self.pool.get('purchase.order').write(cr, uid, [purchase_id], {'lead_id':req_bro.lead_seq_id.id}, context=context)
                    self.pool.get('purchase.order').message_post(cr, uid, [purchase_id], body=_("RFQ created"), context=context)
                    pur_line = self.pool.get('purchase.order.line').create(cr, uid, self._prepare_purchase_order_line(cr, uid, req_bro, line_bro, purchase_id, sup, context=context), context=context)
                    self.pool.get('purchase.order.line').write(cr, uid, [pur_line], {'part_no':line_bro.part_no, 'color':True ,'make_no':line_bro.make_no,'item_no':line_bro.item_no, 'request_id':req_bro.id})
                    vals = {
                           'purchase_history_id':purchase_id,
                           'product_id':line_bro.product_id.id,
                           #~ 'name':'test',
                           'name':line_bro.product_id.product_tmpl_id.description_purchase or line_bro.product_id.description or line_bro.product_id.name,
                           'uom_id':line_bro.product_uom_id.id,
                           'product_qty':line_bro.product_qty,
                           'part_no':line_bro.part_no,
                           'make_no':line_bro.make_no,
                           'item_no':line_bro.item_no,
                           }
                    self.pool.get('history.order.line').create(cr, uid, vals, context=context)
        return self.write(cr, uid, ids, {'state': 'open'}, context=context)

    def write(self, cr, uid, ids, vals, context=None):
       
        obj = self.browse(cr, uid, ids)
        
        return super(purchase_requisition_inherit, self).write(cr, uid, ids, vals, context=context)
    
    def validate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        for line in obj.sale_line:
            percen = line.unit_price * line.margin_id.amount
            percen_tot = percen + line.unit_price
            total = line.product_qty * percen_tot
            self.pool.get('request.so.line').write(cr, uid, line.id, {'margin':percen_tot, 'margin_price':total}, context=context)
        return True
        
    def _so_create(self, cr, uid, obj, line, context=None):
        vals = {
           'partner_id':obj.lead_seq_id.partner_id.id,
           'client_order_ref':obj.lead_seq_id.client_order_ref,
           'request_id':obj.id,
           'lead_id':obj.lead_seq_id.id,
           'offer':'OFFER ' + str(int(obj.offer)),
                  }
        sale_obj = self.pool.get('sale.order').create(cr, uid, vals, context=context)
        for prod in line:
            vals  = {
                    'order_id':sale_obj,
                    'sale_call_id':prod.id,
                    'product_id':prod.product_id.id,
                    'product_uom_qty':prod.product_qty,
                    'order_code':prod.order_code,
                    'part_no':prod.part_no,
                    'make_no':prod.make_no,
                    #~ 'offer':prod.offer,
                    'purchase_id':prod.purchase_id.id,
                    'price_unit':prod.margin,
                    'item_no':prod.item_no,
                            }
            
            k = self.pool.get('sale.order.line').create(cr, uid, vals, context=context)
        obj.offer += 1   
        return sale_obj    
    
    def so_quote(self, cr, uid, ids, context=None):
        call_obj = self.browse(cr, uid, ids)
        sale_sr = self.pool.get('sale.order').search(cr, uid, [('request_id', '=', call_obj.id)], context=None)
        line = []
        for sale in call_obj.sale_line:
            if sale.select:
                line.append(sale)
        sale = self._so_create(cr, uid, call_obj, line, context=context)
        val = self.pool.get('purchase.order').search(cr, uid, [('requisition_id','=',call_obj.id)],context=context)
        #~ self.pool.get('purchase.order').write(cr, uid, val, {'po_sale_ids':[(6,0,[sale])]},context=context)
        return True 
        
        
    def po_confirm(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        pur_line = [pur.id for pur in obj.purchase_ids]
        pro_line = [prodline.purchase_id.id for prodline in obj.sale_line if prodline.select]
        rm_list = [val for val in  pur_line if val not in pro_line]
        self.pool.get('purchase.order').action_cancel(cr, uid, rm_list, context=context)
        pro1_line = [line_prod.purchase_line_id.id for line_prod in obj.sale_line if line_prod.select == False]
        self.pool.get('purchase.order.line').unlink(cr, uid, pro1_line, context=context)
        pro1 = [line_prod.purchase_id.id for line_prod in obj.sale_line if line_prod.select == True]
        for produ in pro1:        
            self.pool.get('purchase.order').draft(cr, uid, [produ], context=context)
            self.pool.get('purchase.order').load_currency(cr, uid, [produ], context=context)
            #~ self.pool.get('purchase.order').calculate_conversion(cr, uid, [produ], context=context)
            #~ self.pool.get('purchase.order').cal_confirm(cr, uid, [produ], context=context)
            #~ self.pool.get('purchase.order').gen_process(cr, uid, [produ], context=context)
        #~ l = []
        #~ for dup in pro_line:
            #~ if dup not in l:
                #~ l.append(dup)
        #~ self.pool.get('purchase.order').wkf_confirm_order(cr, uid, l, context=context)
        ######## Sale line update ########
        sa_line = []
        sa = [sal for sal in obj.sale_line if sal.select == False]
        for s in sa:
            k = self.pool.get('sale.order.line').search(cr, uid, [('sale_call_id', '=', s.id)], context=context)
            if k:
                sa_line.append(k[0])   
        self.pool.get('sale.order.line').unlink(cr, uid, sa_line, context=context)
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)
        
purchase_requisition_inherit()

class purchase_requisition_line_inherit(osv.osv):
    _inherit = 'purchase.requisition.line'
    _columns = {
             'item_no':fields.char('Item No'),
             'lead_line_id':fields.many2one('crm.lead.line', 'Lead Product'),
             'partner_ids':fields.many2many('res.partner', 'request_partner_rel', 'request_id', 'partner_id', 'Supplier'),
             'part_no': fields.char('Part No', size=64), 
             'make_no': fields.char('Make', size=64), 
               }
purchase_requisition_line_inherit()

class request_so_line(osv.osv):
    _name = 'request.so.line'
    _columns = {
             'item_no':fields.char('Item No'),
             'so_id': fields.many2one('purchase.requisition', 'Purchase requesting'),
             'select': fields.boolean('Select'),
             'purchase_id': fields.many2one('purchase.order', 'Purchase Quote', readonly=True),
             'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Line'),
             'partner_id': fields.many2one('res.partner', 'Supplier', readonly=True),
             'purchase_cost_history_id': fields.many2one('cost.history.line', 'Cost History'),
             'offer': fields.char('Offer', size=64, readonly=True),
             'product_id': fields.many2one('product.product', 'Product' ,readonly=True),
             'product_qty': fields.float('Quantity' ,readonly=True),
             'ot_unit_price': fields.float('Unit Price' ,readonly=True),
             'part_no':fields.char('Part No', size=64 ,readonly=True),   
             'make_no':fields.char('Make', size=64 ,readonly=True),
             'ot_total_price': fields.float('Total Price' ,readonly=True),
             'unit_price': fields.float('AED Unit Price' ,readonly=True),
             'total_price': fields.float('AED Total Price' ,readonly=True),
             'margin_id': fields.many2one('costing.margin', 'Margin % '),
             'margin': fields.float('Margin Price' ,readonly=True),
             'margin_price': fields.float('Customer Price' ,readonly=True), 
             'order_code':fields.char('Order Code', size=64), 
               }
    _order = 'product_id asc, partner_id asc'

request_so_line()
