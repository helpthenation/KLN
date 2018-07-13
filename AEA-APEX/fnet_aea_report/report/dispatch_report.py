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
from datetime import datetime, timedelta
import time

class dispatch_report(osv.osv):
    _name = "dispatch.report"
    _description = "Dispatch Statistics"
    _auto = False

    _columns = {
        'date': fields.date('Date Order', readonly=True),  # TDE FIXME master: rename into date_order
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'tpt_id': fields.many2one('res.partner', 'TPT Co Name'),
        'product_id': fields.many2one('product.product', 'Product'),
        'weight': fields.float('Weight'),
        'case': fields.float('No Of Case'),
        'method_type': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Type', required=True),
        
    }
    _order = 'date asc'

   
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'dispatch_report')
        cr.execute("""CREATE or REPLACE VIEW dispatch_report as (
            SELECT
                 ail.id as id,
                 ai.date_invoice as date,
                 ai.partner_id as partner_id,
                 ai.tpt_name as tpt_id,
                 SUM(ail.quantity * pt.weight) as weight,  
                 ceiling(ail.quantity / pt.case_qty) as case,
                 ai.del_method as method_type,
                 ail.product_id as product_id
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_uom pu ON (pu.id = ail.uos_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE ai.dispatch is False and pt.type != 'service' and ai.state = 'open'
            GROUP BY ail.id,ai.date_invoice,ai.partner_id,ai.tpt_name,ai.del_method,ail.product_id,pt.case_qty
            )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
