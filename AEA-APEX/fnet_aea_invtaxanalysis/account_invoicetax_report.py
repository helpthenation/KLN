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

class account_invoicetax_report(osv.osv):
    _name = "account.invoicetax.report"
    _description = "Invoices  Statistics With Taxes"
    _auto = False
    _rec_name = 'date'

    def _compute_amounts_in_user_currency(self, cr, uid, ids, field_names, args, context=None):
        """Compute the amounts in the currency of the user
        """
        if context is None:
            context={}
        currency_obj = self.pool.get('res.currency')
        currency_rate_obj = self.pool.get('res.currency.rate')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        user_currency_id = user.company_id.currency_id.id
        currency_rate_id = currency_rate_obj.search(
            cr, uid, [
                ('rate', '=', 1),
                '|',
                    ('currency_id.company_id', '=', user.company_id.id),
                    ('currency_id.company_id', '=', False)
                ], limit=1, context=context)[0]
        base_currency_id = currency_rate_obj.browse(cr, uid, currency_rate_id, context=context).currency_id.id
        res = {}
        ctx = context.copy()
        for item in self.browse(cr, uid, ids, context=context):
            ctx['date'] = item.date
            price_total = currency_obj.compute(cr, uid, base_currency_id, user_currency_id, item.price_total, context=ctx)
            price_average = currency_obj.compute(cr, uid, base_currency_id, user_currency_id, item.price_average, context=ctx)
            residual = currency_obj.compute(cr, uid, base_currency_id, user_currency_id, item.residual, context=ctx)
            res[item.id] = {
                'user_currency_price_total': price_total,
                'user_currency_price_average': price_average,
                'user_currency_residual': residual,
            }
        return res
    #~ def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True):
        #~ print'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',domain
        #~ res = super(account_invoicetax_report, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby, lazy=lazy)
        #~ return res
    _columns = {
        'date': fields.date('Date', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_qty':fields.float('Product Quantity', readonly=True),
        'uom_name': fields.char('Reference Unit of Measure', size=128, readonly=True),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term', readonly=True),
        'period_id': fields.many2one('account.period', 'Force Period', domain=[('state','<>','done')], readonly=True),
        'fiscal_position': fields.many2one('account.fiscal.position', 'Fiscal Position', readonly=True),
        'currency_id': fields.many2one('res.currency', 'Currency', readonly=True),
        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'journal_id': fields.many2one('account.journal', 'Journal', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'commercial_partner_id': fields.many2one('res.partner', 'Partner Company', help="Commercial Entity"),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'user_id': fields.many2one('res.users', 'Salesperson', readonly=True),
        'price_total': fields.float('Total Without Tax', readonly=True),
        'user_currency_price_total': fields.function(_compute_amounts_in_user_currency, string="Total Without Tax", type='float', digits_compute=dp.get_precision('Account'), multi="_compute_amounts"),
        'price_average': fields.float('Average Price', readonly=True, group_operator="avg"),
        'user_currency_price_average': fields.function(_compute_amounts_in_user_currency, string="Average Price", type='float', digits_compute=dp.get_precision('Account'), multi="_compute_amounts"),
        'currency_rate': fields.float('Currency Rate', readonly=True),
        'nbr': fields.integer('# of Invoices', readonly=True),  # TDE FIXME master: rename into nbr_lines
        'type': fields.selection([
            ('out_invoice','Customer Invoice'),
            ('in_invoice','Supplier Invoice'),
            ('out_refund','Customer Refund'),
            ('in_refund','Supplier Refund'),
            ],'Type', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('proforma','Pro-forma'),
            ('proforma2','Pro-forma'),
            ('open','Open'),
            ('paid','Done'),
            ('cancel','Cancelled')
            ], 'Invoice Status', readonly=True),
        'date_due': fields.date('Due Date', readonly=True),
        'account_id': fields.many2one('account.account', 'Account',readonly=True),
        'account_line_id': fields.many2one('account.account', 'Account Line',readonly=True),
        'partner_bank_id': fields.many2one('res.partner.bank', 'Bank Account',readonly=True),
        'number': fields.char('Invoice Number',readonly=True),
        'residual': fields.float('Total Residual', readonly=True),
        'user_currency_residual': fields.function(_compute_amounts_in_user_currency, string="Total Residual", type='float', digits_compute=dp.get_precision('Account'), multi="_compute_amounts"),
        'country_id': fields.many2one('res.country', 'Country of the Partner Company'),
        'cgst':fields.float('CGST'),
        'sgst':fields.float('SGST'),
        'igst':fields.float('IGST'),
        'vat':fields.float('VAT'),
        'tax':fields.float('Total Tax Amount'),
        'dis_total':fields.float('Dis. Total Without Tax'),
        'months':fields.char('Months'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team'),
        'district_id': fields.many2one('res.country.district', string='Territory'),
        
        'discounts':fields.float('Discount'),
        'disc_price_unit':fields.float('Disc. Unit Price '),
        'gross_amount':fields.float('Gross Amount '),
        'product_discount':fields.float('Product Discount'),
    }
    _order = 'months asc'

    _depends = {
        'account.invoice': [
            'account_id', 'amount_total', 'commercial_partner_id', 'company_id','number',
            'currency_id', 'date_due', 'date_invoice', 'fiscal_position',
            'journal_id', 'partner_bank_id', 'partner_id', 'payment_term',
            'period_id', 'residual', 'state', 'type', 'user_id',
        ],
        'account.invoice.line': [
            'account_id', 'invoice_id', 'price_subtotal', 'product_id',
            'quantity', 'uos_id',
        ],
        'product.product': ['product_tmpl_id'],
        'product.template': ['categ_id'],
        'product.uom': ['category_id', 'factor', 'name', 'uom_type'],
        'res.currency.rate': ['currency_id', 'name'],
        'res.partner': ['country_id'],
    }

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id,sub.section_id as section_id,
                sub.payment_term, sub.period_id, sub.uom_name, sub.currency_id, sub.journal_id,sub.district_id as district_id,
                sub.fiscal_position, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,sub.number,
                sub.product_qty, sub.price_total / cr.rate as price_total, sub.price_average /cr.rate as price_average,
                cr.rate as currency_rate, sub.residual / cr.rate as residual, sub.commercial_partner_id as commercial_partner_id,
                sub.CGST as cgst,sub.SGST as sgst,sub.IGST as igst,sub.VAT as vat,sub.tax,sub.months,sub.dis_total, sub.discounts,
                sub.disc_price_unit as disc_price_unit,
                sub.gross_amount as gross_amount,
                sub.product_discount as product_discount

        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT min(ail.id) AS id,
                    ai.date_invoice AS date,
                    ail.product_id, ai.partner_id, ai.payment_term, ai.period_id,
                    u2.name AS uom_name,
                    ai.section_id as section_id,
                     ai.district_id as district_id,
                    ai.currency_id, ai.journal_id, ai.fiscal_position, ai.user_id, ai.company_id,
                    count(ail.*) AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id,ai.number,
                    EXTRACT(MONTH FROM ai.date_invoice) as months,
                    SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - disp.discount_price
                            ELSE disp.discount_price
                        END) AS dis_total,                    
                    (CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - gta.CGST
                            ELSE gta.CGST
                        END) AS cgst,
                    (CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - gta.SGST
                            ELSE gta.SGST
                        END) AS sgst,    
                     (CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - gta.IGST
                            ELSE gta.IGST
                        END) AS igst,              
                     (CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - gta.VAT
                            ELSE gta.VAT
                        END) AS vat,      
                     (CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN -(COALESCE(gta.CGST,0) + COALESCE(gta.SGST,0) + COALESCE(gta.IGST,0) + COALESCE(gta.VAT,0))
                            ELSE (COALESCE(gta.CGST,0) + COALESCE(gta.SGST,0) + COALESCE(gta.IGST,0) + COALESCE(gta.VAT,0))
                        END) AS tax,                           
                    SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN (- ail.quantity) / u.factor * u2.factor
                            ELSE ail.quantity / u.factor * u2.factor
                        END) AS product_qty,
                    SUM(CASE
                         WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                            THEN - ail.price_subtotal
                            ELSE ail.price_subtotal
                        END) AS price_total,
                    CASE
                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                        THEN SUM(- ail.price_subtotal)
                        ELSE SUM(ail.price_subtotal)
                    END / CASE
                           WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN CASE
                                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                                        THEN SUM((- ail.quantity) / u.factor * u2.factor)
                                        ELSE SUM(ail.quantity / u.factor * u2.factor)
                                    END
                               ELSE 1::numeric
                          END AS price_average,
                    CASE
                     WHEN ai.type::text = ANY (ARRAY['out_refund'::character varying::text, 'in_invoice'::character varying::text])
                        THEN - ai.residual
                        ELSE ai.residual
                    END / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id,
                    ail.discounts as discounts,
                    ail.disc_price_unit as disc_price_unit,
                    ail.gross_amount as gross_amount,
                    ail.product_discount as product_discount,
              
        """
        return select_str

    def _from(self):
        from_str = """
                FROM account_invoice_line ail
                JOIN account_invoice ai ON ai.id = ail.invoice_id
                JOIN res_partner partner ON ai.commercial_partner_id = partner.id
                LEFT JOIN product_product pr ON pr.id = ail.product_id
                left JOIN product_template pt ON pt.id = pr.product_tmpl_id
                LEFT JOIN product_uom u ON u.id = ail.uos_id
                LEFT JOIN product_uom u2 ON u2.id = pt.uom_id
                LEFT JOIN gst_tax_analysis gta ON gta.id=ail.id
                LEFT JOIN discounted_price disp ON disp.id=ail.id
        """
        return from_str

    def _group_by(self):
        group_by_str = """
                GROUP BY ail.id,ail.product_id, ai.date_invoice, ai.id,
                    ai.partner_id, ai.payment_term, ai.period_id, u2.name, u2.id, ai.currency_id, ai.journal_id,
                    ai.fiscal_position, ai.user_id, ai.company_id, ai.type, ai.state, pt.categ_id,
                    ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual,ai.section_id,
                    ai.amount_total, ai.commercial_partner_id, partner.country_id,gta.CGST,gta.SGST,gta.IGST,gta.VAT,disp.discount_price,ai.district_id,
                    ail.discounts ,
                    ail.disc_price_unit,
                    ail.gross_amount,
                    ail.product_discount

        """
        return group_by_str

    def init(self, cr):
        # self._table = account_invoice_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""DROP VIEW IF EXISTS gst_tax_analysis CASCADE  """)
        cr.execute("""DROP VIEW IF EXISTS discounted_price CASCADE  """)
        cr.execute("""CREATE or REPLACE VIEW gst_tax_analysis as (
                                      SELECT ail.id,
                                   MAX (CASE WHEN at.ref_code = '1' THEN 
                                       case when ai.disc_value > 0 and apl.days = 0  then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal) 
                                        end 
                                        END) AS CGST,
                                   MAX (CASE WHEN at.ref_code = '2'  THEN  
                                       case when ai.disc_value > 0  and apl.days = 0 then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal)        
                                       end
                                   END) AS SGST,
                                   MAX (CASE WHEN at.ref_code = '3' THEN 
                                       case when ai.disc_value > 0 and apl.days = 0 then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal)        
                                       end
                                    END) AS IGST,
                                MAX (CASE WHEN at.ref_code is Null THEN 
                                at.amount * ail.price_subtotal END ) AS VAT 
                            FROM account_invoice_line ail
                            JOIN account_invoice_line_tax atr on (atr.invoice_line_id = ail.id)
                            JOIN account_tax at ON (at.id = atr.tax_id)
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join res_company rc on (rc.id=ai.company_id)
                            join account_payment_term_line apl on apl.id = ai.payment_term
                            GROUP BY ail.id
        )""")
        cr.execute("""CREATE or REPLACE VIEW discounted_price as (     
                            SELECT ail.id,
                            MAX(CASE WHEN ai.date_invoice >= '2017-07-01' THEN 
                            case when ai.disc_value > 0 and apl.days = 0  then 
                            (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100)))
                            when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                            (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100)))
                            when apl.days > 0 then         
                            ( ail.price_subtotal) 
                            end 
                            WHEN ai.date_invoice < '2017-07-01' THEN ail.price_subtotal 
                            END) AS discount_price
                            FROM account_invoice_line ail                       
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join res_company rc on (rc.id=ai.company_id)
                            join account_payment_term_line apl on apl.id = ai.payment_term                            
                            GROUP BY ail.id        
        )""")   
        cr.execute("""CREATE or REPLACE VIEW %s as (
            WITH currency_rate (currency_id, rate, date_start, date_end) AS (
                SELECT r.currency_id, r.rate, r.name AS date_start,
                    (SELECT name FROM res_currency_rate r2
                     WHERE r2.name > r.name AND
                           r2.currency_id = r.currency_id
                     ORDER BY r2.name ASC
                     LIMIT 1) AS date_end
                FROM res_currency_rate r
            )
            %s
            FROM (
                %s %s %s
            ) AS sub
            JOIN currency_rate cr ON
                (cr.currency_id = sub.currency_id AND
                 cr.date_start <= COALESCE(sub.date, NOW()) AND
                 (cr.date_end IS NULL OR cr.date_end > COALESCE(sub.date, NOW())))
        )""" % (
                    self._table,
                    self._select(), self._sub_select(), self._from(), self._group_by()))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
