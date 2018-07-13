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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from datetime import datetime
class make_multiple_po(osv.osv_memory):
    _name = "sale.make.po"
    _description = "Make Multiple PO From Confirmed Sale"
    _columns={
        'supplier':fields.many2one('res.partner','Choose a Supplier'),
    }
    
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_ids', False)
        for rec in record_id:
            order = self.pool.get('sale.order').browse(cr, uid, rec, context=context)
            if order.state == 'progress' or order.state=='manual':
                return False  
            else:
                raise osv.except_osv(_('Warning!'), _('You cannot create Purchase order when sales order is not confirmed.'))


    def make_po(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids)
        record_id = context and context.get('active_ids', False)
        print tuple(record_id),context
        order_obj = self.pool.get('sale.order')
        cr.execute(''' select sol.product_id, sum(sol.product_uom_qty), 
                       pt.part_no, pt.make_no, pt.uom_id, pt.id
                       from sale_order so join sale_order_line sol on (sol.order_id=so.id) 
                       join product_product pp on (pp.id=sol.product_id) 
                       join product_template pt on (pt.id=pp.product_tmpl_id) 
                       where so.id in %s group by sol.product_id, 
                       pt.part_no, pt.make_no, pt.uom_id,pt.id  ''', (tuple(record_id),))
                       
        product_ids = cr.fetchall()
        vals= {
            'origin': '/',
            'date_order': datetime.now(),
            'partner_id': obj.supplier.id,
            'pricelist_id': obj.supplier.property_product_pricelist_purchase.id,
            'currency_id': obj.supplier.property_product_pricelist_purchase.currency_id.id,
            'location_id': 20,
            'company_id': obj.supplier.company_id.id,
            'fiscal_position': obj.supplier.property_account_position.id,
            'picking_type_id': 6,
            'po_sale_ids':[(6,0,record_id)]
        }        
        purchase_id = self.pool.get('purchase.order').create(cr, uid, vals, context=context)
        for rec in product_ids:
            product_rec=self.pool.get('product.template').browse(cr,uid,rec[5])
            val = {
                   'order_id':purchase_id,
                   'product_id':rec[0],
                   'name':product_rec.description,
                   'product_uom':rec[4],
                   'product_qty':rec[1],
                   'part_no':rec[2],
                   'make_no':rec[3],
                   'price_unit':0.000,
                   'date_planned':datetime.now(),
                   }        
            pur_line = self.pool.get('purchase.order.line').create(cr, uid,val,context=context)
        for id1 in record_id:
            for rec in order_obj.browse(cr,uid,id1):
                for val in rec.order_line:
                        res=self.pool.get('sale.order.line').write(cr, uid, val.id, {'purchase_id':purchase_id}, context=context)  
        pur_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'purchase', 'purchase_order_form')
        pur_rec_id = pur_rec and pur_rec[1] or False,                        
        return {
                    'name': _('Purchase Order'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': [pur_rec_id],
                    'res_model': 'purchase.order',
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': purchase_id or False,
                }

        
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
