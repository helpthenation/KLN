# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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
from datetime import datetime, timedelta
from openerp.tools.translate import _
import time

class target_product_wiz(osv.osv_memory):
    _name = 'target.product.wiz'
    _description = 'Target Product'
    _columns = {
        
        'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True), 
        'pjc_update_line':fields.one2many('pjc.update.line', 'pjc_up_id', 'PJC Product Line'),
        }

    def update_product(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        pjc_prod = self.pool.get('pjc.product.line')
        record_id = context.get('active_ids', [])
        pjc_prd = pjc_prod.search(cr, uid, [('prod_categ_id','=',obj.prod_categ_id.id),('pjc_prod_id','=',record_id[0])], context=context)
        if pjc_prd:
            raise osv.except_osv(_('Error!'), _('Already u entered this category!'))
        else:
            for line in obj.pjc_update_line:
                if line.quantity <> 0.00:
                    vals = {
                     'pjc_prod_id':record_id[0],
                     'prod_categ_id':obj.prod_categ_id.id,
                     'product_id':line.product_id.id,
                     'quantity':line.quantity
                    }
                    pjc_prod.create(cr, uid, vals, context=context)
        return True

    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, context=None):
        result = {}
        list_of_dict=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (prod_categ_id, cate.company_id.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"product_id":fid['prod']})
            result['value'] = {'pjc_update_line':list_of_dict}
        return result
       
target_product_wiz()

class pjc_update_line(osv.osv_memory):
    _name = 'pjc.update.line'
    
    _columns = {
        'pjc_up_id':fields.many2one('target.product.wiz','PJC Entry'),
        'product_id':fields.many2one('product.product', 'Product',required=True),
        'quantity':fields.float('Quantity'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
   
pjc_update_line()
