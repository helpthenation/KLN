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

class aea_sale_report(osv.osv):
    _name = "aea.sale.report"
    _description = "Sales Report Statistics"
    _auto = False
    _rec_name = 'date'
    
    _columns = {
		'manager_id': fields.many2one('res.users', 'Sales Manager', required=True),
        'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'state': fields.selection([('draft', 'submit'),('progress', 'Progress'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company'),
        'scheme_id': fields.many2one('rd.scheme', 'Scheme ID',readonly=True),
        'scheme_entry_line':fields.one2many('scheme.entry.line', 'scheme_entry_id', 'Scheme Line',readonly=True),
    
    }
