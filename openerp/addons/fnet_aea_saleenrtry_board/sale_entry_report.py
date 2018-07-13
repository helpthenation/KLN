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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class sale_entry_report(osv.osv):
    _name = "sale.entry.report"
    _description = "Sale Entry Analysis"
    _auto = False
    _rec_name = 'date_from'

    _columns = {
        'date_from':fields.date('Date'),
        'sr_id': fields.many2one('res.users', 'Sales Representative'),
        'user_id': fields.many2one('res.users', 'Sales Manager'),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id',),
        'prod_categ_id':fields.many2one('product.category', 'Product Category',),
        'state': fields.selection([('draft', 'submit'),('waiting', 'Waiting For Approval'),('done', 'Submitted'),('cancel', 'Cancel')],'Status'),
        'company_id': fields.many2one('res.company', 'Company'),
        'district_id': fields.many2one('res.country.district', 'District'),
        'product_id':fields.many2one('product.product', 'Product'),
        'uom_id':fields.many2one('product.uom', 'Product UOM'),
        'current_stock':fields.float('Opening Stock'),
        'closing_stock':fields.float('Closing Stock'),
        'amount':fields.float('Quantity'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _order = 'date_from asc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'sale_entry_report')
        cr.execute("""create or replace view sale_entry_report as (
                            SELECT se.prod_categ_id,  se.date_from, se.sr_id, se.partner_id, se.district_id, ccs.user_id,
                            se.state,  sel.uom_id,  sel.amount, sel.current_stock, sel.product_id,  sel.company_id, 
                            case when coalesce(sel.amount,0.0) >= 0 then (coalesce(sel.current_stock,0.0) - coalesce(sel.amount,0.0))
                            when sel.amount is null then sel.current_stock end as closing_stock, sel.id
                            FROM sale_entry se
                            JOIN sale_entry_line sel On (se.id = sel.sale_entry_id)
                            left join sale_member_rel smr on (smr.member_id = se.sr_id)
                            left JOIN crm_case_section ccs On (ccs.id = smr.section_id)
                            GROUP BY 
                            sel.id,ccs.user_id, se.prod_categ_id, se.date_from,  se.sr_id,  se.partner_id,  se.district_id, 
                            se.state, sel.uom_id, sel.amount, sel.current_stock, sel.product_id, sel.company_id)""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
