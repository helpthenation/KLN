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


class bank_book_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(bank_book_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date':self._get_date,
                'get_com':self._get_com,
                'get_bank_journal':self._get_bank_journal,
                'get_bank_journal_total':self._get_bank_journal_total,
                'get_opening':self._get_opening,
                'get_closing':self._get_closing,
        })

    def _get_bank_journal(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(""" select  aa.name, aa.code,
                                    sum(aml.debit) as debit,
                                    sum(aml.credit) as credit 
                                from
                                account_move am
                                left join account_move_line aml on (aml.move_id=am.id)
                                left join account_journal aj on (am.journal_id=aj.id)
                                left join account_account aa on (aml.account_id=aa.id)
                                where aa.id in 
                                (
                                select distinct aa.id
                                from
                                account_move am
                                left join account_move_line aml on (aml.move_id=am.id)
                                left join account_account aa on (aml.account_id=aa.id)
                                left join account_journal aj on (am.journal_id=aj.id)
                                left join account_account_type aat on (aa.user_type=aat.id)
                                where aat.code!='bank' and aj.type='bank' 
                                ) and am.date >= '%s' and am.date <= '%s'
                                group by aa.name,aa.code order by aa.name""" % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
            
    def _get_bank_journal_total(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(""" select  
                                sum(aml.debit) as debit,
                                sum(aml.credit) as credit 
                            from
                            account_move am
                            left join account_move_line aml on (aml.move_id=am.id)
                            left join account_journal aj on (am.journal_id=aj.id)
                            left join account_account aa on (aml.account_id=aa.id)
                            where aa.id in 
                            (
                            select distinct aa.id
                            from
                            account_move am
                            left join account_move_line aml on (aml.move_id=am.id)
                            left join account_account aa on (aml.account_id=aa.id)
                            left join account_journal aj on (am.journal_id=aj.id)
                            left join account_account_type aat on (aa.user_type=aat.id)
                            where aat.code!='bank' and aj.type='bank' 
                            ) and  am.date >= '%s' and am.date <= '%s' """ % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_opening(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        t_date=datetime.strptime(str(from_date[0]), "%Y-%m-%d")-timedelta(1)
        f_date=datetime.strptime(str(t_date.year) + '-' + str(t_date.month) + '-'+ str(01), "%Y-%m-%d")
        print f_date,t_date
        self.cr.execute(""" select  (sum(aml.debit)-sum(aml.credit)) as total
                                from account_move am 
                                join account_move_line aml on (aml.move_id=am.id) 
                                left join account_journal aj on (am.journal_id=aj.id)
                                join account_account aa on (aml.account_id=aa.id)
                                join account_account_type aat on (aa.user_type=aat.id)
                                join res_partner rp on (aml.partner_id=rp.id)
                                where aat.code='bank' and aa.active= True and aj.type='bank' and
                                aml.reconcile_id IS NULL 
                                and am.date >= '%s' 
                                and am.date <= '%s'                       
                                order by 1 """ % (str(f_date),str(t_date)))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        if line_list[0]['total']==None:
            lis=[]
            val={}
            amount=0.0
            val['total']=amount  
            lis.append(val)
            print lis
            return lis    
        else:   
            return line_list
        
    def _get_closing(self, data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        self.cr.execute(""" select  (sum(aml.debit)-sum(aml.credit)) as total
                                from account_move am 
                                join account_move_line aml on (aml.move_id=am.id) 
                                left join account_journal aj on (am.journal_id=aj.id)
                                join account_account aa on (aml.account_id=aa.id)
                                join account_account_type aat on (aa.user_type=aat.id)
                                join res_partner rp on (aml.partner_id=rp.id)
                                where aat.code='bank' and aa.active= True and aj.type='bank' and
                                aml.reconcile_id IS NULL 
                                and am.date >= '%s' 
                                and am.date <= '%s'                       
                                order by 1 """ % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list[0]['total']==None:
            lis=[]
            val={}
            amount=0.0
            val['total']=amount  
            lis.append(val)
            return lis    
        else:   
            return line_list
    
    def _get_date(self, data):
        val = []
        res = {}
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        now = time.strftime("%d-%m-%Y")
        res['from_date']=datetime.strptime(from_date[0],'%Y-%m-%d').strftime('%d-%m-%Y')
        res['to_date']=datetime.strptime(to_date[0],'%Y-%m-%d').strftime('%d-%m-%Y')
        res['now']=now
        val.append(res)
        return val
        
            
    def _get_com(self,val):
        na = self.pool.get('res.company').browse(self.cr, self.uid, val)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            return na1
        else:
            na1 = 'Apex Agencies'
            return na1
        
class wrapped_bank_book_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_consolidated_bank_book'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_consolidated_bank_book'
    _wrapped_report_class = bank_book_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
