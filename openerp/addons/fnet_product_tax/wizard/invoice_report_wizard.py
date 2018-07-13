# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-TODAY Serpent Consulting Services Pvt. Ltd.
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
from openerp.osv import osv,fields
from openerp.tools.translate import _
from lxml import etree
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
class product_tax_config(osv.osv_memory):
    _name = "product.tax.config"
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id  
          
    _columns={        
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'supplier_tax_ids':fields.many2many('account.tax','product_supplier_taxes_relations','prod','tax',string='Supplier Taxes'),       
        'customer_tax_ids' : fields.many2many('account.tax', 'product_customer_taxes_relations','prod','tax',string='Customer Taxes'),
        'company_id':fields.many2one('res.company','Company')
    }
    _defaults = {
        'company_id': _get_default_company,
        }    

    def update(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute("select id from product_template where categ_id = %d  and company_id = %d and type='product'"%(obj.prod_categ_id.id,obj.company_id.id))
        product_list = [i for i in cr.dictfetchall()]
        print'product_list',product_list
        for i in product_list:
           cr.execute("delete from product_supplier_taxes_rel where prod_id =%d"%(i['id']))
           cr.execute("delete from product_taxes_rel where prod_id =%d"%(i['id']))
           for j in obj.supplier_tax_ids.ids:
               #~ print'JJJJJJJJJJJJJJJJJJJJJJJJJJJ',j
               cr.execute('insert into product_supplier_taxes_rel (prod_id,tax_id) values(%s,%s)',(i['id'],j))
           for k in obj.customer_tax_ids.ids:
               #~ print'KKKKKKKKKKKKKKKKKKKKKKK',k
               cr.execute('insert into product_taxes_rel (prod_id,tax_id) values(%s,%s)',(i['id'],k))
                    
                
                
            
        
