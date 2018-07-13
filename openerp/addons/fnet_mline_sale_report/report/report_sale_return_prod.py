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


class sale_product_report1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_product_report1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_categ_details': self._get_categ_details,
                'get_prod_details': self._get_prod_details,
                'get_tot_details': self._get_tot_details,
                'get_gr_details': self._get_gr_details,
                'get_dis': self._get_dis,
                'get_grdis': self._get_grdis,
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
        return val
        
    def _get_categ_details(self, data):
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
        self.cr.execute(" select  pt.categ_id as categ,pc.name as categ_name"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN account_invoice_line_tax tlt ON (tlt.invoice_line_id = ail.id)"\
                        " JOIN account_tax at ON (at.id = tlt.tax_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " \
                        " GROUP BY pt.categ_id,pc.name " \
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list

    def _get_prod_details(self, data,va):
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
        self.cr.execute(" SELECT pc.name as categ_name,pp.name_template as name,ail.quantity as qty,ail.price_unit as price,(ail.quantity * ail.price_unit) as tot,((ail.quantity * ail.price_unit) * at.amount) + (ail.quantity * ail.price_unit) as vat"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN account_invoice_line_tax tlt ON (tlt.invoice_line_id = ail.id)"\
                        " JOIN account_tax at ON (at.id = tlt.tax_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pc.id = '%s' "\
                        " GROUP BY pc.name,pp.name_template,ail.quantity,ail.price_unit,at.amount " 
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0]),va))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
    
    def _get_tot_details(self, data, va):
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
        self.cr.execute(" SELECT SUM(ail.quantity) as qty,SUM(ail.price_unit) as price,SUM((ail.quantity * ail.price_unit)) as tot,SUM(((ail.quantity * ail.price_unit) * at.amount) + (ail.quantity * ail.price_unit)) as vat"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN account_invoice_line_tax tlt ON (tlt.invoice_line_id = ail.id)"\
                        " JOIN account_tax at ON (at.id = tlt.tax_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pc.id = '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0]),va))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list 
        
    def _get_gr_details(self, data):
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
        self.cr.execute(" SELECT SUM(ail.quantity) as qty,SUM(ail.price_unit) as price,SUM((ail.quantity * ail.price_unit)) as tot,SUM(((ail.quantity * ail.price_unit) * at.amount) + (ail.quantity * ail.price_unit)) as vat"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN account_invoice_line_tax tlt ON (tlt.invoice_line_id = ail.id)"\
                        " JOIN account_tax at ON (at.id = tlt.tax_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list 
        
    def _get_dis(self, data,va):
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
        self.cr.execute(" SELECT SUM(ail.price_unit) as price"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and pt.type = 'service' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pc.id = '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0]),va))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list[0]['price'] 
        
    def _get_grdis(self, data):
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
        self.cr.execute(" SELECT SUM(ail.price_unit) as price"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " where ai.type = 'out_refund' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.company_id = '%s' "\
                        " and pt.type = 'service' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list[0]['price'] 

class wrapped_sale_product_report1(osv.AbstractModel):
    _name = 'report.fnet_mline_sale_report.report_sale_product1'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_sale_report.report_sale_product1'
    _wrapped_report_class = sale_product_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
