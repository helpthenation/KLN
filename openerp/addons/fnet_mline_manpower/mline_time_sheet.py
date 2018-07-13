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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime

import datetime
from datetime import date
from hours import float_time
from leave_day import leave_count
#~ from openerp import models, fields, api, _
import collections

class hr_timesheet_sheet_inherit(osv.osv):
    _inherit = 'hr_timesheet_sheet.sheet'

    _columns = {

        'sheet_line': fields.one2many('hr.sheet.line', 'sheet_id', 'Timesheet'),
        'total_hours': fields.float('Total Hours', readonly=True),
        'validated':fields.boolean('Validated'),
        'normal_hours': fields.float('Normal Hours', readonly=True),
        'ot_hours': fields.float('Overtime Hours', readonly=True),
        'holiday_hours': fields.float('Holiday Hours', readonly=True),
               }

    def unlink(self, cr, uid, ids, context=None):
        if len(ids) > 1:
            toremove = []
            for obje in ids:
                obj = self.browse(cr, uid, obje)
                for line in obj.sheet_line:
                    toremove.append(line.id)
            self.pool.get('hr.sheet.line').unlink(cr, uid, toremove, context=context)
        else:
            toremove = []
            obj = self.browse(cr, uid, ids)
            for line in obj.sheet_line:
                    toremove.append(line.id)
            self.pool.get('hr.sheet.line').unlink(cr, uid, toremove, context=context)
        return super(hr_timesheet_sheet_inherit, self).unlink(cr, uid, ids, context=context)


    def button_confirm(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        if obj.validated is False:
            raise osv.except_osv(_('Invalid Action!'), _('Please validate the Timesheet,then send to Manager!'))
        else:
            for sheet in self.browse(cr, uid, ids, context=context):
                if sheet.employee_id and sheet.employee_id.parent_id and sheet.employee_id.parent_id.user_id:
                    self.message_subscribe_users(cr, uid, [sheet.id], user_ids=[sheet.employee_id.parent_id.user_id.id], context=context)
                self.check_employee_attendance_state(cr, uid, sheet.id, context=context)
                di = sheet.user_id.company_id.timesheet_max_difference
                if (abs(sheet.total_difference) < di) or not di:
                    sheet.signal_workflow('confirm')
                else:
                    raise osv.except_osv(_('Warning!'), _('Please verify that the total difference of the sheet is lower than %.2f.') %(di,))
        return True

    def cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        self.write(cr, uid, ids, {'total_hours':0.00, 'normal_hours':0.00, 'ot_hours':0.00, 'holiday_hours':0.00, 'validated':0}, context=context)
        toremove = []
        for line in obj.sheet_line:
            toremove.append(line.id)
        self.pool.get('hr.sheet.line').unlink(cr, uid, toremove, context=context)
        return self.signal_workflow(cr, uid, ids, 'cancel')
        
    def _public_holiday(self, cr, uid, obj, context=None):
        det =  obj.date_from
        res = []
        year_obj, month_obj, day = (int(x) for x in det.split('-'))
        pub_hol = self.pool.get('public.holiday').search(cr, uid, [('id', '>=', 1)], context=context)
        for line in self.pool.get('public.holiday').browse(cr, uid, pub_hol):
            dete = line.date
            year, month, day = (int(x) for x in dete.split('-'))
            if year_obj == year and month_obj == month:
                res.append(str(dete))
        return tuple(res)
    
    def validate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        holiday_leave = leave_count(obj.date_from, obj.date_to)
        count = 0.00
        line_sr = self.pool.get('hr.sheet.line').search(cr, uid, [('sheet_id', '=', obj.id)], context=context)
        if line_sr:
            raise osv.except_osv(_('Error!'), _('Time sheet already validated. Please send to Manager!'))
        emp_hour = self.pool.get('hr.employee').browse(cr, uid, obj.employee_id.id)
        public_holi = self._public_holiday(cr, uid, obj, context=context)
        leace_days = []
        #~ cr.execute(''' select hel.name from employee_leave_rel er join hr_employee_leave hel on (hel.id = er.leave_id) where emp_id = '%s' ''' % (obj.employee_id.id))
        #~ ll = cr.fetchall()
        cr.execute(''' select 
                            distinct hel.name
                        from hr_timesheet_sheet_sheet htss
                        join hr_analytic_timesheet hat on (hat.sheet_id = htss.id)
                        join account_analytic_line aal on (aal.id = hat.line_id)
                        join employee_analytic_rel ear on (ear.account_id = aal.account_id)
                        join hr_employee_leave hel on (hel.id = ear.leave_id)
                        where htss.id = '%s' ''' % (obj.id))
        ll = cr.fetchall()
        for l in ll:
            leace_days.append(str(l[0]))
        print leace_days, "GGGGGGGGGGGGGGGGG"
        #~ leace_days = [line.name for line in emp_hour.leave_line]
        #~ print leace_days, "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQqq"
        for line in obj.timesheet_ids:
            acc_sr = self.pool.get('time.sheet.account').search(cr, uid, [('account_id', '=', line.account_id.id), ('date_from', '=', obj.date_from)], context=context)
            if acc_sr:
                acc_obj = self.pool.get('time.sheet.account').browse(cr, uid, acc_sr[0])
                line_normal = 0.00
                line_ot = 0.00
                line_holiday = 0.00
                dt = line.date
                year, month, day = (int(x) for x in dt.split('-'))
                ans = datetime.date(year, month, day)
                if ans.strftime("%A") in tuple(leace_days):
                    print dt, "&&&&&&&&&&"
                    count += 1
                    line_holiday = line.unit_amount
                    line_normal = 0.00
                    line_ot = 0.00
                else:
                    if dt in public_holi:
                        print dt, "PUBLIC"
                        line_holiday = line.unit_amount
                        line_normal = 0.00
                        line_ot = 0.00
                    else:
                        if line.unit_amount > emp_hour.hours:
                            if emp_hour.ot_hours > 0.00:
                                line_normal = emp_hour.hours
                                line_bal = line.unit_amount - line_normal
                                if line_bal > emp_hour.ot_hours:
                                    line_ot = emp_hour.ot_hours
                                    tot_holl = line_normal + line_ot
                                    hol = line.unit_amount - tot_holl
                                    line_holiday += hol
                                else:
                                     line_ot = line_bal
                            else:
                                 line_ot = line.unit_amount - emp_hour.hours
                                 line_normal = emp_hour.hours
                        else:
                            line_normal = line.unit_amount
                vals = {
                      'sheet_id':obj.id,
                      'timesheet_id':acc_obj.id,
                      'date':line.date,
                      'account_id':line.account_id.id,
                      'user_id':line.user_id.id,
                      'employee_id':obj.employee_id.id,
                      'total_hours':line.unit_amount,
                      'normal_hours':line_normal,
                      'ot_hours':line_ot,
                      'holiday_hours':line_holiday,
                       }
                self.pool.get('hr.sheet.line').create(cr, uid, vals, context=context)
            else:
                #~ prod_sr = self.pool.get('hr.project.account').search(cr, uid, [('account_id', '=', line.account_id.id), ('employee_id', '=', obj.employee_id.id)], context=context)
                #~ if not prod_sr:
                    #~ raise osv.except_osv(_('Error!'), _('Please Create Project Account!'))
                #~ else:
                    #~ proj_obj = self.pool.get('hr.project.account').browse(cr, uid, prod_sr[0])
                    vals = {
                       'sheet_id':obj.id,
                       'name':line.account_id.name + ' (' + obj.date_from + ' - ' + obj.date_to + ')',
                       'account_id':line.account_id.id,
                       'date_from':obj.date_from,
                       'date_to':obj.date_to,
                       }
                    acc_obj = self.pool.get('time.sheet.account').create(cr, uid, vals, context=context)
                    line_normal = 0.00
                    line_ot = 0.00
                    line_holiday = 0.00
                    dt = line.date
                    year, month, day = (int(x) for x in dt.split('-'))
                    ans = datetime.date(year, month, day)
                    if ans.strftime("%A") in tuple(leace_days):
                        line_holiday = line.unit_amount
                        line_normal = 0.00
                        line_ot = 0.00
                    else:
                        if dt in public_holi:
                            line_holiday = line.unit_amount
                            line_normal = 0.00
                            line_ot = 0.00
                        else:
                            if line.unit_amount > emp_hour.hours:
                                if emp_hour.ot_hours > 0.00:
                                    line_normal = emp_hour.hours
                                    line_bal = line.unit_amount - line_normal
                                    if line_bal > emp_hour.ot_hours:
                                        line_ot = emp_hour.ot_hours
                                        tot_holl = line_normal + line_ot
                                        hol = line.unit_amount - tot_holl
                                        line_holiday += hol
                                    else:
                                        line_ot = line_bal
                                else:
                                    line_ot = line.unit_amount - emp_hour.hours
                                    line_normal = emp_hour.hours
                            else:
                                line_normal = line.unit_amount
                    vals = {
                      'sheet_id':obj.id,
                      'timesheet_id':acc_obj,
                      'date':line.date,
                      'account_id':line.account_id.id,
                      'user_id':line.user_id.id,
                      'employee_id':obj.employee_id.id,
                      'total_hours':line.unit_amount,
                      'normal_hours':line_normal,
                      'ot_hours':line_ot,
                      'holiday_hours':line_holiday,
                       }
                    self.pool.get('hr.sheet.line').create(cr, uid, vals, context=context)
        total = []
        normal = []
        ot = []
        holiday = []
        em = self.pool.get('hr.employee').browse(cr, uid, obj.employee_id.id)
        balance_leave_hours = (holiday_leave - count) * em.hours
        for tot in obj.sheet_line:
            total.append(tot.total_hours)
            normal.append(tot.normal_hours)
            ot.append(tot.ot_hours)
            holiday.append(tot.holiday_hours)
        #~ tot_h = float(float_time(total)) + balance_leave_hours
        #~ nor_h = float(float_time(normal)) + balance_leave_hours
        tot_h = float_time(total)
        nor_h = float_time(normal)
        ot_h = float_time(ot)
        hol_h =  float_time(holiday)
        self.write(cr, uid, ids, {'validated':1, 'total_hours':tot_h, 'normal_hours':nor_h, 'ot_hours':ot_h, 'holiday_hours':hol_h}, context=context)
        return True
    
    

hr_timesheet_sheet_inherit()

class hr_sheet_line(osv.osv):
    _name = 'hr.sheet.line'
    _columns = {
        'sheet_id': fields.many2one('hr_timesheet_sheet.sheet', 'Timesheet'),
        'timesheet_id': fields.many2one('time.sheet.account', 'Timesheet Account'),
        'name': fields.char('Name', size=64),
        'date': fields.date('date'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'user_id': fields.many2one('res.users', 'User'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'total_hours': fields.float('Total Hours'),
        'normal_hours': fields.float('Normal Hours'),
        'ot_hours': fields.float('Overtime Hours'),
        'holiday_hours': fields.float('Holiday Hours'),

               }


hr_sheet_line()

class time_sheet_acount(osv.osv):
    _name = 'time.sheet.account'
    _columns = {

        'name': fields.char('Name', size=64, required=True, readonly=True),
        'hr_sheet_line': fields.one2many('hr.sheet.line', 'timesheet_id', 'Timesheet'),
        'sheet_id':fields.many2one('hr_timesheet_sheet.sheet', 'HR sheet'),
        'account_id': fields.many2one('account.analytic.account', 'Analytic Account', readonly=True),
        'date_from': fields.date('date From', readonly=True, states={'draft': [('readonly', False)]}),
        'date_to': fields.date('date To', readonly=True, states={'draft': [('readonly', False)]}),
        'time_sheet_acount_line': fields.one2many('time.sheet.account.line', 'time_sheet_id', 'Timesheet'),
        'sheet_employee_line': fields.one2many('sheet.employee.line', 'sheet_emp_id', 'Timesheet', readonly=True, states={'draft': [('readonly', False)]}),
        'sheet_department_line': fields.one2many('sheet.department.line', 'sheet_depart_id', 'Timesheet', states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('cancel', 'Cancelled'),
            ('progress', 'Progress'),
            ('validate', 'Validate'),
            ('done', 'Done'),
            ], 'Status'),
               }
    _defaults = {
         'state': 'draft'
                }

    def unlink(self, cr, uid, ids, context=None):
        time_account = self.read(cr, uid, ids, ['state'], context=context)
        for s in time_account:
            if s['state'] in ['done']:
                raise osv.except_osv(_('Invalid Action!'), _('Time sheet account id done not be deleted'))
        return super(time_sheet_acount, self).unlink(cr, uid, ids, context=context)
        
    def job_valdate(self, cr ,uid, ids, context=None):
        emp_obj2 = self.pool.get('hr.employee')
        emp_con = self.pool.get('hr.contract')
        emp_shee = self.pool.get('hr_timesheet_sheet.sheet')
        obj = self.browse(cr, uid, ids)
        day = str(obj.date_to).split('-')
        emp = []
        list_emp = []
        for line in obj.hr_sheet_line:
            emp.append(line.employee_id.id)
        emp_obj = [item for item, count in collections.Counter(emp).items() if count > 1]
        emp_obj1 = [item for item, count in collections.Counter(emp).items() if count <= 1]
        em = emp_obj + emp_obj1
        for emp1 in em:
            emp_ob = emp_obj2.browse(cr, uid, emp1)
            #~ con_hr = emp_con.search(cr, uid, [('employee_id', '=', emp_ob.id)], context=context)
            #~ con_obj = emp_con.browse(cr, uid, con_hr[0])
            cr.execute(''' SELECT distinct sheet_id FROM hr_sheet_line WHERE timesheet_id = '%s' and employee_id = '%s' ''' % (obj.id, emp_ob.id))
            em_hou = cr.fetchall()
            sheet = emp_shee.browse(cr, uid, em_hou[0][0])
            values = {'sheet_emp_id':obj.id,
                      'employee_id':emp_ob.id,
                      'job_id':emp_ob.job_id.id,
                      'uom_id':emp_ob.uom_id.id,
                      'normal_hours':sheet.normal_hours,
                      'ot_hours':sheet.ot_hours,
                      'holiday_hours':sheet.holiday_hours}
            list_emp.append(values)
        for line in list_emp:
            vals = {
                   'sheet_emp_id':line['sheet_emp_id'],
                   'employee_id':line['employee_id'],
                   'job_id':line['job_id'],
                   'uom_id':line['uom_id'],
                   'normal_hours':line['normal_hours'],
                   'ot_hours':line['ot_hours'],
                   'holiday_hours':line['holiday_hours']
                   }
            self.pool.get('sheet.employee.line').create(cr, uid, vals, context=context)

        depart = []
        for dep in obj.sheet_employee_line:
            emp_obj3 = emp_obj2.browse(cr, uid, dep.employee_id.id)
            if emp_obj3.uom_id.name in 'Hour(s)':
                hour_sal = emp_obj3.salary
                oth = hour_sal * 1.25
                hdh = hour_sal * 1.50
                val_de = {
                   'time_sheet_id':obj.id,
                   'employee_id':dep.employee_id.id,
                   'job_id':dep.job_id.id,
                   'uom_id':dep.uom_id.id,
                   'normal_cost':hour_sal,
                   'ot_cost':oth,
                   'holiday_cost':hdh
                     }
                self.pool.get('time.sheet.account.line').create(cr, uid, val_de, context=context)
            else:
                 if emp_obj3.uom_id.name in 'Day(s)':
                     day_sal = emp_obj3.salary
                     hour_sal = day_sal / emp_obj3.hours
                     oth = hour_sal * 1.25
                     hdh = hour_sal * 1.50
                     val_de1 = {
                             'time_sheet_id':obj.id,
                             'employee_id':dep.employee_id.id,
                             'job_id':dep.job_id.id,
                             'uom_id':dep.uom_id.id,
                             'normal_cost':hour_sal,
                             'ot_cost':oth,
                             'holiday_cost':hdh
                               }
                     self.pool.get('time.sheet.account.line').create(cr, uid, val_de1, context=context)
        return self.write(cr, uid, ids, {'state':'progress'}, context=context)

    def salary_validate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute(''' SELECT
                            sel.employee_id as employee_id,
                            sel.job_id as job_id,
                            sel.uom_id as uom_id,
                            sel.normal_hours * tsal.normal_cost as normal,
                            sel.ot_hours * tsal.ot_cost as ot,
                            sel.holiday_hours * tsal.holiday_cost as holiday
                       FROM sheet_employee_line sel
                       JOIN time_sheet_account_line tsal ON (tsal.employee_id = sel.employee_id)
                       WHERE sel.sheet_emp_id = '%s' and tsal.time_sheet_id= '%s' ''' % (obj.id,obj.id))
        sal = cr.fetchall()
        for salary in sal:
            vals = {
                  'sheet_depart_id':obj.id,
                  'employee_id':salary[0],
                  'job_id':salary[1],
                  'uom_id':salary[2],
                  'normal_cost':salary[3],
                  'ot_cost':salary[4],
                  'holiday_cost':salary[5]
                   }
            self.pool.get('sheet.department.line').create(cr, uid, vals, context=context)
        return self.write(cr, uid, ids, {'state':'validate'}, context=context)

    def invoice_create(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        part = self.pool.get('res.partner').browse(cr, uid, obj.account_id.partner_id.id)
        cr.execute('''
                      SELECT
                           sdl.job_id as job_id,
                           hj.product_id as product_id,
                           SUM(sdl.normal_cost) as normal,
                           SUM(sdl.ot_cost) as ot,
                           SUM(sdl.holiday_cost) as holiday
                      FROM
                          sheet_department_line sdl
                          JOIN hr_job hj ON (hj.id = sdl.job_id)
                      WHERE sdl.sheet_depart_id = '%s' and sdl.create_inv is True
                      GROUP BY sdl.job_id,hj.product_id ''' % (obj.id))
        inv = cr.fetchall()
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')], limit=1)
        prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
        print prop, "RRRRRRRRRRRRRRR"
        vals = {
                   'partner_id':obj.account_id.partner_id.id,
                   'type':'out_invoice',
                   'timesheet_id':obj.id,
                   'contract_id':obj.account_id.id,
                   'origin':obj.name,
                   'account_id':part.property_account_receivable.id,
                   'journal_id':journal_ids[0]

               }
        inv_obj = self.pool.get('account.invoice').create(cr, uid, vals, context=context)
        for invoice in inv:
            items = []
            for line in obj.sheet_department_line:
                cr.execute('''
                         select
                               hr.name_related,
                               sel.normal_hours,
                               sel.ot_hours,
                               sel.holiday_hours,
                               tsal.normal_cost,
                               tsal.ot_cost,
                               tsal.holiday_cost,
                               sdl.normal_cost,
                               sdl.ot_cost,
                               sdl.holiday_cost
                         from
                              time_sheet_account tsc
                              join sheet_employee_line sel on (sel.sheet_emp_id = tsc.id)
                              join hr_employee hr on (hr.id = sel.employee_id)
                              join time_sheet_account_line tsal on (tsal.time_sheet_id = tsc.id)
                              join sheet_department_line sdl on (sdl.sheet_depart_id = tsc.id) 
                         where tsc.id= '%s' and sel.employee_id = '%s' and sdl.create_inv is True and tsal.employee_id = '%s' and sdl.employee_id = '%s' and sel.job_id = '%s' and tsal.job_id='%s' and sdl.job_id='%s'     
                       ''' % (obj.id, line.employee_id.id, line.employee_id.id, line.employee_id.id, invoice[0],invoice[0],invoice[0]))
                emp = cr.fetchall()
                print emp
                if emp:
                    name = 'Employee = ' + str(emp[0][0]) + \
                         ', Normal = ' + str(emp[0][1]).replace(".0", ":00") + ' * ' + str("%0.2f" % emp[0][4]) + ' = ' + str("%0.2f" % emp[0][7]) + \
                         ', Over = ' + str(emp[0][2]).replace(".0", ":00") + ' * ' + str("%0.2f" % emp[0][5]) + ' = ' + str("%0.2f" % emp[0][8]) + \
                         ', Holiday = ' + str(emp[0][3]).replace(".0", ":00") + ' * ' + str("%0.2f" % emp[0][6]) + ' = ' + str("%0.2f" % emp[0][9])
                    items.append(name)
            des = 'Normal Cost = ' + str("%0.2f" % invoice[2]) + ', ' + 'Overtime Cost = ' + str("%0.2f" % invoice[3]) + ', ' + 'Holiday Cost = ' + str("%0.2f" % invoice[4])
            items.append(des)
            vals_line = {
                      'invoice_id':inv_obj,
                      'name':items,
                      'product_id':invoice[1],
                      'account_id':prop.id,
                      'quantity':1.00,
                      'price_unit':invoice[2]+invoice[3]+invoice[4]
                        }
            self.pool.get('account.invoice.line').create(cr, uid, vals_line, context=context)
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def action_view_invoice(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        '''
        This function returns an action that display existing invoices of given Time sheet ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        inv_ids = self.pool.get('account.invoice').search(cr, uid, [('timesheet_id', '=', obj.id)], context=context)
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

time_sheet_acount()

class time_sheet_acount_line(osv.osv):
    _name = 'time.sheet.account.line'
    _columns = {
          'time_sheet_id': fields.many2one('time.sheet.account', 'timesheet'),
          'project_account_id':fields.many2one('hr.project.account', 'Project Account'),
          'employee_id': fields.many2one('hr.employee', 'Employee'),
          'job_id': fields.many2one('hr.job', 'Job Position'),
          'uom_id': fields.many2one('product.uom', 'Salary Type'),
          'normal_cost': fields.float('Normal Price'),
          'ot_cost': fields.float('Overtime Price'),
          'holiday_cost': fields.float('Holiday Price'),
               }
time_sheet_acount_line()

class sheet_employee_line(osv.osv):
    _name = 'sheet.employee.line'
    _columns = {

        'sheet_emp_id': fields.many2one('time.sheet.account', 'Timesheet'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'job_id': fields.many2one('hr.job', 'Job Position'),
        'uom_id': fields.many2one('product.uom', 'Salary Type'),
        'normal_hours': fields.float('Normal Hours'),
        'ot_hours': fields.float('Overtime Hours'),
        'holiday_hours': fields.float('Holiday Hours'),
               }

sheet_employee_line()

class sheet_department_line(osv.osv):
    _name = 'sheet.department.line'
    _columns = {

        'sheet_depart_id':fields.many2one('time.sheet.account', 'Timesheet'),
        'create_inv':fields.boolean('Create Invoice'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'job_id': fields.many2one('hr.job', 'Job Position'),
        'uom_id': fields.many2one('product.uom', 'Salary Type'),
        'normal_cost': fields.float('Normal'),
        'ot_cost': fields.float('Overtime'),
        'holiday_cost': fields.float('Holiday'),
               }

sheet_department_line()


class account_invoice_inherit(osv.osv):
    _inherit = 'account.invoice'
    _columns = {

       'timesheet_id':fields.many2one('time.sheet.account', 'Timesheet Account'),
       'contract_id':fields.many2one('account.analytic.account', 'Contract Account')
              }

account_invoice_inherit()


