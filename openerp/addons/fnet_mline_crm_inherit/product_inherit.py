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

class product_template_inherit(osv.osv):
    _inherit = 'product.template'
    _columns = {

             'part_no': fields.char('MFG Part No', size=64, select=True),
             'make_no': fields.char('Make', size=64, select=True),
             'cust_line':fields.one2many('cutomer.product.line', 'product_cust_id', 'Customer'),
               }
               
    #~ _sql_constraints = [
        #~ ('default_code', 'unique (default_code)', 'The Internal Reference Number must be unique within an application!')
    #~ ]
               
    _defaults = {
           'list_price': 0.00, 
           'type':'product',
           'sale_delay':0.0,
           'categ_id':False,
            }

    def onchange_type(self, cr, uid, ids, type):
        res = super(product_template_inherit, self).onchange_type(cr, uid, ids, type)
        if type in ('consu', 'service'):
            res = {'value': {'valuation': 'manual_periodic'}}
        elif type == 'product':
            res = {'value': {'valuation': 'real_time'}}    
        return res  
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(product_template_inherit, self).create(cr, uid, vals, context=context)
        related_vals = {}
        if vals.get('part_no'):
            related_vals['part_no'] = vals['part_no']
        if vals.get('make_no'):
            related_vals['make_no'] = vals['make_no']
        if related_vals:
            prod = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', product_template_id)], context=context)
            prod_id = self.pool.get('product.product').browse(cr, uid, prod[0])
            self.pool.get('product.product').write(cr, uid, prod_id.id, related_vals, context=context)
        return product_template_id

    def write(self, cr, uid, ids, vals, context=None):
        bro = self.browse(cr, uid, ids)
        related_vals = {}
        if vals.get('part_no'):
            related_vals['part_no'] = vals['part_no']
        if vals.get('make_no'):
            related_vals['make_no'] = vals['make_no']
        if related_vals:
            prod = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', bro.id)], context=context)
            prod_id = self.pool.get('product.product').browse(cr, uid, prod[0])
            self.pool.get('product.product').write(cr, uid, prod_id.id, related_vals, context=context)
        return super(product_template_inherit, self).write(cr, uid, ids, vals, context=context)

product_template_inherit()

class cutomer_product_line(osv.osv):
	_name = 'cutomer.product.line'
	_rec_name = 'reference'
	_columns = {
	      'product_cust_id':fields.many2one('product.template', 'product'),
	      'partner_id':fields.many2one('res.partner', 'Customer'),
	      'reference':fields.char('Reference', size=64),
	      }
cutomer_product_line()

class product_product_inh(osv.osv):
    _inherit = 'product.product'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id    
    _columns = {

            'part_no': fields.char('MFG Part No', size=64, select=True),
            'make_no': fields.char('Make', size=64, select=True),
            'company_id': fields.many2one('res.company', 'Company'),
            }
    _sql_constraints = [
        ('default_code', 'unique (default_code,company_id)', 'The Internal Reference Number must be unique within an application!')
    ]
    _defaults={
       'company_id': _get_default_company,
    }
    
    def onchange_type(self, cr, uid, ids, type):
        res = super(product_product_inh, self).onchange_type(cr, uid, ids, type)
        if type in ('consu', 'service'):
            res = {'value': {'valuation': 'manual_periodic'}}
        elif type == 'product':
            res = {'value': {'valuation': 'real_time'}}    
        return res  
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_product_id = super(product_product_inh, self).create(cr, uid, vals, context=context)
        related_vals = {}
        if vals.get('part_no'):
            related_vals['part_no'] = vals['part_no']
        if vals.get('make_no'):
            related_vals['make_no'] = vals['make_no']
        if related_vals:
            test = self.pool.get('product.product').browse(cr, uid, product_product_id)
            prod = self.pool.get('product.template').search(cr, uid, [('id', '=', test.product_tmpl_id.id)], context=context)
            prod_id = self.pool.get('product.template').browse(cr, uid, prod[0])
            self.pool.get('product.template').write(cr, uid, prod_id.id, related_vals, context=context)
        return product_product_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_product_inh, self).write(cr, uid, ids, vals, context=context)
        bro = self.browse(cr, uid, ids)
        get = []
        related_vals = {}
        if vals.get('part_no'):
            related_vals['part_no'] = vals['part_no']
        if vals.get('make_no'):
            related_vals['make_no'] = vals['make_no']
        if related_vals:
            test = self.browse(cr, uid, bro.id)
            prod = self.pool.get('product.template').search(cr, uid, [('id', '=', test.product_tmpl_id.id)], context=context)
            prod_id = self.pool.get('product.template').browse(cr, uid, prod[0])
            #~ print prod_id.id, "GGGGGGGGGGGGGGGGGGGGG"
            #~ get.append(prod_id.id)
            #~ vals.update(related_vals)
        #~ print get
        #~ self.pool.get('product.template').write(cr, uid, get[0], related_vals, context=context)
        #~ return super(product_product_inh, self).write(cr, uid, ids, vals, context=context)
        #~ return self.pool.get('product.template').write(cr, uid, get[0], related_vals, context=context)
        return res
product_product_inh()
