
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



class product_template(osv.osv):
    _inherit = 'product.template'
   
    _columns = {
         'purchase_discount': fields.float('Purchase Discount Per Piece'),         
               }
               
    def create(self, cr, uid, vals, context=None):
        print ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(product_template, self).create(cr, uid, vals, context=context)
        related_vals = {}
        if vals.get('mrp_price'):
            related_vals['mrp_price'] = vals['mrp_price']
        if vals.get('purchase_discount'):
            related_vals['purchase_discount'] = vals['purchase_discount']                          
        if related_vals:
            prod = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', product_template_id)], context=context)
            prod_id = self.pool.get('product.product').browse(cr, uid, prod[0])
            self.pool.get('product.product').write(cr, uid, prod_id.id, related_vals, context=context)
        return product_template_id
        
    def write(self, cr, uid, ids, vals, context=None):
        bro = self.browse(cr, uid, ids)
        related_vals = {}
        if vals.get('mrp_price'):
            related_vals['mrp_price'] = vals['mrp_price']    
        if vals.get('purchase_discount'):
            related_vals['purchase_discount'] = vals['purchase_discount']            
        if related_vals:
            prod = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', bro.id)], context=context)
            prod_id = self.pool.get('product.product').browse(cr, uid, prod[0])
            self.pool.get('product.product').write(cr, uid, prod_id.id, related_vals, context=context)
        return super(product_template, self).write(cr, uid, ids, vals, context=context)
   
product_template()

class product_product(osv.osv):
    _inherit = 'product.product'
   
    _columns = {
       'purchase_discount': fields.float('Purchase Discount Per Piece'),
               }
   
product_product()
