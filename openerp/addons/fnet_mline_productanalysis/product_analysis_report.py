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

class product_analysis_report(osv.osv):
    _name = "product.analysis.report"
    _description = "Product Price Analysis"
    _auto = False
    _rec_name = 'product_id'
    
    _columns = {
         'date':fields.date('Enquiry Date', readonly=True),
         'seq_no': fields.char('Enquiry Number', required=True, readonly=True),
         'rfq_seq': fields.char('RFQ Seq', required=True, readonly=True),
         'purchase_seq': fields.char('Purchase Seq', required=True, readonly=True),
         'partner_id':fields.many2one('res.partner', 'Customer', required=True),
         'user_id': fields.many2one('res.users', 'Salesperson', readonly=True),
         'supplier_id': fields.many2one('res.partner', 'Supplier', readonly=True),
         'product_id': fields.many2one('product.product', 'Product', readonly=True),
         'part_no':fields.char('Part No', size=64),
         'make_no':fields.char('Make', size=64),
         'aed_unit_price': fields.float('AED Unit Price' ,readonly=True),
         'total_price': fields.float('AED Total Price' ,readonly=True),
         'margin_id': fields.many2one('costing.margin', 'Margin % '),
         'margin': fields.float('Margin Price' ,readonly=True),
         'margin_price': fields.float('Customer Price' ,readonly=True), 
         'default_code' : fields.char('Internal Reference', readonly=True),
		 'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
		 'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
         'company_id': fields.many2one('res.company', 'Company', readonly=True),
         'date_approve':fields.date('Date Approved', readonly=True),
         'date_order':fields.datetime('Ordered Date', readonly=True),
         'date_planned':fields.date('Date Planned', readonly=True),        
         'purchase_price': fields.float('Purchase Unit Price', readonly=True),
         'product_qty': fields.float('Purchase Quantity', readonly=True),
         'purchase_total': fields.float('Purchase Total Price', readonly=True),
         
    }
    _order = 'date desc'
    
    
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'product_analysis_report')
        cr.execute("""
             create or replace view product_analysis_report as (
                WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                    SELECT r.currency_id, r.rate, r.name AS date_start,
                        (SELECT name FROM res_currency_rate r2
                        WHERE r2.name > r.name AND
                            r2.currency_id = r.currency_id
                         ORDER BY r2.name ASC
                         LIMIT 1) AS date_end
                    FROM res_currency_rate r
                )
                select
                    distinct on (pol.id)
                    min(pol.id) as id, 
                    cl.date,
                    cl.seq_no,
                    cl.partner_id,
                    cl.user_id,
                    pp.part_no,
                    pp.make_no,
                    pt.categ_id,
                    pp.default_code,
                    pp.company_id,
                    rsl.unit_price as aed_unit_price,
                    rsl.total_price,
                    rsl.margin_id,
                    rsl.margin,
                    rsl.margin_price,
                    po.currency_id,
                    po.partner_id as supplier_id,
                    po.date_approve,
                    po.date_order,
                    pol.product_id,
                    pol.date_planned,
                    pr.name as rfq_seq,
                    po.name as purchase_seq,
                    pol.price_unit as purchase_price,
                    pol.product_qty,
                    (pol.price_unit*pol.product_qty)::decimal(16,2) as purchase_total
                    
                    FROM 
					   purchase_order_line pol
					   LEFT JOIN purchase_order po ON (pol.order_id = po.id)
					   LEFT JOIN request_so_line rsl ON (po.id = rsl.purchase_id) 
					   LEFT JOIN purchase_requisition pr ON (po.requisition_id = pr.id)
					   LEFT JOIN purchase_requisition_line prl ON(pr.id = prl.requisition_id)
					   LEFT JOIN crm_lead cl ON(cl.id = pr.lead_seq_id)
					   LEFT JOIN product_product pp on pp.id = pol.product_id
					   LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
                       join currency_rate cr on (cr.currency_id = po.currency_id and
                       cr.date_start <= coalesce(po.date_order, now()) and
                       (cr.date_end is null or cr.date_end > coalesce(po.date_order, now())))
                group by
                    cl.seq_no,
                    cl.date,
                    cl.partner_id,
                    cl.user_id,
                    pp.part_no,
                    pp.make_no,
                    pt.categ_id,
                    pp.default_code,
                    pp.company_id,
                    rsl.unit_price,
                    rsl.total_price,
                    rsl.margin_id,
                    rsl.margin,
                    rsl.margin_price,
                    po.currency_id,
                    po.partner_id,
                    po.date_approve,
                    po.date_order,
                    pol.product_id,
                    pol.date_planned,
                    pr.name,
                    po.name,
                    pol.price_unit,
                    pol.product_qty,
                    pol.id

            )
   """)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

