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
import time
import calendar
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from openerp.exceptions import ValidationError,Warning
from openerp.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT,
    drop_view_if_exists,
)
class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'
    _description = 'Hr attendance customized module'
    _order = "employee_id,date desc"
    _rec_name="date"

    def _get_current_sheets(self, cr, uid, branch_id, date=False,context=None):
        sheet_obj = self.pool['attendance.validation']
        if not date:
            date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        sheet_ids = sheet_obj.search(cr, uid,
            [('date_from', '<=', date),
             ('date_to', '>=', date),
             ('branch_id', '=', branch_id)],
            limit=1, context=context)
        return sheet_ids and sheet_ids[0] or False

    def _sheets(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for attendance in self.browse(cursor, user, ids, context=context):
            res[attendance.id] = self._get_current_sheets(
                    cursor, user, attendance.branch_id.id, attendance.date,
                    context=context)
        return res
    def _get_hr_attendance_sheet(self, cr, uid, ids, context=None):
        attendances_ids = []
        for ts in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                        SELECT a.id
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_from)s <= date_trunc('day', a.date)
                              AND %(date_to)s >= date_trunc('day', a.date)
                              AND %(branch_id)s = a.branch_id
                         GROUP BY a.id""", {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'branch_id': ts.branch_id.id,})
            attendances_ids.extend([row[0] for row in cr.fetchall()])
        return attendances_ids
    def _get_current_sheet(self, cr, uid, employee_id, date=False,context=None):
        sheet_obj = self.pool['hr_timesheet_sheet.sheet']
        if not date:
            date = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        sheet_ids = sheet_obj.search(cr, uid,
            [('date_from', '<=', date),
             ('date_to', '>=', date),
             ('employee_id', '=', employee_id)],
            limit=1, context=context)
        return sheet_ids and sheet_ids[0] or False

    def _sheet(self, cursor, user, ids, name, args, context=None):
        res = {}.fromkeys(ids, False)
        for attendance in self.browse(cursor, user, ids, context=context):
            res[attendance.id] = self._get_current_sheet(
                    cursor, user, attendance.employee_id.id, attendance.date,
                    context=context)
        return res
    def _get_hr_timesheet_sheet(self, cr, uid, ids, context=None):
        attendances_ids = []
        for ts in self.browse(cr, uid, ids, context=context):
            cr.execute("""
                        SELECT a.id
                          FROM hr_attendance a
                         INNER JOIN hr_employee e
                               INNER JOIN resource_resource r
                                       ON (e.resource_id = r.id)
                            ON (a.employee_id = e.id)
                         LEFT JOIN res_users u
                         ON r.user_id = u.id
                         LEFT JOIN res_partner p
                         ON u.partner_id = p.id
                         WHERE %(date_to)s >= date_trunc('day', a.date)
                              AND %(date_from)s <= date_trunc('day', a.date)
                              AND %(employee_id)s = a.employee_id
                         GROUP BY a.id""", {'date_from': ts.date_from,
                                            'date_to': ts.date_to,
                                            'employee_id': ts.employee_id.id,})
            attendances_ids.extend([row[0] for row in cr.fetchall()])
        return attendances_ids


    _columns = {
        'action': fields.selection([('sign_in', 'Sign In'), ('sign_out', 'Sign Out'), ('action','Action')], 'Action', required=False),
        'employee_id': fields.many2one('hr.employee', "Employee", select=True,required=True),
        #~ 'name':fields.many2one('hr.department', 'Department Name'),
        'emp_code':fields.char('Employee Code'),
        'user_id':fields.char('User Id'),
        'date':fields.date('Date', required=True),
        'sign_in':fields.float('Sign In (24 Hours)', required=True),
        'sign_out':fields.float('Sign Out (24 Hours)',required=True),
        'worked_hours':fields.float('Work Done in Day (Hour)', required=True),
        'remark':fields.text('Remark'),
        'status':fields.char('Status'),
        'validated':fields.char('Validate'),
        'branch_id':fields.many2one('company.branch', 'Sponsor ID'),
        #~ 'branch_id': fields.related('employee_id', 'branch_id', type="many2one", relation="company.branch", store=True, string="Sponsor ID"),
        'account_id': fields.many2one('account.analytic.account', 'Customer Contract'),
        'validation_id': fields.function(_sheets, string='Validation',
            type='many2one', relation='attendance.validation',
            store={
                      'attendance.validation': (_get_hr_attendance_sheet, ['branch_id', 'date_from', 'date_to'], 10),
                      'hr.attendance': (lambda self,cr,uid,ids,context=None: ids, ['employee_id', 'date', 'day'], 10),
                  },
            ),
        'sheet_id': fields.function(_sheet, string='Sheet',
            type='many2one', relation='hr_timesheet_sheet.sheet',
            store={
                      'hr_timesheet_sheet.sheet': (_get_hr_timesheet_sheet, ['employee_id', 'date_from', 'date_to'], 10),
                      'hr.attendance': (lambda self,cr,uid,ids,context=None: ids, ['employee_id', 'date', 'day'], 10),
                  },
            )  ,
        'state':fields.selection([
            ('draft', 'Draft'),
            ('validated', 'Validated'),
            ],'Status',  select=True, readonly=True, copy=False),
        'is_vacation_counted':fields.boolean('Vacation Counted'),
        'active':fields.boolean('Active'),
        'no_of_days':fields.integer('No.Of.Days'),
    }

    _defaults = {
        'date':datetime.now(),
        'validated':'No',
        'state': 'draft',
        'active':True,
        'is_vacation_counted':False,
        'no_of_days':1
    }

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
        return True

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

    def create(self, cr, uid, values, context=None):

        """ Override to avoid automatic logging of creation
            SELECT date_from, date_to
            FROM hr_holidays
            WHERE '2017-10-10' between date_from::date and date_to::date"""
        if context is None:
            context = {}
        employee_id = values.get('employee_id', False)
        if employee_id:
            emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context = context)
            if emp_obj.department_id.id:
                values.update({'name':emp_obj.department_id.id})
            if  emp_obj.emp_code:
                values.update({'emp_code':emp_obj.emp_code})
            if  emp_obj.branch_id:
                values.update({'branch_id':emp_obj.branch_id.id})
            if  emp_obj.account_id:
                values.update({'account_id':emp_obj.account_id.id})
        cr.execute("""select id from hr_holidays where '%s' between date_from::date and date_to::date and employee_id = %d """%(values.get('date'),employee_id))
        prev_hol=cr.dictfetchone()
        if prev_hol:
            raise osv.except_osv(_('Invalid Action!'), _('There Is A Holiday Request Entry For This Employee On This Date!!!'))
        cr.execute("""select id from hr_attendance where employee_id = %d and date= '%s' """%(employee_id, values.get('date')))
        prev_att=cr.dictfetchone()
        if prev_att:
            raise osv.except_osv(_('Invalid Action!'), _('Attendance Entry For This Employee For This Date Already Created!'))
        if values.get('date') > datetime.now().strftime('%Y-%m-%d'):
            raise osv.except_osv(_('Invalid Action!'), _('Attendance Date Cannot Be Greater Than Today Date'))
        det = values.get('date')
        year_obj, month_obj, day = (int(x) for x in det.split('-'))
        no_of_fridays=len([1 for i in calendar.monthcalendar(year_obj,month_obj) if i[4] != 0])
        public_holidays=[]
        cr.execute('''select date from public_holiday where to_char(date, 'MM')='%s'
                            and to_char(date, 'YYYY')='%s' ''' % (str(month_obj).zfill(2), str(year_obj)))
        leave = cr.dictfetchall()
        if leave:
            for i in leave:
                public_holidays.append(i['date'])
        if employee_id:
            contract=self.pool.get('hr.contract')
            contract_search=contract.search(cr, uid, [('employee_id', '=', employee_id)],order='id desc', context=context)
            if  not contract_search:
                raise osv.except_osv(_('Invalid Action!'), _('There Is No Employee Contract For This Employee Kindly Map A Employee Contract!'))
            contract_obj=contract.browse(cr, uid, contract_search[0], context=context)
            status=self.pool.get('hr.holidays.status')
            status_search=status.search(cr, uid, [('code', '=', 'VL')], context=context)
            status_obj=status.browse(cr, uid, status_search[0], context=context)
            if  contract_obj and status_obj:
                if contract_obj.trial_date_end < values.get('date'):
                    fri_leave=[]
                    cr.execute("""select hh.employee_id,hh.date_from,hh.date_to from hr_holidays hh
                                   join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                   where hh.employee_id = '%s' and hhs.code in ('UL','VL','LVL') 
                                   and hh.state = 'validate'
                                   and hh.type='remove' and to_char(hh.date_from, 'MM')='%s'
                                   and to_char(date_from, 'YYYY')='%s' """ %(employee_id, str(month_obj).zfill(2), str(year_obj)))
                    fri = cr.dictfetchall()
                    if fri != []:
                        for k in fri:
                            start=parse(k['date_from'])
                            stop=parse(k['date_to'])
                            for dts in rrule(DAILY, dtstart=start, until=stop):
                                day_dates=dts.strftime("%Y-%m-%d")
                                fri_leave.append(day_dates)

                    cr.execute('''select hh.id as id
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code='VL' and hh.type='add' '''%(employee_id))
                    hol_data=cr.dictfetchone()
                    cr.execute('''select id from hr_attendance where employee_id = %d and  to_char(date, 'MM')='%s'
                       and to_char(date, 'YYYY')='%s' ''' % (employee_id, str(month_obj).zfill(2), str(year_obj)))
                    is_first_day=cr.dictfetchall()
                    if  is_first_day != []:
                        if hol_data:
                            holiday_record=self.pool.get('hr.holidays').browse(cr,uid,hol_data['id'])
                            holiday_record.write({'number_of_days':holiday_record.number_of_days+0.0822,
                            'number_of_days_temp':holiday_record.number_of_days_temp+0.0822})
                        else:
                            vals={
                            'name':'Vacation Leave',
                            'type':'add',
                            'employee_id':employee_id,
                            'number_of_days':15.0822,
                            'number_of_days_temp':15.0822,
                            'holiday_type':'employee',
                            'holiday_status_id':status_obj.id,
                            }
                            self.pool.get('hr.holidays').create(cr, uid, vals, context=context)
                    else:
                        emp_leave=[]
                        cr.execute('''select hh.employee_id,hh.date_from,hh.date_to from hr_holidays hh
                                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                       where hh.employee_id = '%s' and hhs.code not in ('UL','VL','LVL') and hh.state='validate'
                                       and hh.type='remove' and to_char(hh.date_from, 'MM')='%s'
                                       and to_char(date_from, 'YYYY')='%s' ''' % (employee_id, str(month_obj).zfill(2), str(year_obj)))
                        emps = cr.dictfetchall()
                        if emps != []:
                            for k in emps:
                                start=parse(k['date_from'])
                                stop=parse(k['date_to'])
                                for dts in rrule(DAILY, dtstart=start, until=stop):
                                    day_dates=dts.strftime("%Y-%m-%d")
                                    if  day_dates not in public_holidays:
                                        emp_leave.append(day_dates)
                        #~ fri_leave=[]

                        val=(len(emp_leave)) * 0.0822
                        if hol_data:
                            holiday_record=self.pool.get('hr.holidays').browse(cr,uid,hol_data['id'])
                            holiday_record.write({'number_of_days':holiday_record.number_of_days+val+0.0822,
                            'number_of_days_temp':holiday_record.number_of_days_temp+val+0.0822})
                        else:
                            vals={
                            'name':'Vacation Leave',
                            'type':'add',
                            'employee_id':employee_id,
                            'number_of_days': 15+ val + 0.0822,
                            'number_of_days_temp': 15+ val + 0.0822,
                            'holiday_type':'employee',
                            'holiday_status_id':status_obj.id,
                            }
                            res=self.pool.get('hr.holidays').create(cr, uid, vals, context=context)
                    for dates in public_holidays:
                        if  dates not in fri_leave:
                            cr.execute("""select id from hr_attendance where employee_id = %d and date= '%s' """%(employee_id,dates))
                            prev_att=cr.dictfetchone()
                            emp_obj=self.pool.get('hr.employee').browse(cr,uid,employee_id)
                            if not prev_att:
                                cr.execute('''select max(date::date) as max_date from hr_attendance where employee_id = %d and  to_char(date, 'MM')='%s'
                                                   and to_char(date, 'YYYY')='%s' ''' % (employee_id, str(month_obj).zfill(2), str(year_obj)))
                                day_list=cr.dictfetchone()
                                if day_list['max_date']:
                                    if dates < day_list['max_date']:
                                        cr.execute("""insert into hr_attendance
                                        (name,employee_id,emp_code,branch_id,account_id,date,sign_in,sign_out,worked_hours,active,is_vacation_counted,create_uid,create_date,no_of_days)
                                        VALUES ('%s',%d,'%s','%s','%s','%s',0.00,0.00,0.00,False,True,'%s','%s',0)"""
                                        %(dates,employee_id,emp_obj.emp_code,emp_obj.branch_id.id,emp_obj.account_id.id,dates,uid,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                        record=self.pool.get('hr.holidays').search(cr,uid,[('holiday_status_id','=',status_obj.id,),('employee_id', '=', employee_id),('type', '=', 'add')], context=context)
                                        if record:
                                            holiday_record=self.pool.get('hr.holidays').browse(cr,uid,record[0])
                                            holiday_record.write({'number_of_days':holiday_record.number_of_days+0.0822,
                                            'number_of_days_temp':holiday_record.number_of_days_temp+0.0822})
        return super(hr_attendance, self).create(cr, uid, values, context=context)


    def on_change_to_get_employee_no(self, cr, uid, ids, employee_id, context = None):
        if not employee_id:
            return False
        res = {}
        if employee_id:
            emp_obj = self.pool.get('hr.employee').browse(cr, uid, employee_id, context = context)
            res['emp_code'] = emp_obj.emp_code
            res['branch_id'] = emp_obj.branch_id.id
            res['account_id'] = emp_obj.account_id.id
        return {'value': res}

    def unlink(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids,context=context)
        for i in obj:
            cr.execute('''SELECT employee_id,date_from, date_to
                FROM mline_payroll
                WHERE '%s' between date_from::date and date_to::date and employee_id=%d'''%(i.date,i.employee_id.id))
            validate=cr.dictfetchall()
            if i.state == 'validated':
                raise osv.except_osv(_('Invalid Action!'), _('Cannot Delete This Absence Entry!'))
            elif validate!=[]:
                 raise osv.except_osv(_('Invalid Action!'), _('Cannot delete this attendance entry since payroll has been generated!'))
            else:
                cr.execute('''select hh.id as id
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code='VL' and hh.type='add' '''%(i.employee_id.id))
                hol_data=cr.dictfetchone()
                if hol_data:
                    holiday_record=self.pool.get('hr.holidays').browse(cr,uid,hol_data['id'])
                    holiday_record.write({'number_of_days':holiday_record.number_of_days - 0.0822,
                    'number_of_days_temp':holiday_record.number_of_days_temp - 0.0822})
                cr.execute('''delete from hr_attendance where id=%d''' %(i.id))

class hr_holidays_status(osv.osv):
    _inherit='hr.holidays.status'

    _columns={
    'code':fields.char('Code'),
    }

class hr_holidays(osv.osv):
    _inherit='hr.holidays'

    _columns={
    'buffer_days':fields.float('Buffered Duration'),
    }
class attendance_validation(osv.osv):
    _name='attendance.validation'
    _columns={
        'branch_id':fields.many2one('company.branch', 'Sponsor ID', required=True,),
        'attendances_ids':fields.one2many('hr.attendance','validation_id',readonly=True),
        'date_from': fields.date('Date from', required=True),
        'date_to': fields.date('Date to', required=True),
        'state' : fields.selection([
            ('draft','Open'),
            ('confirm','Waiting Approval'),
            ('done','Approved'),
            ('cancel','Cancel')], 'Status', readonly=True,),
    }



    _defaults = {
        'date_from' : lambda *a:datetime.now().strftime('%Y-%m-01'),
        'date_to' : lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],
        'state': 'draft',
        }


    def button_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirm'})
    def approve(self, cr, uid, ids, context=None):
        obj = self.pool.get('attendance.validation').browse(cr,uid,ids)
        for rec in obj.attendances_ids:
            self.pool.get('hr.attendance').write(cr, uid, rec.id, {'state':'validated'},context=context)
        self.write(cr, uid, ids, {'state':'done'},context=context)
    def action_set_to_draft(self, cr, uid, ids, context=None):
        obj = self.pool.get('attendance.validation').browse(cr,uid,ids)
        for rec in obj.attendances_ids:
            self.pool.get('hr.attendance').write(cr, uid, rec.id, {'state':'draft'},context=context)
        self.write(cr, uid, ids, {'state':'draft'},context=context)
    def cancel(self, cr, uid, ids,context):
          self.write(cr, uid, ids, {'state':'cancel'},context=context)
    def unlink(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids,context=context)
        for i in obj:
            if i.state == 'done':
                raise osv.except_osv(_('Invalid Action!'), _('Cannot Delete This Entry Which In Done State!!!'))
            else:
                cr.execute('''delete from attendance_validation where id=%d''' %(i.id))

class hr_timesheet_sheet_sheet_day(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet.day"

    def init(self, cr):
        drop_view_if_exists(cr, 'hr_timesheet_sheet_sheet_day')
        cr.execute("""create or replace view hr_timesheet_sheet_sheet_day as
 SELECT
                id,
                name,
                sheet_id,
                total_timesheet,
                total_attendance,
                cast(round(cast(total_attendance - total_timesheet as Numeric),2) as Double Precision) AS total_difference
            FROM
                ((
                    SELECT
                        MAX(id) as id,
                        name,
                        sheet_id,
                        timezone,
                        SUM(total_timesheet) as total_timesheet,
                        CASE WHEN SUM(orphan_attendances) != 0
                            THEN (SUM(total_attendance) +
                                CASE WHEN current_date <> name
                                    THEN 1440
                                    ELSE (EXTRACT(hour FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC')) * 60) + EXTRACT(minute FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC'))
                                END
                                )
                            ELSE SUM(total_attendance)
                        END   as total_attendance
                    FROM
                        ((
                            select
                                min(hrt.id) as id,
                                p.tz as timezone,
                                l.date::date as name,
                                s.id as sheet_id,
                                sum(l.unit_amount) as total_timesheet,
                                0 as orphan_attendances,
                                0.0 as total_attendance
                            from
                                hr_analytic_timesheet hrt
                                JOIN account_analytic_line l ON l.id = hrt.line_id
                                LEFT JOIN hr_timesheet_sheet_sheet s ON s.id = hrt.sheet_id
                                JOIN hr_employee e ON s.employee_id = e.id
                                JOIN resource_resource r ON e.resource_id = r.id
                                LEFT JOIN res_users u ON r.user_id = u.id
                                LEFT JOIN res_partner p ON u.partner_id = p.id
                            group by l.date::date, s.id, timezone
                        ) union (
                            select
                                -min(a.id) as id,
                                p.tz as timezone,
                                (a.date AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date as name,
                                s.id as sheet_id,
                                0.0 as total_timesheet,
                                0.0 as orphan_attendances,
                                (a.worked_hours) as total_attendance
                            from
                                hr_attendance a
                                LEFT JOIN hr_timesheet_sheet_sheet s
                                ON s.id = a.sheet_id
                                JOIN hr_employee e
                                ON a.employee_id = e.id
                                JOIN resource_resource r
                                ON e.resource_id = r.id
                                LEFT JOIN res_users u
                                ON r.user_id = u.id
                                LEFT JOIN res_partner p
                                ON u.partner_id = p.id
                            group by (a.date AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date, s.id, p.tz,timezone,a.worked_hours
                        )) AS foo
                        GROUP BY name, sheet_id, timezone
                )) AS bar""")
