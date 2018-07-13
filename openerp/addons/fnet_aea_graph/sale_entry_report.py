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

from openerp import tools
from openerp.osv import fields, osv

class sale_entry_report(osv.osv):
    _name = "sale.entry.report"
    _description = "Sales Entry Statistics"
    _auto = False
    _rec_name = 'date_from'

    _columns = {
		'date_from':fields.date('Date From'),
		'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
		'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
		'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
		'state': fields.selection([('draft', 'submit'),('waiting', 'Waiting For Approval'),('done', 'Submitted'),('cancel', 'Cancel')],'Status', readonly=True, track_visibility='always'),
		'company_id': fields.many2one('res.company', 'Company'),
		'sale_entry_line':fields.one2many('sale.entry.line', 'sale_entry_id', 'Sale Entry Line'),
		'district_id': fields.many2one('res.country.district', 'District'),
		'product_id':fields.many2one('product.product', 'Product', required=True, readonly=True),
		'uom_id':fields.many2one('product.uom', 'Product UOM', required=True, readonly=True),
		'target_qty':fields.float('Target Quantity',readonly=True),
		'current_stock':fields.float('Current Stock',readonly=True),
		'amount':fields.float('Achieved Quantity'),
    }
    _order = 'date_from desc'



    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT 
              se.id as id,
			  se.prod_categ_id, 
			  se.date_from, 
			  se.company_id, 
			  se.sr_id, 
			  se.partner_id, 
			  se.district_id, 
			  se.state, 
			  sel.product_id, 
			  sel.uom_id,
			  coalesce(sel.current_stock, 0) as  current_stock,
			  coalesce(sel.target_qty, 0) as target_qty ,
			  coalesce(sel.amount,0)  as amount 
			FROM 
			  sale_entry as se  
			  JOIN sale_entry_line as sel On (sel.sale_entry_id = se.id)
            )""" % (self._table))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
