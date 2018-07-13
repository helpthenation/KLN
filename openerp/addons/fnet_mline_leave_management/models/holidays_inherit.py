import datetime
import math
import time
from datetime import date, timedelta
from operator import attrgetter
from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _
import calendar
from dateutil.relativedelta import relativedelta
class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not context.get('employee_id',False):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee            
            return super(hr_holidays_status, self).name_get(cr, uid, ids, context=context)

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            #~ print'RRRRRRRRRRRRRRRRRRRRRRRRRRRRR',context
            name = record.name
            if not record.limit:
                name = name + ('  (%g/%g)' % (record.leaves_taken or 0.0, record.max_leaves or 0.0))
            if context.get('employee_id'):
                 if record.code == 'MAL':
                    emp_obj=self.pool.get('hr.employee').browse(cr,uid,context['employee_id'])
                    if emp_obj.gender == 'female':
                        res.append((record.id, name))
                 elif record.code != 'MAL':
                    res.append((record.id, name))
            #~ else:
                #~ res.append((record.id, name))   
        return res

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"

    def _default_code(self,cr,uid,context=None):
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            a=self.pool.get('hr.employee').browse(cr,uid,emp_id,context=context)
            return a.emp_code
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            a=self.pool.get('hr.employee').browse(cr,uid,ids[0],context=context)
            return a.emp_code
        return False
    def _default_date_from(self,cr,uid,context=None):
        if context.get('default_type') == 'remove':
             return datetime.datetime.now().strftime('%Y-%m-%d 02:30:00')
        else:
            return False    
             
    def _default_doj(self,cr,uid,context=None):
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            a=self.pool.get('hr.employee').browse(cr,uid,emp_id,context=context)
            if a.contract_id.date_start:
                return a.contract_id.date_start
            else:
                return False    
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            a=self.pool.get('hr.employee').browse(cr,uid,ids[0],context=context)
            if a.contract_id.date_start:
                return a.contract_id.date_start
            else:
                return False
        return False            
    def _default_sponsor_id(self,cr,uid,context=None):
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            a=self.pool.get('hr.employee').browse(cr,uid,emp_id,context=context)
            return a.branch_id.id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            a=self.pool.get('hr.employee').browse(cr,uid,ids[0],context=context)
            return a.branch_id.id
        return False

    def _default_medical_leave_allocated(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        res=cr.dictfetchone()
        if res:
            return res['day']

    def _default_vacation_leave_allocated(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        res=cr.dictfetchone()
        if res:
            return res['day']

    def _default_maternity_leave_alocated(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        res=cr.dictfetchone()
        if res:
            return res['day']

    def _default_medical_leave_taken(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        #~ cr.execute('''select sum(hh.number_of_days) as day
                       #~ from hr_holidays hh
                       #~ join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       #~ where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        #~ allocate=cr.dictfetchone()
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        val=0.0
        if  taken['day']:
                val = taken['day']
        else:
            val = 0.0
        return val

    def _default_maternity_leave_taken(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        val=0.0
        if  taken['day']:
                val = taken['day']
        else:
            val = 0.0
        return val

    def _default_vacation_leave_taken(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        #~ cr.execute('''select sum(hh.number_of_days) as day
                       #~ from hr_holidays hh
                       #~ join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       #~ where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        #~ allocate=cr.dictfetchone()
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        val=0.0
        if  taken['day']:
                val = taken['day']
        else:
            val = 0.0
        return val

    def _default_leave_availed(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        #~ cr.execute('''select sum(hh.number_of_days) as day
                       #~ from hr_holidays hh
                       #~ join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       #~ where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        #~ allocate=cr.dictfetchone()
        cr.execute('''select max(date_to::date) as last_date from hr_holidays hh
                       where hh.employee_id = '%s' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        if  taken:
                val = taken['last_date']
        else:
            val = False
        return val

    def _default_as_on_date(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        as_on=False
        cr.execute('''select max(date::date) as last_date from hr_attendance hh
                       where hh.employee_id = '%s' '''%(ids[0]))
        attendance=cr.dictfetchone()
        leave={}
        if  attendance['last_date']:
            attend = datetime.datetime.strptime(attendance['last_date'], "%Y-%m-%d")
            attendance_month = attend.strftime("%m")
            attendance_year = attend.strftime("%Y")
            cr.execute('''select max(date_to::date) as last_date from hr_holidays hh
                           where hh.employee_id = '%s' and hh.state='validate' and hh.type='remove' and extract(month from date_to) = '%s' and extract(year from date_to)='%s' '''%(ids[0],attendance_month,attendance_year))
            leave=cr.dictfetchone()

        if leave.has_key('last_date'):
            if  leave['last_date'] and attendance['last_date']:
                DATE_FORMAT = "%Y-%m-%d"
                leave_dt = datetime.datetime.strptime(leave['last_date'], DATE_FORMAT)
                attendance_dt = datetime.datetime.strptime(attendance['last_date'], DATE_FORMAT)
                if leave_dt >= attendance_dt:
                    as_on=leave['last_date']
                else:
                    as_on=attendance['last_date']
            elif leave['last_date']:
                as_on=leave['last_date']
            elif attendance['last_date']:
                as_on=attendance['last_date']
        else:
            if attendance['last_date']:
                as_on=attendance['last_date']

        return as_on
    def _default_stay_leave_taken(self,cr,uid,context=None):
         ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
         cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='SL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))

         taken=cr.dictfetchone()
         val=0.0
         if  taken['day']:
             val = taken['day']
         else:
             val = 0.0
         return val

    def _default_absent_leave_taken(self,cr,uid,context=None):
         ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
         cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='UL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))

         taken=cr.dictfetchone()
         val=0.0
         if  taken['day']:
             val = taken['day']
         else:
             val = 0.0
         return val

    def _default_medical_leave_remaining(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        res=cr.dictfetchone()
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and  hh.state='validate'  and hh.type='remove' '''%(ids[0]))
        c=cr.dictfetchone()
        if res and c['day']:
            d=res['day']+c['day']
            return d

    def _default_maternity_leave_remaining(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        r=cr.dictfetchone()
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        if r and taken['day']:
            a=r['day']+taken['day']
            return a

    def _default_vacation_leave_remaining(self,cr,uid,context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(ids[0]))
        res=cr.dictfetchone()
        cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='remove' '''%(ids[0]))
        taken=cr.dictfetchone()
        if res and taken['day']:
            b=res['day']+taken['day']
            return b

    _check_vacation_holidays = lambda self, cr, uid, ids, context=None: self.check_vacation_holidays(cr, uid, ids, context=context)
    _columns = {
           'code': fields.char('Employee Code'),
           'sponsor_id':fields.many2one('company.branch','Sponsor ID'),
           'no_of_working_days':fields.float('No.of.Working Days'),
           'no_of_present_days':fields.float('No.of.Present Days'),
           'no_of_absent_days':fields.float('No.Of.Absent Days'),
           'medical_leave_taken':fields.float('Medical Leave  Taken'),
           'medical_leave_allocated':fields.float('Medical Leave Allocated'),
           'medical_leave_remaining':fields.float('Medical Leave Remaining Days'),
           'vacation_leave_remaining':fields.float('Vacation Leave Remaining Days'),
           'vacation_leave_taken':fields.float('Vaction Leave Taken'),
           'vacation_leave_allocated':fields.float('Vaction Leave Allocated'),
           'maternity_leave_taken':fields.float('Maternity Leave  Taken'),
           'maternity_leave_remaining':fields.float('Maternity Leave  Remaining Days'),
           'maternity_leave_alocated':fields.float('Maternity Leave Allocated '),
           'last_leave_availed':fields.date('Last Leave Availed'),
           'as_on_date':fields.date('As On Date'),
           'stay_leave':fields.float('Stay Leave'),
           'absent_days':fields.float('Absent Day'),
           'doj':fields.date('Date Of Joining',readonly=True)
            }


    _defaults = {
           'code': _default_code,
           'sponsor_id':_default_sponsor_id,
           'medical_leave_allocated':_default_medical_leave_allocated,
           'vacation_leave_allocated':_default_vacation_leave_allocated,
           'maternity_leave_alocated':_default_maternity_leave_alocated,
           'medical_leave_taken':_default_medical_leave_taken,
           'maternity_leave_taken':_default_maternity_leave_taken,
           'vacation_leave_taken':_default_vacation_leave_taken,
           'medical_leave_remaining':_default_medical_leave_remaining,
           'maternity_leave_remaining':_default_maternity_leave_remaining,
           'vacation_leave_taken':_default_vacation_leave_remaining,
           'last_leave_availed':_default_leave_availed,
           'as_on_date':_default_as_on_date,
           'stay_leave':_default_stay_leave_taken,
           'absent_days':_default_absent_leave_taken,
           'date_from':_default_date_from,
           'doj':_default_doj,
    }
    _constraints = [
        (_check_vacation_holidays, '\n', ['state','number_of_days_temp','buffered_count'])
    ]

    def onchange_employee(self, cr, uid, ids, employee_id):
        result = {'value': {
                               'department_id': False,
                               'code': None,
                               'sponsor_id':False,
                               'medical_leave_allocated':0.0,
                               'vacation_leave_allocated':0.0,
                               'maternity_leave_alocated':0.0,
                               'maternity_leave_remaining':0.0,
                               'medical_leave_taken':0.0,
                               'medical_leave_remaining':0.0,
                               'vacation_leave_remaining':0.0,
                               'maternity_leave_taken':0.0,
                               'vacation_leave_taken':0.0,
                               'last_leave_availed':False,
                               'as_on_date':False,
                               'holiday_status_id':False,
                               'stay_leave':0.0,
                               'absent_days':0.0,
                               'doj':False,
                               }}
        ml_all=0.0
        mal_all=0.0
        vl_all=0.0
        vl_tak=0.0
        ml_tak=0.0
        mal_tak=0.0
        last_leave=False
        as_on=False
        stay=0.0
        abst=0.0
        ml_remain=0.0
        d=0.0
        a=0.0
        b=0.0
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='add' '''%(employee_id))
            ml_allocate=cr.dictfetchone()
            if ml_allocate:
                ml_all = ml_allocate['day']
            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='add' '''%(employee_id))
            mal_allocate=cr.dictfetchone()
            if mal_allocate:
                mal_all = mal_allocate['day']
            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(employee_id))
            vl_allocate=cr.dictfetchone()
            if vl_allocate:
                vl_all = vl_allocate['day']
            cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            vl_taken=cr.dictfetchone()
            if vl_taken['day']:
                vl_tak = vl_taken['day']
            cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            ml_taken=cr.dictfetchone()
            if ml_taken['day']:
                ml_tak = ml_taken['day']
            cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            mal_taken=cr.dictfetchone()
            if mal_taken['day']:
                mal_tak = mal_taken['day']
            cr.execute('''select max(date_to::date) as last_date from hr_holidays hh
                           where hh.employee_id = '%s' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            taken=cr.dictfetchone()
            if  taken:
                    last_leave = taken['last_date']
            cr.execute('''select max(date::date) as last_date from hr_attendance hh
                           where hh.employee_id = '%s' '''%(employee_id))
            attendance=cr.dictfetchone()
            leave={}
            if  attendance['last_date']:
                attend = datetime.datetime.strptime(attendance['last_date'], "%Y-%m-%d")
                attendance_month = attend.strftime("%m")
                attendance_year = attend.strftime("%Y")
                cr.execute('''select max(date_to::date) as last_date from hr_holidays hh
                               where hh.employee_id = '%s' and hh.state='validate' and hh.type='remove' and extract(month from date_to) = '%s' and extract(year from date_to)='%s' '''%(employee_id,attendance_month,attendance_year))
                leave=cr.dictfetchone()
            if leave.has_key('last_date'):
                if  leave['last_date'] and attendance['last_date']:
                    DATE_FORMAT = "%Y-%m-%d"
                    leave_dt = datetime.datetime.strptime(leave['last_date'], DATE_FORMAT)
                    attendance_dt = datetime.datetime.strptime(attendance['last_date'], DATE_FORMAT)
                    if leave_dt >= attendance_dt:
                        as_on=leave['last_date']
                    else:
                        as_on=attendance['last_date']
                elif leave['last_date']:
                    as_on=leave['last_date']
                elif attendance['last_date']:
                    as_on=attendance['last_date']
            else:
                if attendance['last_date']:
                    as_on=attendance['last_date']
            cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='SL' and hh.state='validate' and hh.type='remove' '''%(employee_id))

            stay_count=cr.dictfetchone()
            if  stay_count['day']:
                 stay = stay_count['day']
            cr.execute('''select sum(hh.number_of_days) as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='UL' and hh.state='validate' and hh.type='remove' '''%(employee_id))

            ul_count=cr.dictfetchone()
            if  ul_count['day']:
                 abst = ul_count['day']

            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code ='ML' and hh.state='validate' and hh.type='add' '''%(employee_id))
            res=cr.dictfetchone()
            cr.execute('''select sum(hh.number_of_days) as day
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code ='ML' and  hh.state='validate'  and hh.type='remove' '''%(employee_id))
            c=cr.dictfetchone()
            if res and c['day']:
                d=res['day']+c['day']

            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='add' '''%(employee_id))
            r=cr.dictfetchone()
            cr.execute('''select sum(hh.number_of_days) as day
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code ='MAL' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            taken=cr.dictfetchone()
            if r and taken['day']:
                a=r['day']+taken['day']

            cr.execute('''select hh.number_of_days as day
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(employee_id))
            res=cr.dictfetchone()
            cr.execute('''select sum(hh.number_of_days) as day
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='remove' '''%(employee_id))
            taken=cr.dictfetchone()
            if res and taken['day']:
                b=res['day']+(taken['day'])
            join_date=False
            if employee.contract_id.date_start:
                join_date=employee.contract_id.date_start
            result['value'] = {'department_id': employee.department_id.id,
                               'code': employee.emp_code,
                               'sponsor_id': employee.branch_id.id,
                               'medical_leave_allocated':ml_all,
                               'vacation_leave_allocated':vl_all,
                               'maternity_leave_alocated':mal_all,
                               'medical_leave_taken':ml_tak,
                               'maternity_leave_taken':mal_tak,
                               'vacation_leave_taken':vl_tak,
                               'last_leave_availed':last_leave,
                                'as_on_date':as_on,
                                'holiday_status_id':False,
                                'stay_leave':stay,
                                'absent_days':abst,
                                'medical_leave_remaining':d,
                                'maternity_leave_remaining':a,
                                'vacation_leave_remaining':b,
                                'doj':join_date
                               }
        return result

    def _get_number_of_days(self,cr,date_from, date_to,emp_id):
        """Returns a float equals to the timedelta between two dates given as string."""
        diff_day=0.0
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        DATE_FORMAT = "%Y-%m-%d"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        from_date = from_dt.strftime(DATE_FORMAT)
        to_date = to_dt.strftime(DATE_FORMAT)
        cr.execute("""select date from hr_attendance where date >= '%s' and date <= '%s' and employee_id =%d order by date::date asc"""%(from_date,to_date,emp_id))
        attendance=cr.dictfetchone()
        if attendance:
            raise osv.except_osv(_('Warning!'),_('You cannot create a leave for %s which is already present attendance')%(attendance['date']))
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day

    def onchange_date_from(self, cr, uid, ids, date_to, date_from,employee_id):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

            #~ return {'warning': {
                    #~ 'title': "Warning!!!",
                    #~ 'message': "The start date must be anterior to the end date.",},
                   #~ 'value': {'date_from':False,'holiday_status_id':False,'date_to':False}}
            #~ raise osv.except_osv(_('Warning!'),_(''))

        result = {'value': {}}
        obj = self.pool.get('hr.holidays').browse(cr,uid,ids)
        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=9)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr,date_from, date_to,employee_id)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from,employee_id):
        """
        Update the number_of_days.
        """

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            return {'warning': {
                    'title': "Warning!!!",
                    'message': "The start date must be anterior to the end date.",},
                   'value': {'date_from':False,'holiday_status_id':False,'date_to':False}}
            raise osv.except_osv(_('Warning!'),_('The start date must be anterior to the end date.'))

        result = {'value': {}}
        obj = self.pool.get('hr.holidays').browse(cr,uid,ids)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(cr,date_from, date_to,employee_id)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day))+1
        else:
            result['value']['number_of_days_temp'] = 0

        return result
        
    def add_follower(self, cr, uid, ids, employee_id, context=None):
        employee = self.pool['hr.employee'].browse(cr, uid, employee_id, context=context)
        if employee.user_id:
            self.message_subscribe(cr, uid, ids, [employee.user_id.partner_id.id], context=context)
            
    def create(self, cr, uid, values, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        employee_id = values.get('employee_id', False)
        context = dict(context, mail_create_nolog=True, mail_create_nosubscribe=True)
        if values.get('state') and values['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % values.get('state'))
        if values.get('type') == 'remove':
            if values.get('date_from') and values.get('date_to'):
                DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
                DATE_FORMAT = "%Y-%m-%d"
                from_dt = datetime.datetime.strptime(values.get('date_from'), DATETIME_FORMAT)
                to_dt = datetime.datetime.strptime(values.get('date_to'), DATETIME_FORMAT)
                from_date = from_dt.strftime(DATE_FORMAT)
                to_date = to_dt.strftime(DATE_FORMAT)
                cr.execute("""select date from hr_attendance where date >= '%s' and date <= '%s' and employee_id =%d order by date::date asc"""%(from_date,to_date,employee_id))
                attendance=cr.dictfetchone()
                if attendance:
                    raise osv.except_osv(_('Warning!'),_('You cannot create a leave for %s which is already present attendance')%(attendance['date']))
        hr_holiday_id = super(hr_holidays, self).create(cr, uid, values, context=context)
        self.add_follower(cr, uid, [hr_holiday_id], employee_id, context=context)
        return hr_holiday_id

    def write(self, cr, uid, ids, vals, context=None):
        obj=self.browse(cr,uid,ids)
        employee_id = vals.get('employee_id', False)
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        DATE_FORMAT = "%Y-%m-%d"
        if obj.type == 'remove':
            date_from= vals.get('date_from') or obj.date_from
            date_to= vals.get('date_to') or obj.date_to
            emp_id= vals.get('employee_id') or obj.employee_id.id
            if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
                raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            from_date = from_dt.strftime(DATE_FORMAT)
            to_date = to_dt.strftime(DATE_FORMAT)
            cr.execute("""select date from hr_attendance where date >= '%s' and date <= '%s' and employee_id =%d order by date::date asc"""%(from_date,to_date,emp_id))
            attendance=cr.dictfetchone()
            if attendance:
                raise osv.except_osv(_('Warning!'),_('You cannot create a leave for %s which is already present attendance')%(attendance['date']))
        hr_holiday_id = super(hr_holidays, self).write(cr, uid, ids, vals, context=context)
        self.add_follower(cr, uid, ids, employee_id, context=context)
        return hr_holiday_id

    def check_holidays(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.is_vaction_leave == False:
                if record.holiday_type != 'employee' or record.type != 'remove' or not record.employee_id or record.holiday_status_id.limit:
                    continue
                leave_days = self.pool.get('hr.holidays.status').get_days(cr, uid, [record.holiday_status_id.id], record.employee_id.id, context=context)[record.holiday_status_id.id]
                if float_compare(leave_days['remaining_leaves'], 0, precision_digits=2) == -1 or \
                  float_compare(leave_days['virtual_remaining_leaves'], 0, precision_digits=2) == -1:
                    # Raising a warning gives a more user-friendly feedback than the default constraint error
                    raise Warning(_('The number of remaining leaves is not sufficient for this leave type.\n'
                                    'Please verify also the leaves waiting for validation.'))
        return True

    def check_vacation_holidays(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.is_vaction_leave:
                if record.number_of_days_temp > record.buffered_count:
                    raise Warning(_('The number of vacation leaves is not sufficient for this leave type.'))
        return True


    def onchange_holidays_status_id(self, cr, uid, ids, holiday_status_id,employee_id,date_from,date_to,type):
        if holiday_status_id:
            holiday_status_obj=self.pool.get('hr.holidays.status').browse(cr,uid,holiday_status_id)
            if holiday_status_obj.code == 'VL' and type == 'remove':
                if employee_id and date_from:
                    employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
                    cr.execute('''select hh.employee_id,hhs.id as id,max(hh.date_from::date) as date_from ,
                    max(hh.date_to::date) as date_to
                                        from hr_holidays hh
                                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                        where hh.employee_id = '%s' and hh.type='remove' and hhs.code ='VL'  
                                        group by hh.id,hh.date_from,hh.date_to,hhs.id
                                        order by hh.date_to::date desc
                                        ''' % (employee_id))
                    prev_rec = cr.dictfetchone() 
                    if  prev_rec:                           
                        if  prev_rec['employee_id'] and prev_rec['date_from'] and prev_rec['date_to'] and prev_rec['id']:
                            cr.execute("""select rejoining_date from rejoin_detail rd
                                                join hr_holidays_status hhs on (hhs.id = rd.type)
                                                join hr_contract hc on (hc.id = rd.resumption_id)
                                                where rd.start_date='%s' and rd.end_date='%s' 
                                                and hhs.id = %d and hc.employee_id = %d"""%(prev_rec['date_from'] , prev_rec['date_to'] , prev_rec['id'],prev_rec['employee_id'])) 
                            rejoin=cr.dictfetchone()
                            if rejoin:
                                if rejoin['rejoining_date'] > date_from:
                                    return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "The start date must be greater to the rejoing date %s."%(rejoin['rejoining_date'])},
                                                'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                               }        
                                    #~ raise Warning("The start date must be greater to the rejoing date %s." %(rejoin['rejoining_date']))                 
                            elif prev_rec['date_to'] > date_from:
                                res = {'warning': {
                                            'title': "Warning!!!",
                                            'message': "There is no Rejoin Date For The Last Vaction Leave %s."%(prev_rec['date_to'])},
                                            'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                           }     
                                return res  
                            else:   
                                return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "There Is No Rejoing Date For Previous Vacation Leave Availed %s To %s. \n Kindly Give Rejoin Date!!!"%(prev_rec['date_from'] , prev_rec['date_to'])},
                                                'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                               }   
                                                   
            elif holiday_status_obj.code == 'LVL' and type == 'remove':  
                if employee_id and date_from and date_to:
                    employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
                    start_date = datetime.datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
                    to_date = datetime.datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
                    six_months = datetime.datetime.strptime(date_from,'%Y-%m-%d %H:%M:%S') + relativedelta(days=+149,hours=15)  
                    trial_end=(six_months).strftime('%Y-%m-%d')   
                    cr.execute('''select hh.employee_id,hhs.id as id,max(hh.date_from::date) as date_from ,
                                        max(hh.date_to::date) as date_to
                                        from hr_holidays hh
                                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                        where hh.employee_id = '%s' and hh.type='remove' and hhs.code ='LVL' 
                                        group by hh.id,hh.date_from,hh.date_to,hhs.id
                                        order by hh.date_to::date desc
                                        ''' % (employee_id))
                    prev_rec = cr.dictfetchone() 
                    if  prev_rec:                           
                        if  prev_rec['employee_id'] and prev_rec['date_from'] and prev_rec['date_to'] and prev_rec['id']:
                            cr.execute("""select rejoining_date from rejoin_detail rd
                                                join hr_holidays_status hhs on (hhs.id = rd.type)
                                                join hr_contract hc on (hc.id = rd.resumption_id)
                                                where rd.start_date='%s' and rd.end_date='%s' 
                                                and hhs.id = %d and hc.employee_id = %d"""%(prev_rec['date_from'] , prev_rec['date_to'] , prev_rec['id'],prev_rec['employee_id'])) 
                            rejoin=cr.dictfetchone()
                            if rejoin:
                                if rejoin['rejoining_date'] > date_from:
                                    return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "The start date must be greater to the rejoing date %s."%(rejoin['rejoining_date'])},
                                                'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                               }        
                                    #~ raise Warning("The start date must be greater to the rejoing date %s." %(rejoin['rejoining_date']))                 
                            elif prev_rec['date_to'] > date_from:
                                res = {'warning': {
                                            'title': "Warning!!!",
                                            'message': "There is no Rejoin Date For The Last Long Vaction Leave %s."%(prev_rec['date_to'])},
                                            'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                           }     
                                return res  
                            else:   
                                return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "There Is No Rejoing Date For Previous Long Vacation Leave Availed %s To %s. \n Kindly Give Rejoin Date!!!"%(prev_rec['date_from'] , prev_rec['date_to'])},
                                                'value': {
                                                            'holiday_status_id':False,
                                                            #~ 'date_from':False,
                                                            #~ 'date_to':False,
                                                } 
                                               }             
                                                     
                    if employee_id and trial_end:
                        if  employee.visa_expiry:
                            before_30day = datetime.datetime.strptime(employee.visa_expiry,'%Y-%m-%d') + relativedelta(days=-30)
                            if trial_end == to_date.strftime('%Y-%m-%d'):
                                pass                                
                            elif before_30day.strftime('%Y-%m-%d') > trial_end:
                                return  {
                                            #~ 'warning': {
                                                    #~ 'title': "Warning!!!",
                                                    #~ 'message': "Sorry!!! You Can't Allocated 150 More Than Days."},
                                            'value':{'date_to':six_months,
                                            'holiday_status_id':False
                                            }      
                                            }                                     
                            
                            elif  before_30day.strftime('%Y-%m-%d') == to_date.strftime('%Y-%m-%d'):
                                pass                            
                            elif  before_30day.strftime('%Y-%m-%d') < trial_end: 
                                b4_date=before_30day.strftime('%Y-%m-%d')+' 17:00:00'                              
                                return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "You Can't Allocated More Days Then Visa Expiry %s ."%(employee.visa_expiry)},
                                                'value':{
                                                'date_to':datetime.datetime.strptime(b4_date, "%Y-%m-%d %H:%M:%S"),
                                                'holiday_status_id':False
                                                }
                                                } 
                            elif start_date  and to_date:
                                if (to_date-start_date).days+1 > 150:
                                    return {'warning': {
                                                    'title': "Warning!!!",
                                                    'message': "Sorry!!! You Can't Allocated 150 More Than Days."},
                                                    'value':{
                                                    'date_to':False,
                                                    'holiday_status_id':False
                                                    }
                                                    }                                   
            elif holiday_status_obj.code == 'MAL' and type=='remove':
                if employee_id and date_from:
                    employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
                    if employee.contract_id.date_start:
                        req_date = datetime.datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
                        request_date=req_date.strftime('%Y-%m-%d')
                        after_year = datetime.datetime.strptime(employee.contract_id.date_start,'%Y-%m-%d') + relativedelta(years=1)                 
                        if request_date < after_year.strftime('%Y-%m-%d'):                              
                                return {'warning': {
                                                'title': "Warning!!!",
                                                'message': "You Can't Avail Maternity Leave Before One Year From Date Of Join!!!."},
                                                'value':
                                                    {'holiday_status_id':False}
                                               }                           



