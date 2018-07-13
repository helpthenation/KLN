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
from openerp import _
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta
import time
from openerp.exceptions import Warning


class job_costing_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(job_costing_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_po_data':self._get_po_data,
                'get_sale_data':self._get_sale_data,
                'get_expense_data':self._get_expense_data,
                'get_po_total':self._get_po_total,
                'get_basic_data': self._get_basic_data,
                'get_purchase_data':self._get_purchase_data,
                'get_supplier_data':self._get_supplier_data,
                'get_expense_total':self._get_expense_total,
                
        })

    def _get_po_data(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select COALESCE(ail.quantity,0) as quantity, COALESCE(ail.price_unit,0.0) as unit_price, pt.name as product,ail.price_subtotal as purchase_subtotal,COALESCE(ai.amount_total,0.0) as po_total"\
                        " from sale_order so "\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "join purchase_invoice_rel pir on (pir.purchase_id = po.id)"\
                        "join account_invoice ai on (ai.id = pir.invoice_id)"\
                        "left join account_invoice_line ail on (ail.invoice_id = ai.id)"\
                        "left join product_product pp on (pp.id = ail.product_id)"\
                        "left join product_template pt on (pt.id = pp.product_tmpl_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))            
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            val['quantity']=0   
            val['unit_price']=0   
            val['product']=''
            val['purchase_subtotal']=0   
            val['po_total']=0   
            lis.append(val)
            return lis  
        else:
            return line_list
        
    def _get_sale_data(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        print job_id
        self.cr.execute(" select COALESCE(ail.quantity,0) as quantity, COALESCE(ail.price_unit,0.0) as unit_price, pt.name as product,ail.price_subtotal as sale_subtotal, COALESCE(ai.amount_total,0.0) as sale_total"\
                        " from sale_order so "\
                        "left join sale_order_invoice_rel soil on (soil.order_id = so.id)"\
                        "left join account_invoice ai on (ai.id = soil.invoice_id)"\
                        "left join account_invoice_line ail on (ail.invoice_id = ai.id)"\
                        "left join product_product pp on (pp.id = ail.product_id)"\
                        "left join product_template pt on (pt.id = pp.product_tmpl_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))            
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'****************'
        if line_list==[]:
            lis=[]
            val={}
            val['quantity']=0   
            val['unit_price']=0   
            val['product']=''
            val['sale_subtotal']=0   
            val['sale_total']=0   
            lis.append(val)
            return lis  
        else:
            return line_list
                
        
    def _get_expense_data(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select distinct aml.id,aml.account_id as account,aml.debit as debit,aml.name as description, po.exchange_rate, po.exchange_rate * aml.debit as total"\
                        " from sale_order so "\
                        "join sale_order_invoice_rel soil on (soil.order_id = so.id)"\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join account_invoice ai on (ai.id = soil.invoice_id) "\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "left join account_move am on (ai.move_id = am.id)"\
                        "join account_move_line aml on (aml.job_id = so.id)"\
                        "join account_account aa on (aa.id = aml.account_id)"\
                        "join account_account_type aat on (aat.id = aa.user_type)"\
                        "where ai.state = 'paid' and aat.code = 'expense'"\
                        " and so.job_id = '%s' " % (job_id[0][1]))            
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_expense_total(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select distinct aml.id, COALESCE(aml.debit,0.0) as debit, COALESCE(po.exchange_rate * aml.debit,0.0) as total"\
                        " from sale_order so "\
                        "join sale_order_invoice_rel soil on (soil.order_id = so.id)"\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join account_invoice ai on (ai.id = soil.invoice_id) "\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "left join account_move am on (ai.move_id = am.id)"\
                        "join account_move_line aml on (aml.job_id = so.id)"\
                        "join account_account aa on (aa.id = aml.account_id)"\
                        "join account_account_type aat on (aat.id = aa.user_type)"\
                        "where ai.state = 'paid' and aat.code = 'expense'"\
                        " and so.job_id = '%s'" % (job_id[0][1]))            
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[0,0]
            return lis  
        else:        
            debit=0
            total=0
            val=[]
            for rec in line_list:
                debit=debit + rec['debit']
                total=total + rec['total']
            val.append(debit)
            val.append(total)
            return val
                    
        
    def _get_po_total(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select  COALESCE(sum(ai.amount_total),0.0) as po_total, COALESCE(sum(ail.price_unit),0.0)  as unit_price"\
                        " from sale_order so "\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "join purchase_invoice_rel pir on (pir.purchase_id = po.id)"\
                        "join account_invoice ai on (ai.id = pir.invoice_id)"\
                        "left join account_invoice_line ail on (ail.invoice_id = ai.id)"\
                        "left join product_product pp on (pp.id = ail.product_id)"\
                        "left join product_template pt on (pt.id = pp.product_tmpl_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))            
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            val['po_total']=0   
            val['unit_price']=0     
            lis.append(val)
            return lis  
        else:
            return line_list            
            
    def _get_basic_data(self, data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
                
        self.cr.execute(" select  so.job_id as job_id,rp.name as client_name"\
                        " from sale_order so "\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "left join res_partner rp on (rp.id=so.partner_id) "\
                        "left join res_partner rpp on (rpp.id=po.partner_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            val['job_id']='' 
            val['client_name']=''    
            lis.append(val)
            return lis  
        else:
            return line_list
        
    def _get_purchase_data(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select  po.id as po_id ,po.name as po_name"\
                        " from sale_order so "\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "join res_partner rp on (rp.id=so.partner_id) "\
                        "join res_partner rpp on (rpp.id=po.partner_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))
        line_list = [i for i in self.cr.dictfetchall()]
        val=[]
        if line_list==[]:
            return False
        else:
            for rec in line_list:
                val.append(rec['po_name'])
            return ','.join(val) 
        
    def _get_supplier_data(self,data):
        job_id = 'job_id' in data['form'] and [data['form']['job_id']] or []
        self.cr.execute(" select  rpp.id as rpp_id ,rpp.name as supplier_name"\
                        " from sale_order so "\
                        "join sale_po_rel spr on (spr.sale_id = so.id)"\
                        "join purchase_order po on (po.id = spr.po_id)"\
                        "join res_partner rp on (rp.id=so.partner_id) "\
                        "join res_partner rpp on (rpp.id=po.partner_id)"\
                        " where so.job_id = '%s' " % (job_id[0][1]))
        line_list = [i for i in self.cr.dictfetchall()]
        val=[]
        if line_list==[]:
            return False
        else:
            for rec in line_list:
                val.append(rec['supplier_name'])
            return ','.join(val)   
        
        
class wrapped_job_costing_report(osv.AbstractModel):
    _name = 'report.fnet_mline_sale_report.report_job_costing'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_sale_report.report_job_costing'
    _wrapped_report_class = job_costing_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
