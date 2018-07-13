from openerp import api, fields, models, _
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

class hr_employee(models.Model):
    _inherit='hr.employee'
    
    @api.model
    def _leave_reset(self):
        employee = self.env['hr.employee']
        dt = datetime.datetime.now()
        today =dt.strftime('%Y-%m-%d')
        employee_line_ids = employee.search([]) 
        vacation_id = self.env['hr.holidays.status'].search([('code', '=', 'VL')], offset=0, limit=1, order='id desc') 
        medical_id = self.env['hr.holidays.status'].search([('code', '=', 'ML')], offset=0, limit=1, order='id desc')  
        for emp in employee_line_ids:
            self.env.cr.execute('''select id from hr_holidays where employee_id=%d and type='add' '''%(emp.id))
            res = self.env.cr.dictfetchall()
            if res:
                for i in res:
                    holiday_obj = self.env['hr.holidays'].browse(i['id'])        
                    if holiday_obj.validity == today and holiday_obj.holiday_status_id == vacation_id:
                        next_validity = datetime.datetime.strptime(holiday_obj.validity,'%Y-%m-%d') + relativedelta(years=2)
                        new_validity=next_validity.strftime('%Y-%m-%d')
                        #~ year_obj, month_obj, day = (int(x) for x in holiday_obj.validity.split('-'))
                        #~ cur_date=[]
                        #~ self.env.cr.execute('''select hh.employee_id,hh.date_from,hh.date_to
                                            #~ from hr_holidays hh
                                            #~ join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                                            #~ where hh.employee_id = '%s' and hhs.code ='VL' and hh.date_from::date >= '%s' and hh.date_to <= '%s'
                                            #~ ''' % (emp.id))
                        #~ emp = self.env.cr.dictfetchall()
                        #~ if emp != []:
                            #~ for k in emp:
                                #~ if k['date_from'] and k['date_to']:
                                    #~ start_dates=parse(k['date_from'])
                                    #~ stop_dates=parse(k['date_to'])
                                    #~ for dts in rrule(DAILY, dtstart=start_dates, until=stop_dates):
                                            #~ day_dates=dts.strftime("%Y-%m-%d")
                                            #~ cur_date.append(day_dates)                        
                        
                        #~ TO ENABLE VACATION LEAVE RESET KINDLY UNCOMMENT BELOW LINE
                        #~ holiday_obj.write({'validity':new_validity,'number_of_days':0.00,'number_of_days_temp':0.00})                    
                        #~ print'VVVVVVVVVVVVVVVVVVVVVVVVV',holiday_obj.validity
                    if holiday_obj.validity == today and holiday_obj.holiday_status_id == medical_id:              
                        next_validity = datetime.datetime.strptime(holiday_obj.validity,'%Y-%m-%d') + relativedelta(years=1)
                        new_validity=next_validity.strftime('%Y-%m-%d')     
                        holiday_obj.write({'validity':new_validity,'number_of_days':15,'number_of_days_temp':15})                    
                        #~ print'VVVVVVVVVVVVVVVVVVVVVVVVV',holiday_obj.validity

