# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.tools.translate import _
import time
from openerp.osv import osv
from openerp.report import report_sxw
import datetime
from openerp.addons.account.report.common_report_header import common_report_header
from datetime import datetime

class fnet_aged_trial_report(report_sxw.rml_parse,common_report_header):

    def __init__(self, cr, uid, name, context):
        super(fnet_aged_trial_report, self).__init__(cr, uid, name, context=context)
        self.total_account = []
        self.localcontext.update({
            'time': time,
            'get_direction': self._get_direction,
            'get_for_period': self._get_for_period,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_partners':self._get_partners,
            'get_account': self._get_account,
            'get_fiscalyear': self._get_fiscalyear,
            'get_target_move': self._get_target_move,
            'get_age':self._get_age,
            'get_date':self._get_date,
            'get_salesperson':self._get_salesperson,
            'get_customer':self._get_customer,
            'get_lines':self._get_lines,
            'get_total':self._get_total,
            'get_total_value':self._get_total_value,
            'get_total_line':self._get_total_line,
            'get_aged_value':self._get_aged_value,
        })

    
    def _get_salesperson(self,data):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        print where_sql,'*********'
        self.cr.execute("""SELECT distinct rpu.id as id,rpu.name as salesperson 
                        FROM account_invoice ai 
                        JOIN res_partner rp ON (rp.id = ai.partner_id) 
                        JOIN res_company rc ON (rc.id = ai.company_id)"""
                        + str(where_sql[0]) +
                        """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id) 
                        WHERE ai.state in %s
                        AND ai.type in %s and
                        ai.company_id=%s and ai.date_invoice <= %s order by 1""", (tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from']))
        partners = self.cr.dictfetchall()
        return partners
    
    def _get_customer(self,data, sales_id):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        print where_sql,'*********'
        self.cr.execute("""SELECT distinct rp.id as id,rp.name as partner , rp.city as city
                        FROM account_invoice ai 
                        JOIN res_partner rp ON (rp.id = ai.partner_id) 
                        JOIN res_company rc ON (rc.id = ai.company_id)"""
                        + str(where_sql[0]) +
                        """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id) 
                        WHERE ai.state in %s
                        AND ai.type in %s  
                        AND rpu.id =%s and
                        ai.company_id=%s and ai.date_invoice <= %s order by 1""", (tuple(move_state),tuple(type_in),sales_id,data['form']['company_id'][0],data['form']['date_from']))
        partners = self.cr.dictfetchall()
        return partners
    
    def _get_aged_value(self,data, sales_id,partner_id):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        self.cr.execute("""SELECT branch,
                                   partner,
                                   salesperson,
                                   SUM(paid) as opening,
                                   SUM(unpaid) as pending,
                                   SUM(pay) as need_to_pay,
                                   SUM(CASE WHEN not_due > %s THEN pay ELSE 0 END) as due, 
                                   SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) as one,
                                   SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS  two,
                                   SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS three,
                                   SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS four,
                                   SUM(CASE WHEN days >  %s THEN pay ELSE 0 END) AS five 
                            FROM
                            (SELECT rc.name as branch, 
                                rp.name as partner,
                                rpu.name as salesperson,
                                (select date_due from account_invoice where id = ai.id) as not_due,
                                %s - ai.date_due as days,
                                SUM(ai.amount_total) as paid,
                                SUM(ai.residual) as unpaid,
                                SUM(CASE WHEN ai.residual = 0.0 THEN ai.amount_total ELSE ai.residual END) as pay
                            FROM account_invoice ai 
                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                            JOIN res_company rc ON (rc.id = ai.company_id)""" 
                            + str(where_sql[0]) +
                            """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id) 
                            WHERE ai.state in %s 
                            AND ai.type in %s and 
                            ai.company_id= %s and ai.date_invoice <= %s and rpu.id = %s and rp.id= %s
                            GROUP BY rc.name,rp.name,rpu.name,ai.number,ai.id,ai.date_invoice,ai.date_due ORDER BY 1,2)temp 
                            GROUP BY branch,partner,salesperson""", (data['form']['date_from'],str(int(data['form']['4']['start'])-1),data['form']['4']['stop'],data['form']['3']['start'],data['form']['3']['stop'],data['form']['2']['start'],data['form']['2']['stop'],data['form']['1']['start'],data['form']['1']['stop'],data['form']['0']['stop'],data['form']['date_from'],tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from'],sales_id,partner_id))
        partners = self.cr.dictfetchall()
        return partners
    
    def _get_total_value(self,data,sales_id,partner_id):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        self.cr.execute("""SELECT partner,
                           SUM(pay) as paid
                           FROM
                            (SELECT rc.name as branch, 
                                ai.date_invoice as date_invoice,
                                rp.name as partner,
                                ai.number as number,
                                rpu.name as salesperson,
                                (select date_due from account_invoice where id = ai.id) as not_due,
                                %s - ai.date_due as days,
                                SUM(ai.amount_total) as paid,
                                SUM(ai.residual) as unpaid,
                                SUM(CASE WHEN ai.residual = 0.0 THEN ai.amount_total ELSE ai.residual END) as pay
                            FROM account_invoice ai 
                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                            JOIN res_company rc ON (rc.id = ai.company_id)""" 
                            + str(where_sql[0]) +
                            """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id) 
                            WHERE ai.state in %s
                            AND ai.type in %s and
                            ai.company_id= %s and ai.date_invoice <= %s and rpu.id = %s and rp.id=%s
                            GROUP BY rc.name,rp.name,rpu.name,ai.number,ai.id,ai.date_invoice,ai.date_due ORDER BY 1,2)temp 
                            GROUP BY partner""", (data['form']['date_from'],tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from'],sales_id,partner_id))
        partners = self.cr.dictfetchall()
        return partners
         
    def _get_lines(self,data,sales_id,partner_id):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        self.cr.execute("""SELECT branch,partner,date_invoice,number,salesperson,not_due,days,
                               SUM(paid) as opening,
                               SUM(unpaid) as pending,
                               SUM(pay) as need_to_pay,
                               SUM(CASE WHEN not_due > %s THEN pay ELSE 0 END) as due, 
                               SUM(CASE WHEN days >= %s AND days <= %s THEN pay ELSE 0 END) as one,
                               SUM(CASE WHEN days >= %s AND days <= %s THEN pay ELSE 0 END) AS  two,
                               SUM(CASE WHEN days >= %s AND days <= %s THEN pay ELSE 0 END) AS three,
                               SUM(CASE WHEN days >= %s AND days <= %s THEN pay ELSE 0 END) AS four,
                               SUM(CASE WHEN days >=  %s THEN pay ELSE 0 END) AS five 
                        FROM
                        (SELECT rc.name as branch, ai.date_invoice as date_invoice,
                            rp.name as partner,
                            ai.number as number,
                            rpu.name as salesperson,
                            (select date_due from account_invoice where id = ai.id) as not_due,
                            %s - ai.date_due as days,
                            SUM(ai.amount_total) as paid,
                            SUM(ai.residual) as unpaid,
                            SUM(CASE WHEN ai.residual = 0.0 THEN ai.amount_total ELSE ai.residual END) as pay
                        FROM account_invoice ai
                        JOIN res_partner rp ON (rp.id = ai.partner_id)
                        JOIN res_company rc ON (rc.id = ai.company_id)"""
                        + str(where_sql[0]) +
                        """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id)
                        WHERE ai.state in %s 
                        AND ai.type in %s and 
                        ai.company_id= %s and ai.date_invoice <= %s and rpu.id = %s and rp.id= %s 
                        GROUP BY rc.name,rp.name,rpu.name,ai.number,ai.id,ai.date_invoice,ai.date_due ORDER BY 1,2)temp
                        GROUP BY branch,partner,date_invoice,number,salesperson,not_due,days""",(data['form']['date_from'],str(int(data['form']['4']['start'])-1),data['form']['4']['stop'],data['form']['3']['start'],data['form']['3']['stop'],data['form']['2']['start'],data['form']['2']['stop'],data['form']['1']['start'],data['form']['1']['stop'],data['form']['0']['stop'],data['form']['date_from'],tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from'],sales_id,partner_id))
        partners = self.cr.dictfetchall()
        return partners
    
    def _get_total(self,data):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id)")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        self.cr.execute("""SELECT branch,
                               SUM(paid) as opening,
                               SUM(unpaid) as pending,
                               SUM(pay) as need_to_pay,
                               SUM(CASE WHEN not_due > %s THEN pay ELSE 0 END) as due, 
                               SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) as one,
                               SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS  two,
                               SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS three,
                               SUM(CASE WHEN days BETWEEN  %s AND %s THEN pay ELSE 0 END) AS four,
                               SUM(CASE WHEN days >  %s THEN pay ELSE 0 END) AS five 
                        FROM
                        (SELECT rc.name as branch,
                            (select date_due from account_invoice where id = ai.id) as not_due,
                            %s - ai.date_due as days,
                            SUM(ai.amount_total) as paid,
                            SUM(ai.residual) as unpaid,
                            SUM(CASE WHEN ai.residual = 0.0 THEN ai.amount_total ELSE ai.residual END) as pay
                        FROM account_invoice ai
                        JOIN res_partner rp ON (rp.id = ai.partner_id)
                        JOIN res_company rc ON (rc.id = ai.company_id)"""
                        + str(where_sql[0]) +
                        """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id)
                        WHERE ai.state in %s 
                        AND ai.type in %s and 
                        ai.company_id= %s and ai.date_invoice <= %s
                        GROUP BY rc.name,ai.id ORDER BY 1,2)temp
                        GROUP BY branch""",(data['form']['date_from'],str(int(data['form']['4']['start'])-1),data['form']['4']['stop'],data['form']['3']['start'],data['form']['3']['stop'],data['form']['2']['start'],data['form']['2']['stop'],data['form']['1']['start'],data['form']['1']['stop'],data['form']['0']['stop'],data['form']['date_from'],tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from']))
        partners = self.cr.dictfetchall()
        return partners
    
    def _get_total_line(self,data):
        move_state = ['open']
        if data['form']['result_selection'] == 'customer':
            type_in= ['out_invoice']
        elif data['form']['result_selection'] == 'supplier':
            type_in= ['in_invoice']
        elif data['form']['result_selection'] == 'customer_supplier':
            type_in= ['out_invoice','in_invoice']
        where_sql=[]
        if data['form']['direction_selection'] == 'sales':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = ai.user_id) ")
        elif data['form']['direction_selection'] == 'executive':
            where_sql.append("LEFT JOIN res_users ru ON (ru.id = rp.inl_executive_id) ")
        elif data['form']['direction_selection'] == 'team':
            where_sql.append("JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)")
        if len(where_sql) < 1:
            where_sql=''
        self.cr.execute("""SELECT branch,
                                   SUM(pay) as total
                            FROM
                            (SELECT rc.name as branch, 
                                (select date_due from account_invoice where id = ai.id) as not_due,
                                %s - ai.date_due as days,
                                SUM(ai.amount_total) as paid,
                                SUM(ai.residual) as unpaid,
                                SUM(CASE WHEN ai.residual = 0.0 THEN ai.amount_total ELSE ai.residual END) as pay
                            FROM account_invoice ai 
                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                            JOIN res_company rc ON (rc.id = ai.company_id)"""
                            + str(where_sql[0]) +
                            """LEFT JOIN res_partner rpu ON (rpu.id = ru.partner_id) 
                            WHERE ai.state in %s
                            AND ai.type in %s and
                            ai.company_id=%s and ai.date_invoice <= %s
                            GROUP BY rc.name,ai.id ORDER BY 1,2)temp 
                            GROUP BY branch""",(data['form']['date_from'],tuple(move_state),tuple(type_in),data['form']['company_id'][0],data['form']['date_from']))
        partners = self.cr.dictfetchall()
        return partners[0]['total']
            
    def _get_age(self,date,date1):
        if date:
            date_diff = int((datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.datetime.strptime(date1, '%Y-%m-%d')).days)+1
            return date_diff
            

    def _get_direction(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_for_period(self,pos):
        period = self.total_account[int(pos)]
        return period or 0.0

    def _get_partners(self,data):
        # TODO: deprecated, to remove in trunk
        if data['form']['result_selection'] == 'customer':
            return self._translate('Receivable Accounts')
        elif data['form']['result_selection'] == 'supplier':
            return self._translate('Payable Accounts')
        elif data['form']['result_selection'] == 'customer_supplier':
            return self._translate('Receivable and Payable Accounts')
        return ''
    
    def _get_start_date(self, data):
        if data.get('form', False) and data['form'].get('date_from', False):
            return data['form']['date_from']
        return ''

    def _get_target_move(self, data):
        if data.get('form', False) and data['form'].get('target_move', False):
            if data['form']['target_move'] == 'all':
                return _('All Entries')
            return _('All Posted Entries')
        return ''
        
    def _get_account(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id'][0]).name
        return ''
        
    def _get_fiscalyear(self, data):
        if data.get('form', False) and data['form'].get('fiscalyear_id', False):
            return self.pool.get('account.fiscalyear').browse(self.cr, self.uid, data['form']['fiscalyear_id']).name
        return ''

    def _get_company(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id.name
        return ''

    def _get_journal(self, data):
        codes = []
        if data.get('form', False) and data['form'].get('journal_ids', False):
            self.cr.execute('select code from account_journal where id IN %s',(tuple(data['form']['journal_ids']),))
            codes = [x for x, in self.cr.fetchall()]
        return codes

    def _get_currency(self, data):
        if data.get('form', False) and data['form'].get('chart_account_id', False):
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['chart_account_id']).company_id.currency_id.symbol
        return ''

    def _get_date(self, val):
        if val:
            ge = datetime.strptime(val.strftime('%d-%m-%Y'), "%d-%m-%Y")
            return ge
        
class report_aged_partner_invoice(osv.AbstractModel):
    _name = 'report.fnet_aea_function.report_aged_partner_invoice'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_function.report_aged_partner_invoice'
    _wrapped_report_class = fnet_aged_trial_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
