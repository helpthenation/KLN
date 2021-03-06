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


class product_wise_sales_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(product_wise_sales_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_categ_details': self._get_categ_details,
                'get_prod_details': self._get_prod_details,
                'get_tot_details': self._get_tot_details,
                'get_gr_details': self._get_gr_details,
                'get_com': self._get_com,
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
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
       
                 
        self.cr.execute(" select  distinct pc.name as categ_name ,pt.categ_id as categ"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN account_invoice_line_tax tlt ON (tlt.invoice_line_id = ail.id)"\
                        " JOIN account_tax at ON (at.id = tlt.tax_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " \
                        " GROUP BY pt.categ_id,pc.name " \
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list

    def _get_prod_details(self, data,va):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            
        self.cr.execute(" SELECT distinct pp.name_template as name,pp.default_code,sum(ail.quantity) as qty,sum(ail.quantity * ail.price_unit) as product_value,COALESCE(ail.mrp_price,0) as mrp"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " JOIN res_partner rp ON (rp.id = ai.partner_id)"\
                        " where ai.type = 'out_invoice'  "\
                        " and pt.type != 'service'"\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pc.id = '%s' "\
                        " group by pp.name_template ,ail.mrp_price,pp.default_code"\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0]),va))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
    
    def _get_tot_details(self, data, va):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []           
        self.cr.execute(" SELECT SUM((ail.quantity * ail.price_unit)) as total"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = '%s' "\
                        " and pt.type != 'service'"\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pc.id = '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0]),va))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list 
      
    def _get_gr_details(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []           
        self.cr.execute(" SELECT SUM((ail.quantity * ail.price_unit)) as total"\
                        " FROM account_invoice ai "\
                        " JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)"\
                        " JOIN product_product pp ON (pp.id = ail.product_id)"\
                        " JOIN product_template pt ON (pt.id = pp.product_tmpl_id)"\
                        " JOIN product_category pc ON (pc.id = pt.categ_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = '%s' "\
                        " and pt.type != 'service'"\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " ORDER BY 1 "% (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list        
        
    def _get_com(self,val):
        na = self.pool.get('res.company').browse(self.cr, self.uid, val)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            return na1
        else:
            na1 = 'Apex Agencies'
            return na1         

class wrapped_product_wise_sales_summary_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_product_wise_sales'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_product_wise_sales'
    _wrapped_report_class = product_wise_sales_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
