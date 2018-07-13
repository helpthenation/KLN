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


class credit_note_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(credit_note_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_month':self._get_month,
                'get_product_category':self._get_product_category,
                'get_discount_details_april':self._get_discount_details_april,
                'get_discount_details_may':self._get_discount_details_may,
                'get_discount_details_june':self._get_discount_details_june,
                'get_discount_details_july':self._get_discount_details_july,
                'get_discount_details_aug':self._get_discount_details_aug,
                'get_discount_details_sep':self._get_discount_details_sep,
                'get_discount_details_oct':self._get_discount_details_oct,
                'get_discount_details_nov':self._get_discount_details_nov,
                'get_discount_details_dec':self._get_discount_details_dec,
                'get_discount_details_jan':self._get_discount_details_jan,
                'get_discount_details_feb':self._get_discount_details_feb,
                'get_discount_details_mar':self._get_discount_details_mar,
                'get_discount_details_total':self._get_discount_details_total,
                'get_category_april':self._get_category_april,
                'get_category_may':self._get_category_may,
                'get_category_june':self._get_category_june,
                'get_category_july':self._get_category_july,
                'get_category_aug':self._get_category_aug,
                'get_category_sep':self._get_category_sep,
                'get_category_oct':self._get_category_oct,
                'get_category_nov':self._get_category_nov,
                'get_category_dec':self._get_category_dec,
                'get_category_jan':self._get_category_jan,
                'get_category_feb':self._get_category_feb,
                'get_category_march':self._get_category_march,
                'get_category_total':self._get_category_total,
                
        })
        
    def _get_month(self,data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").month
        date=[]
        for i in range(from_month,to_month+1):
            date.append(i)
        print date
        return date
        
    def _get_product_category(self,data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select distinct ai.category_id as categ_id,pc.name as category "\
                                " from account_invoice ai "\
                                " join product_category pc on (ai.category_id=pc.id) "\
                                " where to_char(ai.date_invoice, 'YYYY-MM-DD') >= '%s' "\
                                " and to_char(ai.date_invoice, 'YYYY-MM-DD') <= '%s' "\
                                " and ai.company_id=%s "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()] 
            
        else:
            self.cr.execute(" select ai.category_id as categ_id,pc.name as category "\
                                " from account_invoice ai "\
                                " join product_category pc on (ai.category_id=pc.id) "\
                                " where to_char(ai.date_invoice, 'YYYY-MM-DD') >= '%s' "\
                                " and to_char(ai.date_invoice, 'YYYY-MM-DD') <= '%s' "\
                                " and ai.company_id in %s "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
        categ=[]
        for i in line_list:
            categ.append(i['category'])
        return list(set(categ))
                  
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
        
    def _get_discount_details_april(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            print '***************************8888'
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                                      
            
    def _get_discount_details_may(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list   
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis              
            
    def _get_discount_details_june(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                           
                    
    def _get_discount_details_july(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list  
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                        
           
    def _get_discount_details_aug(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list   
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis              
            
    def _get_discount_details_sep(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list                    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis              
        
        
    def _get_discount_details_oct(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis              
                    
                    
    def _get_discount_details_nov(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list
                
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis              
            
    def _get_discount_details_dec(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list   
                
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                
            
    def _get_discount_details_jan(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
        
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list   
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                              
            
    def _get_discount_details_feb(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            print from_year,to_year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list     
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis                     
                                    
                                
    def _get_discount_details_mar(self, data,month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
            
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where pt.type='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis
                  
            else:
                return line_list
                
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_discount_details_total(self, data):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''    
        from_date_sql.append("ai.date_invoice>= '%s'" % (str(from_date[0])))     
        to_date_sql.append("ai.date_invoice<= '%s'" % (str(to_date[0])))  
        if from_date_sql or  to_date_sql:
            from_date_sql = ' and '+' and '.join(from_date_sql)
            to_date_sql = ' and '+' and '.join(to_date_sql)
        else:
            from_date_sql=''
            to_date_sql=''
    
        self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where pt.type='service' "\
                        " and ai.state in ('open') "\
                        " "+ where_sql +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis      
        else:
            return line_list   
                
        
    def _get_category_april(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_may(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_june(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis       
            
    def _get_category_july(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_aug(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_sep(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_oct(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_nov(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_dec(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_jan(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))   
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_feb(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis            
                           
    def _get_category_march(self, data, categ_id, month):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if from_month in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))
            categ_sql.append("pc.name= '%s'" % (str(categ_id)))    
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                categ_sql = ' and '+' and '.join(categ_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                categ_sql=''
    
            self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id=ai.category_id)"\
                            " where pt.type!='service' "\
                            " and ai.state in ('open') "\
                            " "+ where_sql +  " "\
                            " "+ categ_sql +  " "\
                            " "+ from_date_sql +  " "\
                            " "+ to_date_sql +  " ")
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['total']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list    
        else:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis
            
    def _get_category_total(self, data, categ_id):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        categ_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").month
        print from_month
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''      
        from_date_sql.append("ai.date_invoice>= '%s'" % (str(from_date[0])))     
        to_date_sql.append("ai.date_invoice<= '%s'" % (str(to_date[0])))
        categ_sql.append("pc.name= '%s'" % (str(categ_id)))  
        if from_date_sql or  to_date_sql:
            from_date_sql = ' and '+' and '.join(from_date_sql)
            to_date_sql = ' and '+' and '.join(to_date_sql)
            categ_sql = ' and '+' and '.join(categ_sql)
        else:
            from_date_sql=''
            to_date_sql=''
            categ_sql=''

        self.cr.execute(" select sum(ail.price_subtotal ) as total"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " join product_category pc on (pc.id=ai.category_id)"\
                        " where pt.type!='service' "\
                        " and ai.state in ('open') "\
                        " "+ where_sql +  " "\
                        " "+ categ_sql +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list==[]:
            lis=[]
            val={}
            amount=0
            val['total']=amount  
            lis.append(val)
            return lis      
        else:
            return line_list                                                             
                                                                             
                                                
class wrapped_credit_note_summary_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_credit_note_summary'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_credit_note_summary'
    _wrapped_report_class = credit_note_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
