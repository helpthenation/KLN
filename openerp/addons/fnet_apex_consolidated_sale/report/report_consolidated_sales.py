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


class consolidated_sales_apex(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(consolidated_sales_apex, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_invoice_details_ap':self._get_invoice_details_ap,
                'get_invoice_details_tl':self._get_invoice_details_tl,
                'get_invoice_details_odb':self._get_invoice_details_odb,
                'get_invoice_details_ods':self._get_invoice_details_ods,
                'get_invoice_details_total':self._get_invoice_details_total,
                'get_round_off_ap':self._get_round_off_ap,
                'get_round_off_tl':self._get_round_off_tl,
                'get_round_off_odb':self._get_round_off_odb,
                'get_round_off_ods':self._get_round_off_ods,
                'get_round_off_total':self._get_round_off_total,
                'get_invoice_product':self._get_invoice_product,
                'get_invoice_products_ap':self._get_invoice_products_ap,
                'get_invoice_products_tl':self._get_invoice_products_tl,
                'get_invoice_products_odb':self._get_invoice_products_odb,
                'get_invoice_products_ods':self._get_invoice_products_ods,
                'get_invoice_products_total':self._get_invoice_products_total,
                
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
        
    def _get_invoice_details_ap(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []       
        self.cr.execute(" select sum(ai.amount_total) as invoice, ROUND(sum(ail.price_unit* ail.quantity)::numeric,2) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id=3 "\
                        "and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount
            val['product_value']=amount     
            lis.append(val)
            return lis      
        else:
            return line_list    
            
    def _get_invoice_details_ods(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []     
        self.cr.execute(" select sum(ai.amount_total) as invoice, ROUND(sum(ail.price_unit* ail.quantity)::numeric,2) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id=5 "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount
            val['product_value']=amount     
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_invoice_details_odb(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(" select sum(ai.amount_total) as invoice, ROUND(sum(ail.price_unit* ail.quantity)::numeric,2) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id=4 "\
                        "and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount
            val['product_value']=amount     
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_invoice_details_tl(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(" select sum(ai.amount_total) as invoice, ROUND(sum(ail.price_unit* ail.quantity)::numeric,2) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id=6 "\
                        "and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount
            val['product_value']=amount     
            lis.append(val)
            return lis      
        else:
            return line_list            
            
    def _get_invoice_details_total(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(" select sum(ai.amount_total) as invoice, ROUND(sum(ail.price_unit* ail.quantity)::numeric,2) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id in (3,4,5,6) "\
                        "and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount
            val['product_value']=amount     
            lis.append(val)
            return lis      
        else:
            return line_list                                    
                   
            
    def _get_round_off_ap(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []            
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and pt.type='service' "\
                        " and ai.company_id = 3 "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'ROIUNDDDDDDDDDDDDD'
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount    
            lis.append(val)
            return lis      
        else:
            return line_list   
            
    def _get_round_off_odb(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []            
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and pt.type='service' "\
                        " and ai.company_id = 4 "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'ROIUNDDDDDDDDDDDDD'
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount    
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_round_off_ods(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []            
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and pt.type='service' "\
                        " and ai.company_id = 5 "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'ROIUNDDDDDDDDDDDDD'
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount    
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_round_off_tl(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []            
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and pt.type='service' "\
                        " and ai.company_id = 6 "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'ROIUNDDDDDDDDDDDDD'
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount    
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_round_off_total(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []            
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and pt.type='service' "\
                        " and ai.company_id in (3,4,5,6) "\
                        " and ai.date_invoice>= '%s' "\
                        " and ai.date_invoice<= '%s' "% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list,'ROIUNDDDDDDDDDDDDD'
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['invoice']=amount    
            lis.append(val)
            return lis      
        else:
            return line_list                                    
            
    def _get_invoice_product(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []  
                      
        self.cr.execute(" select distinct pp.default_code, pt.name as product"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id in (3,4,5,6) "\
                        " and pt.type != 'service' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        "group by pp.default_code,ail.product_id, pt.name" % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        dic_cus={}
        for cus in line_list:
            dic_cus[cus['product']]=[]
        for cus in line_list:
            dic_cus[cus['product']].append([cus['default_code'],cus['product']])
        return dic_cus                              
        
    def _get_invoice_products_total(self,data,product):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []        
        self.cr.execute(" select ROUND(sum(ail.price_unit* ail.quantity)::numeric,2)  as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id in (3,4,5,6) "\
                        " and pp.default_code='%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pt.type != 'service' "% (str(product),str(from_date[0]),str(to_date[0])))

        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['product_value']=amount   
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_invoice_products_ap(self,data,product):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []        
        self.cr.execute(" select ROUND(sum(ail.price_unit* ail.quantity)::numeric,2)  as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = 3 "\
                        " and pp.default_code='%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pt.type != 'service' "% (str(product),str(from_date[0]),str(to_date[0])))

        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['product_value']=amount   
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_invoice_products_odb(self,data,product):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []        
        self.cr.execute(" select ROUND(sum(ail.price_unit* ail.quantity)::numeric,2)  as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = 4 "\
                        " and pp.default_code='%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pt.type != 'service' "% (str(product),str(from_date[0]),str(to_date[0])))

        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['product_value']=amount   
            lis.append(val)
            return lis      
        else:
            return line_list
            
    def _get_invoice_products_ods(self,data,product):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []        
        self.cr.execute(" select ROUND(sum(ail.price_unit* ail.quantity)::numeric,2)  as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = 5 "\
                        " and pp.default_code='%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pt.type != 'service' "% (str(product),str(from_date[0]),str(to_date[0])))

        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['product_value']=amount   
            lis.append(val)
            return lis      
        else:
            return line_list  
            
    def _get_invoice_products_tl(self,data,product):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []        
        self.cr.execute(" select ROUND(sum(ail.price_unit* ail.quantity)::numeric,2)  as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " and ai.company_id = 6 "\
                        " and pp.default_code='%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        " and pt.type != 'service' "% (str(product),str(from_date[0]),str(to_date[0])))

        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['product_value']=amount   
            lis.append(val)
            return lis      
        else:
            return line_list                                                                  
            
       
        
class wrapped_consolidated_sales_report(osv.AbstractModel):
    _name = 'report.fnet_apex_consolidated_sale.report_consolidated_sales_apex'
    _inherit = 'report.abstract_report'
    _template = 'fnet_apex_consolidated_sale.report_consolidated_sales_apex'
    _wrapped_report_class = consolidated_sales_apex

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
