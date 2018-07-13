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
from calendar import monthrange
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from openerp.exceptions import ValidationError,Warning

class hr_unmapped_attendance(osv.osv):
    _name='hr.unmapped.attendance'

    def _check_date(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        obj_task = self.browse(cr, uid, ids[0], context=context)
        start = obj_task.from_date or False
        end = obj_task.to_date or False
        if start and end :
            DATETIME_FORMAT = "%Y-%m-%d"  ## Set your date format here
            from_dt = datetime.strptime(start, DATETIME_FORMAT)
            to_dt = datetime.strptime(end, DATETIME_FORMAT)
            if to_dt < from_dt:
                return False
        return True
        
    _columns={
    'from_date':fields.date('Start Date',required=True),
    'to_date':fields.date('End Date',required=True),
    'employee_line_ids':fields.one2many('unmapped.employee.details','hr_unmapped_id','Employee'),
    'state':fields.selection([
            ('draft', 'Draft'),
            ('progress', 'Progress'),
            ('cancel', 'Cancel'),
            ('done', 'Done'),
            ],'Status',  select=True, readonly=True, copy=False), 
    }

    _defaults = {
        'state': 'draft',
        'from_date' : lambda *a:datetime.now().strftime('%Y-%m-01'), 
        'to_date' : lambda *a: str(datetime.now() + relativedelta(months=+1, day=1, days=-1))[:10],
         }    
    _constraints = [(_check_date, '\n Error !  \n To Date must be greater then From Date', ['from_date','to_date']),]
    
    #~ def onchange_from_dates(self,cr, uid, ids, from_date, context=context):
        #~ res={}
        #~ if  from_date:
            #~ print'DDDDDDDDDDDDDDDDDD',from_date
            #~ date = datetime.strptime(from_date,"%Y-%m-%d")
            #~ print'DDDDDDDDDDDDDDDDDDDDDDDDD',date
            #~ last_date=date.replace(day = calendar.monthrange(date.year, date.month)[1])
            #~ end_date=last_date.strftime("%Y-%m-%d")
            #~ print'$$$$$$$$$$$$$$$$$$$$$$$$$$$$',end_date
            #~ res['to_date'] = end_date
            #~ return {'value': res}            
    def generate(self, cr, uid, ids,context):
        obj = self.pool.get('hr.unmapped.attendance').browse(cr,uid,ids)
        total_days=[]
        public_holidays=[]
        start=parse(obj.from_date)
        stop=parse(obj.to_date)
        det = datetime.strptime(obj.from_date,"%Y-%m-%d")
        year_obj = det.strftime("%Y")
        month_obj = det.strftime("%m")
        cr.execute("""select ued.date from unmapped_employee_details ued where extract(month from date) = '%s' and  extract(year from date) = '%s'"""%(month_obj,year_obj))
        data=cr.dictfetchone()
        if data:
            raise osv.except_osv(_('Invalid Action!'), _('Absence List For The Given Period Already Generated!!!'))                      
        for dts in rrule(DAILY, dtstart=start, until=stop):         
            day_dates=dts.strftime("%Y-%m-%d")
            total_days.append(day_dates)  
        cr.execute('''select he.id as id from hr_employee he
                            join resource_resource  rr on (rr.id = he.resource_id)
                            where rr.active=True order by he.id asc''')
        emp_list=cr.dictfetchall()          
        cr.execute("""select date from public_holiday where date >='%s' and date <= '%s'  """%(obj.from_date,obj.to_date))
        leave = cr.dictfetchall()
        for l in leave:
             public_holidays.append(l['date'])
        for i in emp_list:
            present=[]
            present.extend(public_holidays)
            cr.execute("""select date  from hr_attendance
                               where employee_id = %d and date >='%s' and date <= '%s'  """%(i['id'],obj.from_date,obj.to_date))
            attd_list=cr.dictfetchall() 
            for a in attd_list:
                 present.append(a['date'])
            cr.execute("""select hh.employee_id,hh.date_from,hh.date_to from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hh.state='validate' 
                           and hh.type='remove' and hh.date_from >='%s' and hh.date_from <= '%s' """ % (i['id'],obj.from_date,obj.to_date))
            emps = cr.dictfetchall()
            if emps != []:
                for k in emps:
                    start=parse(k['date_from'])
                    stop=parse(k['date_to'])
                    for dts in rrule(DAILY, dtstart=start, until=stop): 
                            day_dates=dts.strftime("%Y-%m-%d")
                            present.append(day_dates)       
            not_mentioned=[]
            for j in total_days:
                if j not in present:
                    dates=datetime.strptime(j,"%Y-%m-%d")
                    dat= dates.strftime("%A")
                    if dat != 'Friday':
                          not_mentioned.append(j)
            for data in  not_mentioned:
                emp_obj=self.pool.get('hr.employee').browse(cr,uid,i['id'])
                vals={
                'hr_unmapped_id':obj.id,
                'employee_id':i['id'],
                'account_id':emp_obj.account_id.id,
                'branch_id':emp_obj.branch_id.id,
                'emp_code':emp_obj.emp_code,
                'date':data,
                }   
                y=self.pool.get('unmapped.employee.details').create(cr, uid, vals, context=context)                                      
        self.write(cr, uid, ids, {'state':'progress'},context=context)             
            
    def update(self, cr, uid, ids,context):
        obj = self.pool.get('hr.unmapped.attendance').browse(cr,uid,ids)
        public_holidays=[]
        cr.execute('''select he.id as id from hr_employee he
                            join resource_resource  rr on (rr.id = he.resource_id)
                            where rr.active=True order by he.id asc''')
        emp_list=cr.dictfetchall()
        cr.execute("""select date from public_holiday where date >='%s' and date <= '%s'  """%(obj.from_date,obj.to_date))
        leave = cr.dictfetchall()
        for l in leave:
             public_holidays.append(l['date'])
        for i in emp_list:
            cr.execute('''select hh.id as id
                       from hr_holidays hh
                       join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                       where hh.employee_id = '%s' and hhs.code='VL' and hh.type='add' '''%(i['id']))   
            hol_data=cr.dictfetchone()       
            present=[]
            present.extend(public_holidays)
            cr.execute("""select date  from hr_attendance 
                               where employee_id = %d and date >='%s' and date <= '%s'  """%(i['id'],obj.from_date,obj.to_date))
            attd_list=cr.dictfetchall() 
            for a in attd_list:
                #~ if hol_data:
                    #~ cr.execute('''update hr_holidays set number_of_days = number_of_days+0.0822,number_of_days_temp = number_of_days+0.0822 where id=%d and employee_id = %d'''%(hol_data['id'], i['id'])) 
                present.append(a['date'])
            cr.execute("""select hhs.code,hh.employee_id,hh.date_from,hh.date_to from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hh.state='validate' 
                           and hh.type='remove' and hh.date_from >='%s' and hh.date_from <= '%s' """ % (i['id'],obj.from_date,obj.to_date))
            emps = cr.dictfetchall()
            if emps != []:
                for k in emps:
                    start=parse(k['date_from'])
                    stop=parse(k['date_to'])
                    for dts in rrule(DAILY, dtstart=start, until=stop): 
                            day_dates=dts.strftime("%Y-%m-%d")
                            present.append(day_dates)  
                            if k['code'] != 'VL' and k['code'] != 'UL':
                                if hol_data:
                                    cr.execute('''update hr_holidays set number_of_days = number_of_days+0.0822,number_of_days_temp = number_of_days+0.0822 where id=%d and employee_id = %d'''%(hol_data['id'], i['id'])) 
            for val in present: 
                cr.execute(""" delete from unmapped_employee_details 
                where date = '%s' and employee_id = %d and hr_unmapped_id = %d """%(val,i['id'],obj.id))   
                
    def submit(self, cr, uid, ids,context):
          obj = self.pool.get('hr.unmapped.attendance').browse(cr,uid,ids)
          for rec in obj.employee_line_ids:
              self.pool.get('unmapped.employee.details').write(cr, uid, rec.id, {'is_validated':True},context=context) 
          self.write(cr, uid, ids, {'state':'done'},context=context)    
    
    def cancel(self, cr, uid, ids,context):
          self.write(cr, uid, ids, {'state':'cancel'},context=context)      
    
    def reset_to_draft(self, cr, uid, ids,context):
          obj = self.pool.get('hr.unmapped.attendance').browse(cr,uid,ids)
          cr.execute(""" delete from unmapped_employee_details 
                where hr_unmapped_id = %d """%(obj.id))     
          self.write(cr, uid, ids, {'state':'draft'},context=context)  

    def unlink(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids,context=context)
        for i in obj:
            if i.state == 'done':
                raise osv.except_osv(_('Invalid Action!'), _('Cannot Delete This Absence Entry Which In Done State!!!')) 
            else:
                cr.execute('''delete from hr_unmapped_attendance where id=%d''' %(i.id))                                                               
class unmapped_employee_details(osv.osv):
    _name='unmapped.employee.details'
    
    _columns={
       'hr_unmapped_id':fields.many2one('hr.unmapped.attendance'),
       'employee_id': fields.many2one('hr.employee', string="Employee"),
       'account_id': fields.many2one('account.analytic.account', 'Customer Contract', required=True),
       'branch_id':fields.many2one('company.branch', 'Sponsor ID', required=True),
       'emp_code':fields.char('Employee Code'),
       'date':fields.date('Absent Date'),
       'is_validated':fields.boolean('Validated'),
    }
    
    _defaults={
     'is_validated':False,
    }
    def unlink(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids,context=context)
        for i in obj:            
            cr.execute('''SELECT employee_id,date_from, date_to
                FROM mline_payroll
                WHERE '%s' between date_from::date and date_to::date and employee_id=%d'''%(i.date,i.employee_id.id)) 
            validate=cr.dictfetchall()
            if i.is_validated:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot Delete This Absence Entry!'))  
            elif validate!=[]:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete this Absence entry since payroll has been generated!'))
            
            else:
                cr.execute('''delete from unmapped_employee_details where id=%d''' %(i.id))    
