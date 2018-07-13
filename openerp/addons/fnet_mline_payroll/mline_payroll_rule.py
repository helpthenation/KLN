
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from calendar import monthrange
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from openerp.exceptions import ValidationError,Warning
from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval
class mline_payroll_rule(osv.osv):
    _name = 'mline.payroll.rule'
    _columns = {
           'name':fields.char('Name', size=64, required=True),
           'code':fields.char('Code', size=64, required=True),
           'type': fields.selection([('add', 'Add'),('remove', 'Remove')], 'Type',required=True),
           'debit_account_id': fields.many2one('account.account', 'Debit Account'),
           'credit_account_id': fields.many2one('account.account', 'Credit Account'),
               }
    _defaults = {
         'type':'add',
          }

    def draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'})

mline_payroll_rule()

class mline_payroll_run(osv.osv):

    _name = 'mline.payroll.run'
    _description = 'Employee Payslip Batches'
    _columns = {
        'name': fields.char('Name', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'slip_ids': fields.one2many('mline.payroll', 'payroll_run_id', 'Employee Payslips', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('close', 'Close'),
        ], 'Status', select=True, readonly=True, copy=False),
        'date_start': fields.date('Date From', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'date_end': fields.date('Date To', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'credit_note': fields.boolean('Credit Note', readonly=True, states={'draft': [('readonly', False)]}, help="If its checked, indicates that all payslips generated from here are refund payslips."),
    }
    _defaults = {
        'state': 'draft',
        'date_start': lambda *a: time.strftime('%Y-%m-01'),
        'date_end': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }

    def draft_payslip_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def close_payslip_run(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'close'}, context=context)

class mline_payroll(osv.osv):
    _name = 'mline.payroll'

    def _count_detail_payslip(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for details in self.browse(cr, uid, ids, context=context):
            res[details.id] = len(details.salary_line)
        return res

    _columns = {
           'name':fields.char('Name', size=64, readonly=True, required=True),
           'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
           'job_id':fields.many2one('hr.job', 'Designation'),
           'emp_id':fields.char('Employee Id', size=64),
           'contract_id':fields.many2one('hr.contract', 'Contract'),
           'branch_id':fields.many2one('company.branch', 'Company'),
           'date_from':fields.date('From Date', required=True),
           'date_to':fields.date('To Date', required=True),
           'move_id':fields.many2one('account.move', 'Journal Entries'),
           'state': fields.selection([
                ('draft', 'Draft'),
                ('compute', 'Computation'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
                        ], 'Status', readonly=True),
           'working_line':fields.one2many('mline.working.line', 'payroll_id', 'Working'),
           'salary_line':fields.one2many('mline.payroll.line', 'payroll_id', 'Payroll'),
           'input_line_ids': fields.one2many('mline.input.line', 'payslip_id', 'Payslip Inputs'),
           'payslip_type': fields.selection([
                ('general', 'General Payslip'),
                ('vacation', 'Vacation Payslip'),
                ('long_vacation', 'Long Vacation Payslip'),
                        ], 'Payslip Type', required=True),
            'payroll_run_id': fields.many2one('mline.payroll.run', 'Payslip Batches', readonly=True, states={'draft': [('readonly', False)]}, copy=False),
            'payslip_count': fields.function(_count_detail_payslip, type='integer', string="Payslip Computation Details"),

             }

    _defaults = {
        'date_from': lambda *a: time.strftime('%Y-%m-01'),
        'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        'state': 'draft',
        #~ 'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'mline.payroll') or '/',
        'payslip_type':'general',
               }

    def create(self, cr, uid, values, context=None):
        if context is None:
            context = {}        
        input_obj=self.pool.get('mline.input.line')
        obj_sequence=self.pool.get('ir.sequence')
        if values.get('payslip_type'):
            h=str('mline.')+str(values.get('payslip_type'))
            seq=obj_sequence.next_by_code(cr,uid,h,context=context)   or 'New'
            values.update({'name':seq})             
        new_rec=super(mline_payroll, self).create(cr, uid, values, context=context)
        if values.get('date_from') and values.get('date_to'):
            start_date=parse(values.get('date_from'))
            stop_date=parse(values.get('date_to'))
            for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                 day_dates=dts.strftime("%Y-%m-%d")
                 cr.execute("""SELECT id
                                    FROM mline_payroll
                                    WHERE '%s' between date_from::date and date_to::date and employee_id = %d and id != %d"""%(day_dates,values.get('employee_id'),new_rec))
                 data=cr.dictfetchone()
                 if data:
                     raise osv.except_osv(_('Invalid Action!'), _(' Payroll Already Generated For This Employee For The Selected Period !'))
        if values.get('payslip_type') == 'general':
            cr.execute("""select hh.id
                    from hr_holidays hh
                    join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                    where hh.employee_id = '%s' and hhs.code in ('VL','LVL') and hh.state='validate'
                    and hh.type='remove'  and hh.date_from::date >= '%s' and hh.date_to::date <= '%s'
                    """%(values.get('employee_id'),values.get('date_from'),values.get('date_to')))              
            data = cr.dictfetchone()
            if data:
                raise osv.except_osv(_('Invalid Action!'), _('''You Can't Generate General Payslip For The Selected Since There Is Leave Record In For Long Vacation Or Vacation'''))
            loan_obj = self.pool.get('hr.loan')
            loan_line_obj = self.pool.get('hr.loan.line')
            loan_ids = loan_obj.search(cr ,uid ,[('employee_id','=',values.get('employee_id')),('state','=','done'),])
            loan_total = 0.0
            input_ids=[]
            if loan_ids:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search(cr ,uid ,[('loan_id','=',loan_id),
                                                              #~ ('paid_date','>=',date_from),
                                                              ('paid_date','<=',values.get('date_to')),
                                                              ('paid','=',False),
                                                              ])
                    if line_ids:
                        for loan in loan_line_obj.browse(cr ,uid ,line_ids):
                            loan_total = loan.paid_amount                        
                            input_obj.create(cr,uid,{'name': 'Loan', 'code': 'LOAN', 'amount': loan_total, 'contract_id': values.get('contract_id'),
                            'loan_id':loan.id,'payslip_id':new_rec},context=context)
        return new_rec
    def write(self, cr, uid, ids,values, context=None):
        obj=self.browse(cr,uid,ids)
        if context is None:
            context = {}        
        input_obj=self.pool.get('mline.input.line')            
        payslip_type =  values.get('payslip_type') or obj.payslip_type
        emp_id =   values.get('employee_id') or obj.employee_id.id 
        to_date =  values.get('date_to') or obj.date_to
        contract_id = values.get('contract_id') or obj.contract_id.id 
        if values.get('employee_id') or values.get('date_to') or values.get('payslip_type'):
            cr.execute("""delete from mline_input_line where payslip_id = %d"""%(obj.id))
            if payslip_type == 'general':
                loan_obj = self.pool.get('hr.loan')
                loan_line_obj = self.pool.get('hr.loan.line')
                loan_ids = loan_obj.search(cr ,uid ,[('employee_id','=',emp_id),('state','=','done'),])
                loan_total = 0.0
                input_ids=[]
                if loan_ids:
                    for loan_id in loan_ids:
                        line_ids = loan_line_obj.search(cr ,uid ,[('loan_id','=',loan_id),
                                                                  ('paid_date','<=',to_date),
                                                                  ('paid','=',False),
                                                                  ])
                        if line_ids:
                            for loan in loan_line_obj.browse(cr ,uid ,line_ids):
                                loan_total = loan.paid_amount                        
                                input_obj.create(cr,uid,{'name': 'Loan', 'code': 'LOAN', 'amount': loan_total, 'contract_id': contract_id,
                                'loan_id':loan.id,'payslip_id':obj.id},context=context)
        return super(mline_payroll, self).write(cr, uid,ids, values, context=context)                    
    def onchange_payslip_type(self, cr, uid, ids, payslip_type,employee_id,context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if payslip_type == 'vacation' and employee_id:
            cr.execute("""
                    select max(hh.date_from::date) as start_date,max(hh.date_to::date) as end_date
                    from hr_holidays hh
                    join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                    where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate'
                    and hh.type='remove' group by hh.date_from,hh.date_to  order by hh.date_to::date desc """%(employee_id))
            get_date=cr.dictfetchone()
            if get_date:
                start=datetime.strptime(get_date['start_date'],'%Y-%m-%d')
                end=datetime.strptime(get_date['end_date'],'%Y-%m-%d')
                if ((end-start).days+1) >= user.company_id.number_of_days_vacation_leave:
                    result = {'value': {
                               'date_from': start,
                               'date_to': end,
                               }}
                    return result
                else:
                        return {'warning': {
                            'title': "Warning!!!",
                            'message': "You Can't Generate Vacation Payslip For No.Of.Lesser Than %s!!!." %(user.company_id.number_of_days_vacation_leave)},
                            'value': {'payslip_type':None,'date_from':False,'date_to':False}}
            else:
                    return {'warning': {
                        'title': "Warning!!!",
                        'message': "There Is No Vacation Leave Record.Kindly Check!!!."},
                        'value': {'payslip_type':None,'date_from':False,'date_to':False}}                           
        elif payslip_type == 'long_vacation' and employee_id:
            return {'value': {'date_from':False,'date_to':False}}

    def onchange_date_from(self, cr, uid, ids, date_to, date_from,employee_id,payslip_type):
        if date_from and date_to and employee_id:
            start_date=parse(date_from)
            stop_date=parse(date_to)
            for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                 day_dates=dts.strftime("%Y-%m-%d")
                 cr.execute("""SELECT id
                                    FROM mline_payroll
                                    WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                 data=cr.dictfetchone()
                 if data:
                     raise osv.except_osv(_('Invalid Action!'), _(' Payroll Already Generated For This Employee For The Selected Period !'))
            if payslip_type == 'vacation':
                cr.execute("""
                        select max(hh.date_from::date) as date_from,max(hh.date_to::date) as date_to
                        from hr_holidays hh
                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                        where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate'
                        and hh.type='remove' 
                        group by hh.date_from::date
                        order by hh.date_from::date desc """%(employee_id))
                get_date=cr.dictfetchone()
                if not get_date:
                    res = {'warning': {
                            'title': "Warning!!!",
                            'message': "There Is No Vacation Leave Request For The Given From Date And To Date !!!",},
                           'value': {'date_from':False,'date_to':False}}
                    return res                    
                elif  get_date:   
                    for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                         day_dates=dts.strftime("%Y-%m-%d")
                         cr.execute("""SELECT hh.id
                                            from hr_holidays hh
                                            join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                         data=cr.dictfetchone()
                         if not data:
                             res = {'warning': {
                                    'title': "Invalid Action!!!",
                                    'message': "There Is No Vacation Leave Record For The Given From Date And To Date !!!",},
                                   'value': {'date_from':False,'date_to':False}}
                             return res                    
            elif payslip_type == 'long_vacation':
                cr.execute("""
                        select max(hh.date_from::date) as date_from,max(hh.date_to::date) as date_to
                        from hr_holidays hh
                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                        where hh.employee_id = '%s' and hhs.code ='LVL' and hh.state='validate'
                        and hh.type='remove' 
                        group by hh.date_from::date
                        order by hh.date_from::date desc """%(employee_id))
                get_date=cr.dictfetchone()
                if not get_date:
                    res = {'warning': {
                            'title': "Warning!!!",
                            'message': "There Is No Long Vacation Leave Request For The Given From Date And To Date !!!",},
                           'value': {'date_from':False,'date_to':False}}
                    return res                    
                elif  get_date:   
                    for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                         day_dates=dts.strftime("%Y-%m-%d")
                         cr.execute("""SELECT hh.id
                                            from hr_holidays hh
                                            join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                         data=cr.dictfetchone()
                         if not data:
                             res = {'warning': {
                                    'title': "Invalid Action!!!",
                                    'message': "There Is No Long Vacation Leave Record For The Given From Date And To Date !!!",},
                                   'value': {'date_from':False,'date_to':False}}
                             return res                  
    def onchange_date_to(self, cr, uid, ids, date_to, date_from,employee_id,payslip_type):
        if date_from and date_to and employee_id:
            start_date=parse(date_from)
            stop_date=parse(date_to)
            for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                 day_dates=dts.strftime("%Y-%m-%d")
                 cr.execute("""SELECT id
                                    FROM mline_payroll
                                    WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                 data=cr.dictfetchone()
                 if data:
                     raise osv.except_osv(_('Invalid Action!'), _(' Payroll Already Generated For This Employee For The Selected Period !'))
            if payslip_type == 'vacation':
                cr.execute("""
                        select max(hh.date_from::date) as date_from,max(hh.date_to::date) as date_to
                        from hr_holidays hh
                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                        where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate'
                        and hh.type='remove' 
                        group by hh.date_from::date
                        order by hh.date_from::date desc """%(employee_id))
                get_date=cr.dictfetchone()
                if not get_date:
                    res = {'warning': {
                            'title': "Warning!!!",
                            'message': "There Is No Vacation Leave Request For The Given From Date And To Date !!!",},
                           'value': {'date_from':False,'date_to':False}}
                    return res                    
                elif  get_date:   
                    for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                         day_dates=dts.strftime("%Y-%m-%d")
                         cr.execute("""SELECT hh.id
                                            from hr_holidays hh
                                            join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                         data=cr.dictfetchone()
                         if not data:
                             res = {'warning': {
                                    'title': "Invalid Action!!!",
                                    'message': "There Is No Vacation Leave Record For The Given From Date And To Date !!!",},
                                   'value': {'date_from':False,'date_to':False}}
                             return res 

            elif payslip_type == 'long_vacation':
                cr.execute("""
                        select max(hh.date_from::date) as date_from,max(hh.date_to::date) as date_to
                        from hr_holidays hh
                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                        where hh.employee_id = '%s' and hhs.code ='LVL' and hh.state='validate'
                        and hh.type='remove' 
                        group by hh.date_from::date
                        order by hh.date_from::date desc """%(employee_id))
                get_date=cr.dictfetchone()
                if not get_date:
                    res = {'warning': {
                            'title': "Warning!!!",
                            'message': "There Is No Long Vacation Leave Request For The Given From Date And To Date !!!",},
                           'value': {'date_from':False,'date_to':False}}
                    return res                    
                elif  get_date:   
                    for dts in rrule(DAILY, dtstart=start_date, until=stop_date):
                         day_dates=dts.strftime("%Y-%m-%d")
                         cr.execute("""SELECT hh.id
                                            from hr_holidays hh
                                            join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            WHERE '%s' between date_from::date and date_to::date and employee_id = %d """%(day_dates,employee_id))
                         data=cr.dictfetchone()
                         if not data:
                             res = {'warning': {
                                    'title': "Invalid Action!!!",
                                    'message': "There Is No Long Vacation Leave Record For The Given From Date And To Date !!!",},
                                   'value': {'date_from':False,'date_to':False}}
                             return res                 
    def worked_days(self, cr, uid, ids, context=None):
        emps = []
        leave = []
        tot = []
        re = []
        lea_da = []
        emp_ret = []
        lisss = []
        friday=[]
        ret = []
        publi_hol=[]
        si=[]
        stay_fri=[]
        obj = self.browse(cr, uid, ids)
        det = obj.date_from
        year_obj, month_obj, day = (int(x) for x in det.split('-'))
        present_days=[]
        start_date=parse(obj.date_from)
        stop_date=parse(obj.date_to)            
        cr.execute('''select date from public_holiday where date >='%s' and date <= '%s' ''' % (obj.date_from,obj.date_to))
        leave_date = cr.fetchall()
        cr.execute('''select hh.employee_id,hh.date_from,hh.date_to
                        from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='SL' and hh.state='validate'
                      and hh.date_from::date >='%s' and hh.date_from::date <= '%s'  ''' % (obj.employee_id.id,obj.date_from,obj.date_to ))
        emps = cr.dictfetchall()
        if emps != []:
            for k in emps:
                start=parse(k['date_from'])
                stop=parse(k['date_to'])
                for dts in rrule(DAILY, dtstart=start, until=stop):
                    dat= dts.strftime("%A")
                    if dat == 'Friday':
                        day_dates=dts.strftime("%Y-%m-%d")
                        stay_fri.append(day_dates)
        for da in leave_date:
            publi_hol.append(da)
            si = [x[0] for x in publi_hol]
        for dt in rrule(DAILY, dtstart=start_date, until=stop_date):
            dat= dt.strftime("%A")
            if dat == 'Friday':
                datess=dt.strftime("%Y-%m-%d")
                if datess not in si:
                    if  datess not in stay_fri:
                            friday.append(datess)
        present_days.extend(si)
        cur_date=[]
        cr.execute('''select hh.employee_id,hh.date_from,hh.date_to
                        from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code not in ('SL','UL','VL','LVL') and hh.state='validate'
                        and hh.date_from::date >='%s' and hh.date_from::date <= '%s'  ''' % (obj.employee_id.id,obj.date_from,obj.date_to ))
        emp = cr.dictfetchall()
        if emp != []:
            for k in emp:
                if k['date_from'] and k['date_to']:
                    start_dates=parse(k['date_from'])
                    stop_dates=parse(k['date_to'])
                    for dts in rrule(DAILY, dtstart=start_dates, until=stop_dates):
                        dat= dts.strftime("%A")
                        if dat != 'Friday':
                            day_dates=dts.strftime("%Y-%m-%d")
                            cur_date.append(day_dates)
        present_days.extend(cur_date)
        cr.execute('''select date  from hr_attendance
                       where employee_id = '%s'  and  date >='%s' and date <= '%s'  ''' % (obj.employee_id.id, obj.date_from,obj.date_to ))
        att = cr.fetchall()
        attend=[x[0] for x in att]
        present_days.extend(attend)
        cr.execute('''select
                            sum(ot_hours) as ot,
                            sum(holiday_hours) as hol
                      from hr_timesheet_sheet_sheet
                      where employee_id = '%s' and state='done' and date_from >='%s' and date_from <= '%s' ''' % (obj.employee_id.id,obj.date_from,obj.date_to ))
        time = cr.dictfetchall()
        cr.execute(''' select
                            sum(hh.number_of_days) as days
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code='SL' and hh.state='validate'
                       and hh.date_from::date >='%s' and hh.date_from::date <= '%s'  ''' % (obj.employee_id.id,obj.date_from,obj.date_to ))
        stay = cr.dictfetchall()
        st = 0.00
        if stay[0]['days'] is None:
            st = 0.00
        else:
            st = abs(stay[0]['days'])
        cr.execute(''' select
                            sum(hh.number_of_days) as days
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code='UL' and hh.state='validate'
                       and hh.date_from::date >='%s' and hh.date_from::date <= '%s'  ''' % (obj.employee_id.id,obj.date_from,obj.date_to ))
        leave = cr.dictfetchall()
        le = 0.00
        if leave[0]['days'] is None:
            le = 0.00
        else:
            le = abs(leave[0]['days'])
        pay_sr = self.pool.get('mline.working.line').search(cr, uid, [('payroll_id', '=', obj.id)], context=context)
        if not pay_sr:
            vals = {
               'payroll_id':obj.id,
               'ot_hours':time[0]['ot'],
               'holiday_hours':time[0]['hol'],
               'leave_days':le,
               'stay_days':st
               }
            if obj.payslip_type == 'general':
                if present_days != []:
                    vals.update({'present_days':len(set(present_days))})
                else:
                    vals.update({'present_days':0.00})
            else:
                if obj.date_from and obj.date_to:
                    start=datetime.strptime(obj.date_from,'%Y-%m-%d')
                    end=datetime.strptime(obj.date_to,'%Y-%m-%d')
                    if (end-start).days:
                        vals.update({'present_days':(end-start).days + 1})
                    else:
                        vals.update({'present_days':0.00})
            self.pool.get('mline.working.line').create(cr, uid, vals, context=context)
        return self.write(cr, uid, ids, {'state': 'compute'}, context=context)

    def _get_datas(self, cr, uid, obj, context=None):
        data = []
        ots = {}
        hols = {}
        leave = {}
        rule = self.pool.get('mline.payroll.rule')
        for line in obj.working_line:
            ot = line.ot_hours * obj.contract_id.ot_price
            hol = line.holiday_hours * obj.contract_id.holiday_price
            le =  (line.leave_days * 8) * obj.contract_id.normal_price
            if line.leave_days == 0.00:
                ru = rule.search(cr, uid, [('code', 'in', ('OT', 'HOL'))], context=context)
                for rul_id in rule.browse(cr, uid, ru):
                    if rul_id.code == 'OT' and ot <> 0.00:
                        ots['amd'] = ot
                        ots['rule'] = rul_id.id
                        data.append(ots)
                    else:
                        if hol <> 0.00:
                            hols['amd'] = hol
                            hols['rule'] = rul_id.id
                            data.append(hols)
            else:
                ru = rule.search(cr, uid, [('code', 'in', ('OT', 'HOL', 'LEAVE'))], context=context)
                for rul_id in rule.browse(cr, uid, ru):
                    if rul_id.code == 'OT' and ot <> 0.00:
                        ots['amd'] = ot
                        ots['rule'] = rul_id.id
                        data.append(ots)
                    elif rul_id.code == 'HOL' and hol <> 0.00:
                        hols['amd'] = hol
                        hols['rule'] = rul_id.id
                        data.append(hols)
                    else:
                        if len(leave) < 1 and rul_id.code not in ('OT', 'HOL'):
                            leave['amd'] = le
                            leave['rule'] = rul_id.id
                            data.append(leave)
        return data


    def compute_sheet(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        det = obj.date_from
        year_obj, month_obj, day = (int(x) for x in det.split('-'))
        no_of_days=monthrange(year_obj,month_obj)[1]
        cont = self.pool.get('hr.contract')
        contract_id=cont.browse(cr, uid, obj.contract_id.id)
        sal = self.pool.get('mline.payroll.line')
        rule = self.pool.get('mline.payroll.rule')
        gross_rule = rule.search(cr, uid, [('code', '=', 'GROSS')], context=context)
        basic_rule = rule.search(cr, uid, [('code', '=', 'BASIC')], context=context)
        food_rule = rule.search(cr, uid, [('code', '=', 'FOOD')], context=context)
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)
        cash_rule = rule.search(cr, uid, [('code', '=', 'CSH')], context=context)
        net_rule = rule.search(cr, uid, [('code', '=', 'NET')], context=context)
        loan_rule = rule.search(cr, uid, [('code', '=', 'LOAN')], context=context)
        eos_rule = rule.search(cr, uid, [('code', '=', 'EOS')], context=context)
        work = [line for line in obj.working_line]
        input_line=[line for line in obj.input_line_ids]
        print'DDDDDDDDDDDDDDDDDD',contract_id.avail_eos
        deduction=[]
        if work:
            cr.execute(''' SELECT
                                hcl.rule_id as rule,
                                hcl.amount as amd
                           FROM hr_contract hc
                           JOIN hr_contract_line hcl ON (hcl.contract_id = hc.id)
                           WHERE hc.id = '%s'
                           order by 1 ''' % (obj.contract_id.id))
            sala = cr.dictfetchall()
            data = self._get_datas(cr, uid, obj, context=context)
            sal_sr = sal.search(cr, uid, [('payroll_id', '=', obj.id)], context=context)
            if not sal_sr:
                gross=0.0
                basic_amount=0.0
                food_amount=0.0
                hra=0.0
                for line in sala:
                    if  rule.browse(cr,uid,line['rule']).code == 'BASIC':
                        gross=cont.browse(cr, uid, obj.contract_id.id).gross
                        #~ basic_per_day=round(line['amd']/no_of_days,2)
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        basic_per_day=round(limit_by_3,2)
                        basic_amount=limit_by_3*work[0].present_days
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':basic_rule[0],
                         'amount':round(basic_amount)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'FOOD':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        food_per_day=round(limit_by_3,2)
                        food_amount=limit_by_3*work[0].present_days
                        #~ food_per_day =   round(line['amd'] /no_of_days,2)
                        #~ food_amount =   food_per_day * (work[0].present_days+work[0].stay_days)
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':food_rule[0],
                         'amount':round(food_amount)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'HRA':
                        hra=line['amd']
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':line['rule'],
                         'amount':line['amd']
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'OA':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        other_per_day=round(limit_by_3,2)
                        other_allowance=limit_by_3*work[0].present_days
                        #~ other_allowance = round(line['amd'] /no_of_days,2)
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':oa_rule[0],
                         'amount':round(other_allowance)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'CSH':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        cash_per_day=round(limit_by_3,2)
                        cash_allowance=limit_by_3*work[0].present_days
                        #~ cash_allowance =  round(line['amd']/no_of_days,2)
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':cash_rule[0],
                         'amount':round(cash_allowance)
                          }
                        sal.create(cr, uid, val, context=context)
 #~ FOR LOAN PROCESSING                       
                    elif  rule.browse(cr,uid,line['rule']).code == 'LOAN':
                        if input_line:
                            for rec in input_line:                        
                                val = {
                                 'payroll_id':obj.id,
                                 'rule_id':loan_rule[0],
                                 'amount': -(rec.amount)
                                  }
                                sal.create(cr, uid, val, context=context)        
                                deduction.append(rec.amount)     
                    elif  contract_id.avail_eos:                      
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':eos_rule[0],
                         'amount': round((basic_amount/30.0) * contract_id.service_days)
                          }
                        sal.create(cr, uid, val, context=context)        
                                                                              
                    else:
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':line['rule'],
                         'amount':line['amd']
                          }
                        sal.create(cr, uid, val, context=context)

                for datas in data:
                    vals = {
                     'payroll_id':obj.id,
                     'rule_id':datas['rule'],
                     'amount':datas['amd']
                      }
                    sal.create(cr, uid, vals, context=context)
                cr.execute(''' SELECT
                                     sum(amount) as gross
                               FROM mline_payroll_line mpl
                               JOIN mline_payroll_rule mpr ON (mpr.id = mpl.rule_id)
                               WHERE mpl.payroll_id= '%s' and mpr.type = 'add' ''' % (obj.id))
                gross = cr.dictfetchall()
                cr.execute(''' SELECT
                                    ROUND(sum(amount)) as net
                               FROM mline_payroll_line mpl
                               JOIN mline_payroll_rule mpr ON (mpr.id = mpl.rule_id)
                               WHERE mpl.payroll_id= '%s' and mpr.type = 'add' ''' % (obj.id))
                net = cr.dictfetchall()
                gro_val = {
                         'payroll_id':obj.id,
                         'rule_id':gross_rule[0],
                         'amount':gross[0]['gross'] - sum(deduction)
                         }
                sal.create(cr, uid, gro_val, context=context)
                gro_val = {
                         'payroll_id':obj.id,
                         'rule_id':net_rule[0],
                         'amount':net[0]['net'] - sum(deduction)
                         }
                sal.create(cr, uid, gro_val, context=context)
                if contract_id.avail_eos:          
                        print'DDDDDDDDDDDDDDDDDDDDDDDD' , contract_id.service_days          
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':eos_rule[0],
                         'amount': round(((contract_id.gross * 0.6)/30.0) * contract_id.service_days)
                          }
                        sal.create(cr, uid, val, context=context)                
            else:
                sal_sr1 = sal.search(cr, uid, [('payroll_id', '=', obj.id)], context=context)
                sal.unlink(cr, uid, sal_sr1, context=context)
                gross=0.0
                basic_amount=0.0
                food_amount=0.0
                hra=0.0
                for line in sala:
                    if  rule.browse(cr,uid,line['rule']).code == 'BASIC':
                        gross=cont.browse(cr, uid, obj.contract_id.id).gross
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        basic_per_day=round(limit_by_3,2)
                        basic_amount=limit_by_3*work[0].present_days
                        #~ basic_amount=basic_per_day*work[0].present_days
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':basic_rule[0],
                         'amount':round(basic_amount)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'FOOD':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        food_per_day=round(limit_by_3,2)
                        food_amount=limit_by_3*work[0].present_days
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':food_rule[0],
                         'amount':round(food_amount)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'HRA':
                        hra=line['amd']
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':line['rule'],
                         'amount':line['amd']
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'OA':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        other_per_day=round(limit_by_3,2)
                        other_allowance=limit_by_3*work[0].present_days
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':oa_rule[0],
                         'amount':round(other_allowance)
                          }
                        sal.create(cr, uid, val, context=context)
                    elif  rule.browse(cr,uid,line['rule']).code == 'CSH':
                        split_point=str(float(line['amd']/no_of_days)).split('.')
                        limit_by_3=float(split_point[0]+'.'+split_point[1][0:3])
                        cash_per_day=round(limit_by_3,2)
                        cash_allowance=limit_by_3*work[0].present_days
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':cash_rule[0],
                         'amount':round(cash_allowance)
                          }
                        sal.create(cr, uid, val, context=context)
 #~ FOR LOAN PROCESSING                       
                    elif  rule.browse(cr,uid,line['rule']).code == 'LOAN':
                        if input_line:
                            for rec in input_line:                        
                                val = {
                                 'payroll_id':obj.id,
                                 'rule_id':loan_rule[0],
                                 'amount': -(rec.amount)
                                  }
                                sal.create(cr, uid, val, context=context)     
                                deduction.append(rec.amount)  
                      
                    else:
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':line['rule'],
                         'amount':line['amd']
                          }
                        sal.create(cr, uid, val, context=context)

                for datas in data:
                    vals = {
                     'payroll_id':obj.id,
                     'rule_id':datas['rule'],
                     'amount':datas['amd']
                      }
                    sal.create(cr, uid, vals, context=context)
                cr.execute(''' SELECT
                                     sum(amount) as gross
                               FROM mline_payroll_line mpl
                               JOIN mline_payroll_rule mpr ON (mpr.id = mpl.rule_id)
                               WHERE mpl.payroll_id= '%s' and mpr.type = 'add' ''' % (obj.id))
                gross = cr.dictfetchall()
                cr.execute(''' SELECT
                                    ROUND(sum(amount)) as net
                               FROM mline_payroll_line mpl
                               JOIN mline_payroll_rule mpr ON (mpr.id = mpl.rule_id)
                               WHERE mpl.payroll_id= '%s' and mpr.type = 'add' ''' % (obj.id))
                net = cr.dictfetchall()
                gro_val = {
                         'payroll_id':obj.id,
                         'rule_id':gross_rule[0],
                         'amount':gross[0]['gross'] - sum(deduction)
                         }
                sal.create(cr, uid, gro_val, context=context)
                gro_val = {
                         'payroll_id':obj.id,
                         'rule_id':net_rule[0],
                         'amount':net[0]['net'] - sum(deduction)
                         }
                sal.create(cr, uid, gro_val, context=context)
                if contract_id.avail_eos:          
                        print'DDDDDDDDDDDDDDDDDDDDDDDD' , contract_id.service_days          
                        val = {
                         'payroll_id':obj.id,
                         'rule_id':eos_rule[0],
                         'amount': round(((contract_id.gross * 0.6)/30.0) * contract_id.service_days)
                          }
                        sal.create(cr, uid, val, context=context)               
        else:
            raise osv.except_osv(_('Warning!'), _('First Update Employee Work Days'))            
        return True

    def confirm(self, cr, uid, ids, context=None):
        line_ids = []
        obj = self.browse(cr, uid, ids)
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        period_pool = self.pool.get('account.period')
        rule = self.pool.get('mline.payroll.rule')
        cont = self.pool.get('hr.contract')
        contract_id=cont.browse(cr, uid, obj.contract_id.id)        
        input_line=[line for line in obj.input_line_ids]        
        gross_rule = rule.search(cr, uid, [('code', '=', 'GROSS')], context=context)
        net_rule = rule.search(cr, uid, [('code', '=', 'NET')], context=context)
        loan_rule = rule.search(cr, uid, [('code', '=', 'LOAN')], context=context)
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')
        timenow = time.strftime('%Y-%m-%d')
        default_partner_id = obj.employee_id.address_home_id.id
        date = timenow
        search_periods = period_pool.find(cr, uid, date, context=context)
        period_id = search_periods[0]
        name = _('Payslip of %s') % (obj.employee_id.name)
        move = {
                'narration': name,
                'date': timenow,
                'ref': obj.name,
                'journal_id': obj.employee_id.journal_salary_id.id,
                'period_id': period_id,
            }
        move_id = move_pool.create(cr, uid, move, context=context)
        for line in obj.salary_line:
            if line.rule_id.code == 'EOS':
                contract_id.write({'prev_service_days':contract_id.service_days,'service_days': 0, 'avail_eos': False})
            if line.rule_id.id == net_rule[0]:
                debit_li = {
                         'move_id':move_id,
                         'name':line.rule_id.name,
                         'date': timenow,
                         'partner_id':default_partner_id,
                         'account_id':obj.employee_id.debit_account_id.id,
                         'journal_id':obj.employee_id.journal_salary_id.id,
                         'period_id':period_id,
                         'debit':0.0,
                         'credit':line.amount,
                 }
                move_line_pool.create(cr, uid, debit_li, context=context)
            if line.rule_id.id == net_rule[0]:
                credit_li = {
                         'move_id':move_id,
                         'name':line.rule_id.name,
                         'date': timenow,
                         'partner_id':default_partner_id,
                         'account_id':obj.employee_id.credit_account_id.id,
                         'journal_id':obj.employee_id.journal_salary_id.id,
                         'period_id':period_id,
                         'debit':line.amount,
                         'credit':0.0
                         }
                move_line_pool.create(cr, uid, credit_li, context=context)
                self.write(cr, uid, obj.id, {'move_id':move_id}, context=context)
        if input_line:
            for rec in input_line:                        
                new_amount=0.0
                new_term=0.0
                if contract_id.balance_amount > 0.0 and contract_id.no_month > 0:
                    new_adv=contract_id.loan_amount - (rec.amount+contract_id.total_paid_amount)
                    new_term=contract_id.no_month - 1
                    new_paid=contract_id.total_paid_amount + rec.amount
                    contract_id.write({'balance_amount': new_adv, 'no_month': new_term,'total_paid_amount':new_paid})                      
                if contract_id.balance_amount == 0.0 and contract_id.no_month == 0:
                    sal_id=self.pool.get('hr.contract.line').search(cr, uid, [('contract_id', '=', contract_id.id),('rule_id','=',loan_rule[0])], context=context)
                    if sal_id != []:
                        self.pool.get('hr.contract.line').unlink(cr,uid,sal_id[0])
                loan_obj=self.pool.get('hr.loan.line').browse(cr,uid,rec.loan_id.id)        
                loan_obj.write({'paid':True,'payroll_id':obj.id})                           
        
        return self.write(cr, uid, obj.id, {'state':'done'}, context=context)

    def cancel(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('account.move')
        obj = self.browse(cr, uid, ids)
        cont = self.pool.get('hr.contract')
        rule = self.pool.get('mline.payroll.rule')
        contract_id=cont.browse(cr, uid, obj.contract_id.id)        
        input_line=[line for line in obj.input_line_ids]
        deduction=[]        
        loan_rule = rule.search(cr, uid, [('code', '=', 'LOAN')], context=context)
        if obj.move_id.id:
            if obj.employee_id.journal_salary_id.update_posted is True:
                move_pool.button_cancel(cr, uid, [obj.move_id.id], context=context)
                move_pool.unlink(cr, uid, [obj.move_id.id], context=context)
            else:
                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.First you should set the journal to allow cancelling entries'))
        for line in obj.salary_line:
            if line.rule_id.code == 'EOS':
                contract_id.write({'service_days':contract_id.prev_service_days, 'avail_eos':True})        
        if input_line:
            for rec in input_line:                        
                new_amount=0.0
                new_term=0.0
                if contract_id.balance_amount >= 0.0 and contract_id.no_month >= 0:
                    new_adv=contract_id.balance_amount + (rec.amount)
                    new_term=contract_id.no_month+1
                    new_paid=contract_id.total_paid_amount - rec.amount
                    contract_id.write({'balance_amount': new_adv, 'no_month': new_term,'total_paid_amount':new_paid})                    
                    sal_id=self.pool.get('hr.contract.line').search(cr, uid, [('contract_id', '=', contract_id.id),('rule_id','=',loan_rule[0])], context=context)
                    if sal_id == []:
                        self.pool.get('hr.contract.line').create(cr,uid,{'contract_id':contract_id.id,'rule_id':loan_rule[0],'amount':-(rec.amount)})
                loan_obj=self.pool.get('hr.loan.line').browse(cr,uid,rec.loan_id.id)        
                print'DDDDDDDDDDDDDDDDDDDDDDDD',rec.loan_id.id
                loan_obj.write({'paid':False,'payroll_id':False})         
        return self.write(cr, uid, obj.id, {'state':'cancel'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        payroll = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in payroll:
            if s['state'] in ['draft', 'cancel']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You must cancel it before! delete Payslip'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

    def set_dtaft(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        work_line = self.pool.get('mline.working.line')
        pay_line = self.pool.get('mline.payroll.line')
        work_sr = work_line.search(cr, uid, [('payroll_id', '=', obj.id)], context=context)
        pay_sr = pay_line.search(cr, uid, [('payroll_id', '=', obj.id)], context=context)
        work_line.unlink(cr, uid, work_sr, context=context)
        pay_line.unlink(cr, uid, pay_sr, context=context)
        return self.write(cr, uid, obj.id, {'state':'draft'}, context=context)

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, payslip_type=False,context=None):
        values={'employee_id':False,'emp_id':False,'job_id':False,'contract_id':False,'branch_id':False,'date_from':False,'date_to':False}
        employee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        job_obj = self.pool.get('hr.job')
        if context is None:
            context = {}
        values = {}
        if employee_id:
            emp = employee_obj.browse(cr, uid, employee_id)
            cont = contract_obj.search(cr, uid, [('employee_id', '=', emp.id)], context=context)
            if not date_from:
                raise osv.except_osv(_('Error!'), _('Invalid Date Format!!!'))
            ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
            if cont:
                cont_br = contract_obj.browse(cr, uid, cont[0])
                values = {
                      'emp_id':emp.emp_code,
                      'job_id':emp.job_id.id,
                      'contract_id':cont_br.id,
                      'branch_id':emp.branch_id.id,
                      }
                return {'value': values}        
            else:
                return {'warning': {
                    'title': "Error!!!",
                    'message': "Please Create Employee related Internal Contract !!!",},
                   'value': {'employee_id':False,'emp_id':False,'job_id':False,'contract_id':False,'branch_id':False,'payslip_type':False,'date_to':False,'date_from':False}}
            if date_from and date_to and payslip_type:
                return self.onchange_date_from(cr,uid,ids,date_to,date_from,employee_id,payslip_type)
                return self.onchange_date_to(cr,uid,ids,date_to,date_from,employee_id,payslip_type) 
        return {'value': values}
mline_payroll()

class mline_working_line(osv.osv):
    _name = 'mline.working.line'
    _columns = {
        'payroll_id': fields.many2one('mline.payroll', 'Working'),
        'ot_hours': fields.float('OT Hours', readonly=True),
        'holiday_hours': fields.float('Holiday Hours', readonly=True),
        'leave_days': fields.float('Absent Days'),
        'present_days':fields.float('Present Days'),
        'stay_days':fields.float('Stay Days'),
             }

mline_working_line()

class mline_input_line(osv.osv):
    '''
    Payslip Input    '''

    _name = 'mline.input.line'
    _description = 'Payslip Input'
    _columns = {
        'name': fields.char('Description', required=True),
        'payslip_id': fields.many2one('mline.payroll', 'Pay Slip', required=True, ondelete='cascade', select=True),
        'sequence': fields.integer('Sequence', required=True, select=True),
        'code': fields.char('Code', size=52, required=True, help="The code that can be used in the salary rules"),
        'amount': fields.float('Amount', help="It is used in computation. For e.g. A rule for sales having 1% commission of basic salary for per product can defined in expression like result = inputs.SALEURO.amount * contract.wage*0.01."),
        'contract_id': fields.many2one('hr.contract', 'Contract', required=False, help="The contract for which applied this input"),
        'loan_id':fields.many2one('hr.loan', string="Loan Ref.")
    }
    _order = 'payslip_id, sequence'
    _defaults = {
        'sequence': 10,
        'amount': 0.0,
    }
class mline_payroll_line(osv.osv):
    _name = 'mline.payroll.line'
    _columns = {
        'payroll_id': fields.many2one('mline.payroll', 'Payroll'),
        'rule_id':fields.many2one('mline.payroll.rule', 'Rule'),
        'amount':fields.float('Amount', readonly=True, digits_compute= dp.get_precision('Payroll')),
        }
mline_payroll_line()

