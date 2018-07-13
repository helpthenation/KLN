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


class salary_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(salary_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_employee': self._get_employee,
                'get_contract':self._get_contract,
                'get_payslip_details':self._get_payslip_details,
                'get_payslip_details_total':self._get_payslip_details_total,
                'get_contract_total':self._get_contract_total,
                
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
        
    def _get_employee(self, data):
        month=[]
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
                
        self.cr.execute(" select hp.employee_id, hr.emp_code, hp.contract_id, hr.name_related as name,hd.name as department "\
                        " from hr_payslip hp join hr_employee hr on (hr.id = hp.employee_id) "\
                        "join hr_department hd on (hd.id = hr.department_id)"\
                        " where state='done'"\
                        " and hp.date_from = '%s' "\
                        " and hp.date_to = '%s' " % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_contract(self, data,contract_id):
        month=[]
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
        self.cr.execute(" select hc.employee_id,hc.wage as basic,hc.monthly_deduction,hc.advance_amount,hc.payment_term, "\
                        " hc.tax_deuduction,hc.other_deduction_2,hc.other_deduction_1,hc.lunch_expense,hc.medical_allownace,hc.convance,"\
                        " hc.leave_allownace,hc.hra,hc.special_allowance, hp.lop as LOP,hp.no_of_days, hpl.total as gross"\
                        " from hr_contract hc join hr_payslip hp on (hp.contract_id=hc.id)"\
                        " join hr_payslip_line hpl on (hpl.slip_id=hp.id) where hp.state='done' and hpl.code='GROSS'"\
                        " and hp.date_from = '%s' "\
                        " and hp.contract_id = '%s' "\
                        " and hp.date_to = '%s' " % (str(from_date[0]),str(contract_id),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list        
        
    def _get_payslip_details(self, data,contract_id,code):
        month=[]
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
        self.cr.execute(" select hpl.total from hr_payslip hp join hr_payslip_line hpl on (hpl.slip_id=hp.id) "\
                        " where hp.state='done' and hpl.code='%s'"\
                        " and hp.date_from = '%s' "\
                        " and hp.contract_id = '%s' "\
                        " and hp.date_to = '%s' " % (str(code),str(from_date[0]),str(contract_id),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        lis=[]
        val={}
        if line_list:
            return line_list        
        else:
            val['total']=0.0
            lis.append(val)
            return lis
            
    def _get_contract_total(self, data):
        month=[]
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
        self.cr.execute(" select sum(coalesce(hc.wage,0)) as basic,sum(coalesce(hc.monthly_deduction,0)) as monthly_deduction,sum(coalesce(hc.advance_amount,0)) as advance_amount,sum(coalesce(hc.payment_term,0)) as payment_term, "\
                        " sum(coalesce(hc.tax_deuduction,0)) as tax_deduction,sum(coalesce(hc.other_deduction_2,0)) as other_deduction_2,sum(coalesce(hc.other_deduction_1,0)) as other_deduction_1,sum(coalesce(hc.lunch_expense,0)) as lunch_expense,sum(coalesce(hc.medical_allownace,0)) as medical_allownace, sum(coalesce(hc.convance,0)) as convance,"\
                        " sum(coalesce(hc.leave_allownace,0)) as leave_allownace,sum(coalesce(hc.hra,0)) as hra,sum(coalesce(hc.special_allowance,0)) as special_allowance, sum(coalesce(hp.lop,0)) as lop, sum(coalesce(hp.no_of_days,0)) as no_of_days, sum(coalesce(hpl.total,0)) as gross"\
                        " from hr_contract hc join hr_payslip hp on (hp.contract_id=hc.id)"\
                        " join hr_payslip_line hpl on (hpl.slip_id=hp.id) where hp.state='done' and hpl.code='GROSS'"\
                        " and hp.date_from = '%s' "\
                        " and hp.date_to = '%s' " % (str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        lis=[]
        val={}    
        if line_list[0]['basic']==None:
            val['basic']=0.0
            val['monthly_deduction']=0.0
            val['advance_amount']=0.0
            val['tax_deuduction']=0.0
            val['other_deduction_2']=0.0
            val['leave_allownace']=0.0
            val['hra']=0.0
            val['payment_term']=0.0
            val['convance']=0.0
            val['lunch_expense']=0.0
            val['other_deduction_1']=0.0
            val['gross']=0.0
            val['no_of_days']=0.0
            val['lop']=0.0
            val['special_allowance']=0.0
            val['medical_allownace']=0.0
            lis.append(val)
            return lis  
        else:
            return line_list        
        
    def _get_payslip_details_total(self, data,code):
        month=[]
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
        self.cr.execute(" select sum(hpl.total) as total from hr_payslip hp join hr_payslip_line hpl on (hpl.slip_id=hp.id) "\
                        " where hp.state='done' and hpl.code='%s'"\
                        " and hp.date_from = '%s' "\
                        " and hp.date_to = '%s' " % (str(code),str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        lis=[]
        val={}
        if line_list:
            return line_list        
        else:
            val['total']=0.0
            lis.append(val)
            return lis             
            
           
        
class wrapped_salary_summary_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_salary_summary'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_salary_summary'
    _wrapped_report_class = salary_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
