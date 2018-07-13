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


class party_wise_sale_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(party_wise_sale_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_invoice_details': self._get_invoice_details,
                'get_invoice_april':self._get_invoice_april,
                'get_invoice_may':self._get_invoice_may,
                'get_invoice_june':self._get_invoice_june,
                'get_invoice_july':self._get_invoice_july,
                'get_invoice_august':self._get_invoice_august,
                'get_invoice_september':self._get_invoice_september,
                'get_invoice_october':self._get_invoice_october,
                'get_invoice_november':self._get_invoice_november,
                'get_invoice_dec':self._get_invoice_dec,
                'get_invoice_jan':self._get_invoice_jan,
                'get_invoice_feb':self._get_invoice_feb,
                'get_invoice_march':self._get_invoice_march,
                'get_invoice_april_total':self._get_invoice_april_total,
                'get_invoice_may_total':self._get_invoice_may_total,
                'get_invoice_june_total':self._get_invoice_june_total,
                'get_invoice_july_total':self._get_invoice_july_total,
                'get_invoice_august_total':self._get_invoice_august_total,
                'get_invoice_september_total':self._get_invoice_september_total,
                'get_invoice_october_total':self._get_invoice_october_total,
                'get_invoice_november_total':self._get_invoice_november_total,
                'get_invoice_dec_total':self._get_invoice_dec_total,
                'get_invoice_jan_total':self._get_invoice_jan_total,
                'get_invoice_feb_total':self._get_invoice_feb_total,
                'get_invoice_march_total':self._get_invoice_march_total,
                'get_invoice_total':self._get_invoice_total,
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
        
    def _get_invoice_details(self, data):
        month=[]
        where_sql=[]
        partner_sql=[]
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
        if 'partner_ids' in data['form']:
            if len(data['form']['partner_ids']) < 2:
                for ide in data['form']['partner_ids']:
                    partner_sql.append("ai.partner_id=%s" % (str(data['form']['partner_ids'][0])))
            else:
                partner_sql.append("ai.partner_id in %s" % (str(tuple(data['form']['partner_ids']))))
        if partner_sql:
            partner_sql = ' and '+' and '.join(partner_sql)
            str(partner_sql)
        else:
            partner_sql=''            
        print partner_sql        
        self.cr.execute(" select rp.id as partner_id, rp.name as partner,  sum(ai.amount_total) as amount"\
                        " from account_invoice ai "\
                        " join res_partner rp on (rp.id = ai.partner_id)"\
                        " where ai.type = 'out_invoice' "\
                        " and ai.state not in ('draft,cancel') "\
                        " "+ where_sql +  " "\
                        " "+ partner_sql +  " "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " \
                        "group by  rp.id, rp.name"% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        dic_cus={}
        for cus in line_list:
            dic_cus[cus['partner']]=[]
        for cus in line_list:
            dic_cus[cus['partner']].append([cus['partner'],cus['partner_id'],cus['amount'],month])
        return dic_cus
        
    def _get_invoice_april(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_may(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_june(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_july(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_august(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_september(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_october(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_november(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_dec(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_jan(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_feb(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_march(self,data,month,partner_id):
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
            self.cr.execute(" select rp.id as partner_id, sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " \
                " and rp.id = '%s' "\
                "group by  rp.id"% (str(f_date),str(t_date),partner_id))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_april_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 4 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_may_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 5 in month:
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
            self.cr.execute(" select  sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_june_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 6 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' "% (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_july_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 7 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_august_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 8 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_september_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 9 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' "% (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_october_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 10 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_november_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 11 in month:
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
            self.cr.execute(" select  sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_dec_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 12 in month:
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
            self.cr.execute(" select  sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_jan_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 1 in month:
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
            self.cr.execute(" select  sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_feb_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 2 in month:
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
            self.cr.execute(" select sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
            
    def _get_invoice_march_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)        
        if 3 in month:
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
            self.cr.execute(" select  sum(ai.amount_total) as amount"\
                " from account_invoice ai "\
                " join res_partner rp on (rp.id = ai.partner_id)"\
                " where ai.type = 'out_invoice' "\
                " and ai.state not in ('draft,cancel') "\
                " "+ where_sql +  " "\
                " and ai.date_invoice >= '%s' "\
                " and ai.date_invoice <= '%s' " % (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                amount=0
                val['amount']=amount
                lis.append(val)
                return lis
            else:
                return line_list 
        else:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis    
            
    def _get_invoice_total(self,data):
        lis=[]
        val={}
        where_sql=[]
        month=[]
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
        self.cr.execute(" select  sum(ai.amount_total) as amount"\
            " from account_invoice ai "\
            " join res_partner rp on (rp.id = ai.partner_id)"\
            " where ai.type = 'out_invoice' "\
            " and ai.state not in ('draft,cancel') "\
            " "+ where_sql +  " "\
            " and ai.date_invoice >= '%s' "\
            " and ai.date_invoice <= '%s' " % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list==[]:
            amount=0
            val['amount']=amount
            lis.append(val)
            return lis
        else:
            return line_list                     
            
           
        
class wrapped_party_wise_sale_summary_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_party_wise_sale_summary'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_party_wise_sale_summary'
    _wrapped_report_class = party_wise_sale_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
