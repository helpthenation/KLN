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


class sale_summary_report_month_wise(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_summary_report_month_wise, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_invoice_details':self._get_invoice_details,
                'get_round_off':self._get_round_off,
                'get_invoice_product':self._get_invoice_product,
                'get_invoice_products':self._get_invoice_products,
                
        })

    def _get_date(self, data):
        val = []
        res = {}
        period_id = 'period_id' in data['form'] and [data['form']['period_id']] or []
        self.cr.execute("select date_start from account_period where id=%s" %(str(period_id[0][0])))
        line_list = [i for i in self.cr.dictfetchall()]
        from_date=line_list[0]['date_start']
        from_month=datetime.strptime(str(from_date), "%Y-%m-%d").date().strftime('%B')
        res['from_month']=from_month
        val.append(res)
        return val
        
    def _get_invoice_details(self, data):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        period_id = 'period_id' in data['form'] and [data['form']['period_id']] or []
        self.cr.execute("select date_start, date_stop from account_period where id=%s" %(str(period_id[0][0])))
        line_list = [i for i in self.cr.dictfetchall()]
        from_date=line_list[0]['date_start']
        to_date=line_list[0]['date_stop']
        from_month=datetime.strptime(str(from_date), "%Y-%m-%d").date().month
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
            
        if from_month==4:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==5:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''
                
        elif from_month==6:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==7:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==8:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''     
                
        elif from_month==9:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==10:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==11:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==12:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==1:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==2:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''  
                
        elif from_month==3:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                   
        self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
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
                   
            
    def _get_round_off(self, data):
        print '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4'
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        period_id = 'period_id' in data['form'] and [data['form']['period_id']] or []
        self.cr.execute("select date_start, date_stop from account_period where id=%s" %(str(period_id[0][0])))
        line_list = [i for i in self.cr.dictfetchall()]
        from_date=line_list[0]['date_start']
        to_date=line_list[0]['date_stop']
        from_month=datetime.strptime(str(from_date), "%Y-%m-%d").date().month
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
        if from_month==4:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==5:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==6:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==7:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==8:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''     
                
        elif from_month==9:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==10:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==11:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==12:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==1:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==2:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
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
                
        elif from_month==3:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
            else:
                from_date_sql=''
                to_date_sql=''           
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and pt.type='service' "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
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
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        period_id = 'period_id' in data['form'] and [data['form']['period_id']] or []
        self.cr.execute("select date_start, date_stop from account_period where id=%s" %(str(period_id[0][0])))
        line_list = [i for i in self.cr.dictfetchall()]
        from_date=line_list[0]['date_start']
        to_date=line_list[0]['date_stop']
        from_month=datetime.strptime(str(from_date), "%Y-%m-%d").date().month
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
        self.cr.execute(" select ail.product_id, pt.name as product"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and pt.type != 'service' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' "\
                        "group by pp.default_code,ail.product_id, pt.name" % (str(from_date),str(to_date)))
        line_list = [i for i in self.cr.dictfetchall()]
        dic_cus={}
        for cus in line_list:
            dic_cus[cus['product_id']]=[]
        for cus in line_list:
            dic_cus[cus['product_id']].append([cus['product_id'],cus['product']])
        return dic_cus                              
        
    def _get_invoice_products(self,data,product):
        where_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        product_id=[]
        print product,'###################################################3333'
        period_id = 'period_id' in data['form'] and [data['form']['period_id']] or []
        self.cr.execute("select date_start, date_stop from account_period where id=%s" %(str(period_id[0][0])))
        line_list = [i for i in self.cr.dictfetchall()]
        from_date=line_list[0]['date_start']
        to_date=line_list[0]['date_stop']
        from_month=datetime.strptime(str(from_date), "%Y-%m-%d").date().month    
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    add=[0]
                    where_sql.append("ai.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("ai.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''         
        if from_month==4:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''
                
        elif from_month==5:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id='' 
                
        elif from_month==6:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''
                
        elif from_month==7:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''   
                
        elif from_month==8:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''     
                
        elif from_month==9:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''  
                
        elif from_month==10:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''     
                
        elif from_month==11:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''
                
        elif from_month==12:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''
                
        elif from_month==1:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id='' 
                
        elif from_month==2:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id='' 
                
        elif from_month==3:
            from_year=datetime.strptime(str(from_date), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'       
            from_date_sql.append("ai.date_invoice>= '%s'" % (str(f_date)))     
            to_date_sql.append("ai.date_invoice<= '%s'" % (str(t_date)))  
            product_id.append("ail.product_id = '%s'" %(product))
            print from_date_sql, to_date_sql 
            if from_date_sql or  to_date_sql:
                from_date_sql = ' and '+' and '.join(from_date_sql)
                to_date_sql = ' and '+' and '.join(to_date_sql)
                product_id = ' and '+' and '.join(product_id)
            else:
                from_date_sql=''
                to_date_sql=''  
                product_id=''                      
        self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " "+ product_id +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " " \
                        " and pt.type != 'service' ")

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
            
       
        
class wrapped_sale_summary_month_wise_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_sale_summary_month_wise'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_sale_summary_month_wise'
    _wrapped_report_class = sale_summary_report_month_wise

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
