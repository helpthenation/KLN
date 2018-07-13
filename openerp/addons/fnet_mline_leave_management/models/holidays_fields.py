# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
import datetime
import math
import time
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api,_
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from openerp.exceptions import Warning

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'

    is_vaction_leave=fields.Boolean(string="Is Vaction Leave")
    is_long_vaction_leave=fields.Boolean(string="Is Long Vaction Leave")
    buffered_count=fields.Float(compute='_compute_buffered_days',string='Buffered Vacation Days',store=True)
    validity=fields.Date(compute='_leave_validity',string='Leave Validity Upto',store=True,readonly=False)
    as_on_allocation=fields.Date('As On',help='The Date Of The Leave Allocation')
    
    @api.multi
    @api.depends('employee_id.contract_ids.date_start')
    def _leave_validity(self):
        for rec in self:
            if rec.employee_id.contract_id.date_start:
                if rec.holiday_status_id.code == 'VL':              
                    next_year = datetime.datetime.strptime(rec.employee_id.contract_id.date_start,'%Y-%m-%d') + relativedelta(years=2)
                    rec.validity=next_year.strftime('%Y-%m-%d')
                if rec.holiday_status_id.code == 'ML':              
                    next_year = datetime.datetime.strptime(rec.employee_id.contract_id.date_start,'%Y-%m-%d') + relativedelta(years=1)
                    rec.validity=next_year.strftime('%Y-%m-%d')     

    
    @api.depends('holiday_status_id','date_from','date_to','as_on_date')
    @api.multi
    def _compute_buffered_days(self):
        for rec in self:
            if rec.holiday_status_id.code == 'VL' and rec.type=='remove':
                rec.is_vaction_leave=True
                if rec.as_on_date and rec.date_from and rec.date_to:
                    start_date = datetime.datetime.strptime(rec.as_on_date, "%Y-%m-%d")
                    end_date = datetime.datetime.strptime(rec.date_from, "%Y-%m-%d %H:%M:%S")
                    if rec.employee_id:
                        cur_date=[]
                        self.env.cr.execute('''select hh.employee_id,hh.date_from,hh.date_to
                                            from hr_holidays hh
                                            join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            where hh.employee_id = '%s' and hhs.code ='VL' and hh.date_from != '%s' and hh.date_to != '%s'
                                            ''' % (rec.employee_id.id,rec.date_from,rec.date_to))
                        emp = self.env.cr.dictfetchall()
                        if emp != []:
                            for k in emp:
                                if k['date_from'] and k['date_to']:
                                    start_dates=parse(k['date_from'])
                                    stop_dates=parse(k['date_to'])
                                    for dts in rrule(DAILY, dtstart=start_dates, until=stop_dates):
                                            day_dates=dts.strftime("%Y-%m-%d")
                                            cur_date.append(day_dates)
                        vacation_date=[]
                        start_dates=parse(rec.as_on_date)
                        stop_dates=parse(rec.date_from)
                        for dts in rrule(DAILY, dtstart=start_dates, until=stop_dates):
                            day_dates=dts.strftime("%Y-%m-%d")
                            self.env.cr.execute('''select hh.id
                                        from hr_holidays hh
                                        join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                        where hh.employee_id = '%s' and hhs.code ='VL' and '%s' between hh.date_from::date and hh.date_to::date
                                        ''' % (rec.employee_id.id,day_dates))
                            emp = self.env.cr.dictfetchone()
                            if emp:
                                vacation_date.append(day_dates)                                  
                                                                            
                        self.env.cr.execute('''select hh.number_of_days as day
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code ='VL' and hh.state='validate' and hh.type='add' '''%(rec.employee_id.id))
                        res=self.env.cr.dictfetchone()                        
                        if res:
                           rec.buffered_count = res['day']  - len(cur_date)  +  (((end_date-start_date).days-1 - len(vacation_date)) * 0.0822)
                    else:
                        rec.buffered_count = ((end_date-start_date).days-1  * 0.0822)
                else:
                    rec.buffered_count = 0.00
            else:
                rec.is_long_vaction_leave=True

                            
                    
