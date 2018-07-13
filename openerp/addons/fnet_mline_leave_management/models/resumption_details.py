import datetime
import math
import time
from datetime import date, timedelta,datetime
from operator import attrgetter
from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _
import calendar

class resumption_details(osv.osv):
    _name="resumption.details"
    _rec_name="discription"    
    def _default_code(self,cr,uid,context=None):
        print 'tttttttttttttttttttttttttt'
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            a=self.pool.get('hr.employee').browse(cr,uid,emp_id,context=context)
            return a.emp_code
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            a=self.pool.get('hr.employee').browse(cr,uid,ids[0],context=context)
            return a.emp_code
        return False
        
    def _default_sponsor_id(self,cr,uid,context=None):
        print 'lllllllllllllllllllllllllllllllll'
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            a=self.pool.get('hr.employee').browse(cr,uid,emp_id,context=context)
            return a.branch_id.id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            a=self.pool.get('hr.employee').browse(cr,uid,ids[0],context=context)
            return a.branch_id.id
        return False    
    
      
    def _employee_get(self, cr, uid, context=None):        
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False    
    
    _columns = {   
           'holiday_status_id':fields.selection([('VL','Vacation Leave'),('LVL','Long Vaction Leave')],'Leave Type',required=True),      
           'employee_id': fields.many2one('hr.employee','Employee',required=True),
           'code': fields.char('Employee Code',readonly=True),
           'sponsor_id':fields.many2one('company.branch','Sponsor ID', readonly=True),
           'doj':fields.date('Re-Joining Date', required=True),
           'discription':fields.text('Description'),
           'state':fields.selection([('draft','Draft'),('hr_approval','HR Approval'),('manager_approval','Manager Approval'),('done','Done'),('cancel','Cancel')],'State'),
           } 
           
    _defaults={
              'employee_id': _employee_get,
              'code':_default_code,
              'sponsor_id':_default_sponsor_id,
              'state':'draft',
              }  
  
              
    #~ def button_submit(self, cr, uid, ids, context=None):     
        #~ self.write(cr, uid, ids, {'state': 'hr_approval'})   
                      
    def button_validate(self, cr, uid, ids, context=None):     
        self.write(cr, uid, ids, {'state': 'hr_approval'})
           
    def button_approve(self, cr, uid, ids, context=None):     
        self.write(cr, uid, ids, {'state': 'manager_approval'}) 
          
    def button_done(self, cr, uid, ids, context=None):
        obj=self.browse(cr,uid,ids)
        cr.execute('''select hh.date_from::date as date_from,hh.date_to::date as date_to,hh.holiday_status_id as holiday_id
                           from hr_holidays hh
                           join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                           where hh.employee_id = '%s' and hhs.code='%s' and hh.type='remove' order by date_to::date Desc'''%(obj.employee_id.id,obj.holiday_status_id)) 
        res=cr.dictfetchone()
        date=datetime.now().strftime('%Y-%m-%d')
        if res:
            contract_id=self.pool.get('hr.contract').search(cr, uid,[('employee_id', '=', obj.employee_id.id)],limit=1,order='id desc')                 
            print 'fffffffffffffffff',contract_id
            
            if contract_id != []:
                vals={                
                      'resumption_id':contract_id[0],
                      'rejoining_date':obj.doj,
                      'start_date':res['date_from'],
                      'end_date':res['date_to'],
                      'type':res['holiday_id'],
                      'detail_id':obj.id
                      }
                self.pool.get('rejoin.detail').create(cr,uid,vals,context=context)
        self.write(cr, uid, ids, {'state': 'done'}) 
          
    def button_cancel(self, cr, uid, ids, context=None):     
        self.write(cr, uid, ids, {'state': 'cancel'}) 
        
    def action_set_to_draft(self, cr, uid, ids, context=None): 
        obj=self.browse(cr,uid,ids)
        cr.execute("""delete from  rejoin_detail where rejoining_date = '%s' and
        detail_id = %d"""%(obj.doj,obj.id))
        self.write(cr, uid, ids, {'state': 'draft'}) 
          
                      
    def onchange_employee_id(self,cr,uid,ids,employee_id,context=None):
        result = {'value': {
                               'department_id': False,
                               'code': None,
                               'sponsor_id':False,
                               }}
        if employee_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            result['value'] = {
                                   'code': employee.emp_code,
                                   'sponsor_id': employee.branch_id.id,
                                  
                                   }
        return result   
        
    def onchange_date_of_rejoining(self,cr,uid,ids,doj,employee_id,holiday_status_id,context=None):
        obj=self.browse(cr,uid,ids)
        if employee_id and doj and holiday_status_id:                          
            cr.execute('''select hh.date_from::date as date_from,hh.date_to::date as date_to,hh.holiday_status_id as holiday_id
                               from hr_holidays hh
                               join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)
                               where hh.employee_id = '%s' and hhs.code='%s' and hh.type='remove' 
                               group by hh.date_from,hh.date_to,hh.holiday_status_id
                               order by date_to::date Desc'''%(employee_id,holiday_status_id)) 
            leave_date=cr.dictfetchone()
            date=datetime.now().strftime('%Y-%m-%d')
            if leave_date:
                if  doj < leave_date['date_to']:
                    return {'warning': {
                                'title': "Warning!!!",
                                'message': "Rejoin Date Must Be Greater Vacation To Date %s."%(leave_date['date_to'])},
                                'value':{'doj':False},
                               }  
                elif doj > date:
                    return {'warning': {
                                'title': "Warning!!!",
                                'message': "Rejoin Date Must Be Less Or Equal Present Date %s."%(date)},
                                'value':{'doj':False},
                               }                
                else:
                    cr.execute("""select id from hr_holidays where '%s' between date_from::date and date_to::date and employee_id = %d """%(doj,employee_id))
                    prev_hol=cr.dictfetchone()
                    if  prev_hol:
                         return {'warning': {
                                'title': "Warning!!!",
                                'message': "Invalid Re-Joining Date \n You Cann't Given A Date Which Already Present In Leave %s."%(doj)},
                                'value':{'doj':False},
                               }                               
                                                 
            elif doj < date:
                return {'warning': {
                            'title': "Warning!!!",
                            'message': "Rejoin Date Must Be Less Or Equal Present Date %s."%(date)},
                            'value':{'doj':False},
                           }                
            else:
                cr.execute("""select id from hr_holidays where '%s' between date_from::date and date_to::date and employee_id = %d """%(doj,employee_id))
                prev_hol=cr.dictfetchone()
                if  prev_hol:
                     return {'warning': {
                            'title': "Warning!!!",
                            'message': "Invalid Re-Joining Date \n You Cann't Given A Date Which Already Present In Leave %s."%(doj)},
                            'value':{'doj':False},
                           } 
                           
                
            
           
            #~ if obj.doj < res['date_to']  :
                 #~ raise Warning(('Invalid Re-Joining Date'))
            #~ elif  date >= obj.doj:     
                 #~ raise Warning(('Invalid Re- Date'))

               

