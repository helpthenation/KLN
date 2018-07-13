#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta
import time


class sale_return_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_return_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_invoice_details': self._get_invoice_details,
                'get_invoice_line_details': self._get_invoice_line_details,
                'get_prod_value': self._get_prod_value,
                'get_date': self._get_date,
        })

    def _get_date(self, data):
        val = []
        res = {}
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        now = time.strftime("%Y-%m-%d")
        res['from_date']=from_date
        res['to_date']=to_date
        res['now']=now
        val.append(res)
        print val, "DDDDDDDd"
        return val
        
    def _get_invoice_details(self, data):
        where_sql = []
        com = 'company_id' in data['form'] and [data['form']['company_id']] or []
        partner = 'partner_ids' in data['form'] and [data['form']['partner_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if data['form']['partner_ids']:
            if len(data['form']['partner_ids'])== 1:
                add = [0]
                data = data['form']['partner_ids']
                where_sql.append("ai.partner_id in %s" % (str(tuple(data+add))))
            else:
                where_sql.append("ai.partner_id in %s" % (str(tuple(data['form']['partner_ids']))))
        
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        self.cr.execute(" select  ai.id,ai.date_invoice, rp.name, ai.number, ai.amount_total, ai.amount_untaxed"\
                        " from account_invoice ai "\
                        " join res_partner rp on (rp.id = ai.partner_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " % (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list

    def _get_invoice_line_details(self, data):
        self.cr.execute(" select pp.name_template as prod, ail.quantity as qty, ail.price_unit as price, ail.quantity* ail.price_unit as value, (ail.quantity * ail.price_unit)- ail.price_subtotal as dis, ail.price_subtotal net"\
                        " FROM account_invoice_line ail "\
                        " JOIN product_product pp ON (pp.id = ail.product_id) "\
                        " where ail.invoice_id = '%s'" % (data))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
        
    def _get_prod_value(self, data):
        self.cr.execute(" select sum(ail.price_unit * ail.quantity) as prod_price, ai.amount_untaxed as tax_val"\
                        " from account_invoice ai "\
                        " JOIN account_invoice_line ail on (ail.invoice_id = ai.id) "\
                        " WHERE ai.id = '%s'"\
                        " GROUP BY ai.amount_untaxed" % (data))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
        
class wrapped_sale_return_summary(osv.AbstractModel):
    _name = 'report.fnet_mline_sale_report.report_sale_return'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_sale_report.report_sale_return'
    _wrapped_report_class = sale_return_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
