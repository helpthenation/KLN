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


class sale_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_invoice_details_april':self._get_invoice_details_april,
                'get_invoice_details_may':self._get_invoice_details_may,
                'get_invoice_details_june':self._get_invoice_details_june,
                'get_invoice_details_july':self._get_invoice_details_july,
                'get_invoice_details_august':self._get_invoice_details_august,
                'get_invoice_details_september':self._get_invoice_details_september,
                'get_invoice_details_oct':self._get_invoice_details_oct,
                'get_invoice_details_nov':self._get_invoice_details_nov,
                'get_invoice_details_dec':self._get_invoice_details_dec,
                'get_invoice_details_jan':self._get_invoice_details_jan,
                'get_invoice_details_feb':self._get_invoice_details_feb,
                'get_invoice_details_march':self._get_invoice_details_march,
                'get_invoice_details':self._get_invoice_details,
                'get_invoice_round_april':self._get_invoice_round_april,
                'get_invoice_round_may':self._get_invoice_round_may,
                'get_invoice_round_june':self._get_invoice_round_june,
                'get_invoice_round_july':self._get_invoice_round_july,
                'get_invoice_round_august':self._get_invoice_round_august,
                'get_invoice_round_sep':self._get_invoice_round_sep,
                'get_invoice_round_oct':self._get_invoice_round_oct,
                'get_invoice_round_nov':self._get_invoice_round_nov,
                'get_invoice_round_dec':self._get_invoice_round_dec,
                'get_invoice_round_jan':self._get_invoice_round_jan,
                'get_invoice_round_feb':self._get_invoice_round_feb,
                'get_invoice_round_march':self._get_invoice_round_march,
                'get_invoice_round':self._get_invoice_round,
                'get_invoice_product':self._get_invoice_product,
                'get_invoice_product_april':self._get_invoice_product_april,
                'get_invoice_product_may':self._get_invoice_product_may,
                'get_invoice_product_june':self._get_invoice_product_june,
                'get_invoice_product_july':self._get_invoice_product_july,
                'get_invoice_product_august':self._get_invoice_product_august,
                'get_invoice_product_sep':self._get_invoice_product_sep,
                'get_invoice_product_oct':self._get_invoice_product_oct,
                'get_invoice_product_nov':self._get_invoice_product_nov,
                'get_invoice_product_dec':self._get_invoice_product_dec,
                'get_invoice_product_jan':self._get_invoice_product_jan,
                'get_invoice_product_feb':self._get_invoice_product_feb,
                'get_invoice_product_march':self._get_invoice_product_march,
                'get_invoice_product_data':self._get_invoice_product_data,
                
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
        
    def _get_invoice_details_april(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
            
        if 4 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            
            
    def _get_invoice_details_may(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
            
        if 5 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            

    def _get_invoice_details_june(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 6 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            
            
    def _get_invoice_details_july(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 7 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            

    def _get_invoice_details_august(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 8 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis             

    def _get_invoice_details_september(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 9 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            
            
    def _get_invoice_details_oct(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 10 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis            
          
    def _get_invoice_details_nov(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 11 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis             

    def _get_invoice_details_dec(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 12 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis             
            
    def _get_invoice_details_jan(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 1 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis             

    def _get_invoice_details_feb(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 2 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis   

    def _get_invoice_details_march(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 3 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'            
            self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
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
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            val['product_value']=amount
            lis.append(val)
            return lis 
            
    def _get_invoice_details(self, data):
        where_sql=[]
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
        self.cr.execute(" select sum(ai.amount_total) as invoice, sum(ail.price_unit* ail.quantity) as product_value "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]                                                                                                                  
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
            
    def _get_invoice_round_april(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 4 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount    
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis         
            
    def _get_invoice_round_may(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 5 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount  
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis         
            
    def _get_invoice_round_june(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 6 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis   
            
    def _get_invoice_round_july(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 7 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis     
            
    def _get_invoice_round_august(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 8 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis       
            
    def _get_invoice_round_sep(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 9 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis 
            
    def _get_invoice_round_oct(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 10 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis    
            
    def _get_invoice_round_nov(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 11 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis     
            
    def _get_invoice_round_dec(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 12 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis  
            
    def _get_invoice_round_jan(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 1 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-1-01'
            t_date=str(to_year)+'-1-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_round_feb(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 2 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_round_march(self, data):
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
        if 10 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'            
            self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type='service' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['invoice']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['invoice']=amount
            lis.append(val)
            return lis    
            
    def _get_invoice_round(self, data):
        where_sql=[]
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
        self.cr.execute(" select sum(ail.price_subtotal) as invoice "\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and pt.type='service' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
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
        month=[]
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
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
                        "group by pp.default_code,ail.product_id, pt.name" % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        dic_cus={}
        for cus in line_list:
            dic_cus[cus['product']]=[]
        for cus in line_list:
            dic_cus[cus['product']].append([cus['product_id'],cus['product'],month])
        return dic_cus
        
    def _get_invoice_product_april(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 4 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis    
            
    def _get_invoice_product_may(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 5 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis   
            
    def _get_invoice_product_june(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 6 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis    
            
    def _get_invoice_product_july(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 7 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis            
            
                             
    def _get_invoice_product_august(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 8 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_sep(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 9 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_oct(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 10 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_nov(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 11 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_dec(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 12 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis   
            
    def _get_invoice_product_jan(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 1 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_feb(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 2 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_product_march(self, data,product,month):
        lis=[]
        val={}
        where_sql=[]
        if 3 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'    
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
            self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                            " from account_invoice ai "\
                            " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                            " join product_product pp on (pp.id=ail.product_id)"\
                            " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                            " where ai.type = 'out_invoice' "\
                            " and ai.state not in ('draft,cancel') "\
                            " "+ where_sql +  " "\
                            " and pt.type != 'service' "\
                            " and ail.product_id = '%s' "\
                            " and ai.date_invoice >= '%s' "\
                            " and ai.date_invoice <= '%s' " % (product,str(f_date),str(t_date)))
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
        else:
            val={}
            lis=[]
            amount=0
            val['product_value']=amount
            lis.append(val)
            return lis   
            
    def _get_invoice_product_data(self, data,product):
        lis=[]
        val={}
        where_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []  
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
        self.cr.execute(" select sum(ail.price_unit* ail.quantity) as product_value"\
                        " from account_invoice ai "\
                        " join account_invoice_line ail on (ail.invoice_id=ai.id)"\
                        " join product_product pp on (pp.id=ail.product_id)"\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " and pt.type != 'service' "\
                        " and ail.product_id = '%s' "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " % (product,str(from_date[0]),str(to_date[0])))
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
            
        
                    
            
           
        
class wrapped_sale_summary_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_sale_summary'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_sale_summary'
    _wrapped_report_class = sale_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
