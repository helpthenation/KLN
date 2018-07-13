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
from calendar import monthrange
from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta
import time


class debtors_closing_balance_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(debtors_closing_balance_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_debtors': self._get_debtors,
                'get_debtor_closing':self._get_debtor_closing,
                'get_debtor_total':self._get_debtor_total,
                'get_debtor_opening':self._get_debtor_opening,
                'get_debtor_invoice':self._get_debtor_invoice,
                'get_debtor_cash':self._get_debtor_cash,
                'get_debtor_bank':self._get_debtor_bank,
                'get_debtor_credit_note':self._get_debtor_credit_note,
                
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
        
    def _get_debtors(self, data):
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        self.cr.execute(
                "select distinct aml.partner_id, rp.name from account_move am " \
                "join account_move_line aml on (aml.move_id=am.id) " \
                "join account_account aa on (aml.account_id=aa.id)" \
                "join account_account_type aat on (aa.user_type=aat.id)"\
                "join res_partner rp on (aml.partner_id=rp.id)"\
                "where am.state in ('posted') and " \
                    " aat.code='receivable' and aa.active= True and " \
                    " aml.reconcile_id IS NULL " \
                    " "+ where_sql +  " "\
                    " and am.date >= '%s' "\
                    " and am.date <= '%s' " \
                    " order by 1"% (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_debtor_closing(self,data,partner,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select (sum(aml.debit)-sum(aml.credit)) as balance  " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id) " \
                    "join account_account aa on (aml.account_id=aa.id)" \
                    "join account_account_type aat on (aa.user_type=aat.id)"\
                    "join res_partner rp on (aml.partner_id=rp.id)"\
                    "where am.state in ('posted') and " \
                        " aat.code='receivable' and aa.active= True and " \
                        " aml.reconcile_id IS NULL " \
                        " "+ where_sql +  " "\
                        " and aml.partner_id = '%s' "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (partner,str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                amount=0
                val['balance']=amount   
                lis.append(val)
                return lis      
            else:
                return line_list
        else:
            val={}
            lis=[]
            amount=0
            val['balance']=amount
            lis.append(val)
            return lis

    def _get_debtor_total(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select sum(aml.debit)-sum(aml.credit) as total  " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id) " \
                    "join account_account aa on (aml.account_id=aa.id)" \
                    "join account_account_type aat on (aa.user_type=aat.id)"\
                    "join res_partner rp on (aml.partner_id=rp.id)"\
                    "where am.state in ('posted') and " \
                        " aat.code='receivable' and aa.active= True and " \
                        " aml.reconcile_id IS NULL " \
                        " "+ where_sql +  " "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis  
            
    def _get_debtor_opening(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon-1)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon-1) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon-1) +'-'+ str(from_day)
            print f_date,t_date
            self.cr.execute(
                    "select (sum(aml.debit)-sum(aml.credit)) as total  " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id) " \
                    "join account_account aa on (aml.account_id=aa.id)" \
                    "join account_account_type aat on (aa.user_type=aat.id)"\
                    "join res_partner rp on (aml.partner_id=rp.id)"\
                    "where am.state in ('posted') and " \
                        " aat.code='receivable' and aa.active= True and " \
                        " aml.reconcile_id IS NULL " \
                        " "+ where_sql +  " "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis       
            
    def _get_debtor_invoice(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
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
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select  sum(ai.amount_total) as total " \
                    "from account_invoice ai " \
                    " join account_invoice_line ail on (ail.invoice_id=ai.id) " \
                    "join res_partner rp on (ai.partner_id=rp.id)"\
                    "where ai.state in ('paid') and" \
                        " ai.type = 'out_invoice' " \
                        " "+ where_sql +  " "\
                        " and ai.date_invoice >= '%s' "\
                        " and ai.date_invoice <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis
            
    def _get_debtor_cash(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select (sum(aml.debit)-sum(aml.credit)) as total   " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id)" \
                    "join account_journal aj on (am.journal_id=aj.id) " \
                    "where am.state in ('posted') and" \
                        " aj.type='cash' and  " \
                        "aml.reconcile_id IS NULL  " \
                        " "+ where_sql +  " "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list,'CASHHHHHHHHHHHHHHHHH',f_date,t_date
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis     
            
    def _get_debtor_bank(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select (sum(aml.debit)-sum(aml.credit)) as total   " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id)" \
                    "join account_journal aj on (am.journal_id=aj.id) " \
                    "where am.state in ('posted') and" \
                        " aj.type='bank' and aj.allow_rd_writing=False and " \
                        "aml.reconcile_id IS NULL  " \
                        " "+ where_sql +  " "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
            line_list = [i for i in self.cr.dictfetchall()]
            print line_list,'Bankkkkkkkkkkkkkkkkk',f_date,t_date
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis                                            
        
            
        
    def _get_debtor_credit_note(self,data,mon):
        month=[]
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("am.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("am.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        if mon in month:
            from_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            to_day=monthrange(to_year,mon)[1]
            from_day=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().day
            t_date= str(to_year) +'-'+ str(mon) +'-'+ str(to_day)
            f_date= str(from_year) +'-'+ str(mon) +'-'+ str(from_day)
            self.cr.execute(
                    "select (sum(aml.debit)-sum(aml.credit)) as total   " \
                    "from account_move am  " \
                    "join account_move_line aml on (aml.move_id=am.id)" \
                    "join account_journal aj on (am.journal_id=aj.id) " \
                    "where am.state in ('posted') and" \
                        " aj.type='bank' and aj.allow_rd_writing=True " \
                        " and aml.reconcile_id IS NULL  " \
                        " "+ where_sql +  " "\
                        " and am.date >= '%s' "\
                        " and am.date <= '%s' " \
                        " order by 1"% (str(f_date),str(t_date)))
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
            val={}
            lis=[]
            amount=0
            val['total']=amount
            lis.append(val)
            return lis                    
            
           
        
class wrapped_debtors_closing_balance_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_debtors_closing_balance'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_debtors_closing_balance'
    _wrapped_report_class = debtors_closing_balance_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
