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

from openerp import models, fields, api
from openerp.osv import osv, fields
from openerp.tools.translate import _
import datetime

class hr_employee(osv.osv):
    
    _inherit = 'hr.employee'

    def send_reminder_email(self,cr,uid,context=None):
        partner_obj = self.pool.get('hr.employee')
        mail_mail = self.pool.get('mail.mail')
        mail_ids=[]
        template_obj = self.pool.get('email.template')
        today = datetime.datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        par_id = partner_obj.search(cr, uid, [ ('pass_remind','like',today_month_day)])
        group_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hr.employee')])[0]
        body_html="Employee Code"+'               '+"Employee Name"+"<br/>"
        for val in partner_obj.browse(cr, uid, par_id):
            body_html+=str(val.emp_code)+'                    '+str(val.name)+"<br/>"
        print 'dfgffffffffffffffffffffffffffffh',body_html
        print'333333333333333333333333333333333333333333333',par_id
        s=[]
        cr.execute("""SELECT DISTINCT
                res_users.login
                FROM res_groups_users_rel
                JOIN res_groups
                ON res_groups.id = res_groups_users_rel.gid
                JOIN public.res_users
                ON res_groups_users_rel.uid = res_users.id
                JOIN ir_module_category 
                ON res_groups.category_id = ir_module_category.id
                WHERE res_groups.name='Manager' and ir_module_category.name='Human Resources'""")
        d = cr.fetchall()
        print'0000000000000000000000000000000000000000',d
        for val in partner_obj.browse(cr, uid, par_id):
            s.append(val.name)
        if par_id:
            try:
                for i in range(len(d)):
                    print'222222222222222222222222222222222222',val.name
                    email_from = d[i][0]
                    name = val.name                
                    subject = "Passport Expiry Reminder"
                    body = _("Dear Manager, \n")
                                    
                    body+=_("\t Validity of a Passport has been expired for the follwing list of employees. \n ")                     
                    mail_ids.append(mail_mail.create(cr, uid, {
                        'email_to': email_from,
                        'subject': subject,
                        
                        'body_html':'<pre><span class="inner-pre" style="font-size:15px">%s<br/>%s</span></pre>'%(body,body_html),
                        
                     }, context=context))
                    mail_mail.send(cr, uid, mail_ids, context=context)            
            except Exception, e:
                print "Exception", e ,'****************************'  
        return None         
        
    def send_visa_reminder_email(self,cr,uid,context=None):
        partner_obj = self.pool.get('hr.employee')
        mail_mail = self.pool.get('mail.mail')
        mail_ids=[]
        template_obj = self.pool.get('email.template')
        today = datetime.datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        par_id = partner_obj.search(cr, uid, [ ('visa_remind','like',today_month_day)])
        group_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hr.employee')])[0]
        body_html="Employee Code"+'               '+"Employee Name"+"<br/>"
        for val in partner_obj.browse(cr, uid, par_id):
            body_html+=str(val.emp_code)+'                    '+str(val.name)+"<br/>"
        print 'dfgffffffffffffffffffffffffffffh',body_html
        print'333333333333333333333333333333333333333333333',par_id
        s=[]
        cr.execute("""SELECT DISTINCT
                res_users.login
                FROM res_groups_users_rel
                JOIN res_groups
                ON res_groups.id = res_groups_users_rel.gid
                JOIN public.res_users
                ON res_groups_users_rel.uid = res_users.id
                JOIN ir_module_category 
                ON res_groups.category_id = ir_module_category.id
                WHERE res_groups.name='Manager' and ir_module_category.name='Human Resources'""")
        d = cr.fetchall()
        print'0000000000000000000000000000000000000000',d
        for val in partner_obj.browse(cr, uid, par_id):
            s.append(val.name)
        if par_id:
            try:
                for i in range(len(d)):
                    print'222222222222222222222222222222222222',val.name
                    email_from = d[i][0]
                    name = val.name                
                    subject = "Visa Expiry Reminder"
                    body = _("Dear Manager, \n")
                                    
                    body+=_("\t Validity of a Visa has been expired for the follwing list of employees. \n ")                     
                    mail_ids.append(mail_mail.create(cr, uid, {
                        'email_to': email_from,
                        'subject': subject,
                        
                        'body_html':'<pre><span class="inner-pre" style="font-size:15px">%s<br/>%s</span></pre>'%(body,body_html),
                        
                     }, context=context))
                    mail_mail.send(cr, uid, mail_ids, context=context)            
            except Exception, e:
                print "Exception", e ,'****************************'  
        return None         
        
    def send_insurance_reminder_email(self,cr,uid,context=None):
        partner_obj = self.pool.get('hr.employee')
        mail_mail = self.pool.get('mail.mail')
        mail_ids=[]
        template_obj = self.pool.get('email.template')
        today = datetime.datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        par_id = partner_obj.search(cr, uid, [ ('ins_remind','like',today_month_day)])
        group_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hr.employee')])[0]
        body_html="Employee Code"+'               '+"Employee Name"+"<br/>"
        for val in partner_obj.browse(cr, uid, par_id):
            body_html+=str(val.emp_code)+'                    '+str(val.name)+"<br/>"
        print 'dfgffffffffffffffffffffffffffffh',body_html
        print'333333333333333333333333333333333333333333333',par_id
        s=[]
        cr.execute("""SELECT DISTINCT
                res_users.login
                FROM res_groups_users_rel
                JOIN res_groups
                ON res_groups.id = res_groups_users_rel.gid
                JOIN public.res_users
                ON res_groups_users_rel.uid = res_users.id
                JOIN ir_module_category 
                ON res_groups.category_id = ir_module_category.id
                WHERE res_groups.name='Manager' and ir_module_category.name='Human Resources'""")
        d = cr.fetchall()
        print'0000000000000000000000000000000000000000',d
        for val in partner_obj.browse(cr, uid, par_id):
            s.append(val.name)
        if par_id:
            try:
                for i in range(len(d)):
                    print'222222222222222222222222222222222222',val.name
                    email_from = d[i][0]
                    name = val.name                
                    subject = "Insurance Expiry Reminder"
                    body = _("Dear Manager, \n")
                                    
                    body+=_("\t Validity of a Insurance has been expired for the follwing list of employees. \n ")                     
                    mail_ids.append(mail_mail.create(cr, uid, {
                        'email_to': email_from,
                        'subject': subject,
                        
                        'body_html':'<pre><span class="inner-pre" style="font-size:15px">%s<br/>%s</span></pre>'%(body,body_html),
                        
                     }, context=context))
                    mail_mail.send(cr, uid, mail_ids, context=context)            
            except Exception, e:
                print "Exception", e ,'****************************'  
        return None         
        
    def send_cnia_reminder_email(self,cr,uid,context=None):
        partner_obj = self.pool.get('hr.employee')
        mail_mail = self.pool.get('mail.mail')
        mail_ids=[]
        template_obj = self.pool.get('email.template')
        today = datetime.datetime.now()    
        today_month_day = '%-' + today.strftime('%m') + '-' + today.strftime('%d')
        par_id = partner_obj.search(cr, uid, [ ('cnia_remind','like',today_month_day)])
        group_model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hr.employee')])[0]
        body_html="Employee Code"+'               '+"Employee Name"+"<br/>"
        for val in partner_obj.browse(cr, uid, par_id):
            body_html+=str(val.emp_code)+'                    '+str(val.name)+"<br/>"
        print 'dfgffffffffffffffffffffffffffffh',body_html
        print'333333333333333333333333333333333333333333333',par_id
        s=[]
        cr.execute("""SELECT DISTINCT
                res_users.login
                FROM res_groups_users_rel
                JOIN res_groups
                ON res_groups.id = res_groups_users_rel.gid
                JOIN public.res_users
                ON res_groups_users_rel.uid = res_users.id
                JOIN ir_module_category 
                ON res_groups.category_id = ir_module_category.id
                WHERE res_groups.name='Manager' and ir_module_category.name='Human Resources'""")
        d = cr.fetchall()
        print'0000000000000000000000000000000000000000',d
        for val in partner_obj.browse(cr, uid, par_id):
            s.append(val.name)
        if par_id:
            try:
                for i in range(len(d)):
                    print'222222222222222222222222222222222222',val.name
                    email_from = d[i][0]
                    name = val.name                
                    subject = "CNIA Expiry Reminder"
                    body = _("Dear Manager, \n")
                                    
                    body+=_("\t Validity of a CNIA has been expired for the follwing list of employees. \n ")                     
                    mail_ids.append(mail_mail.create(cr, uid, {
                        'email_to': email_from,
                        'subject': subject,
                        
                        'body_html':'<pre><span class="inner-pre" style="font-size:15px">%s<br/>%s</span></pre>'%(body,body_html),
                        
                     }, context=context))
                    mail_mail.send(cr, uid, mail_ids, context=context)            
            except Exception, e:
                print "Exception", e ,'****************************'  
        return None 
