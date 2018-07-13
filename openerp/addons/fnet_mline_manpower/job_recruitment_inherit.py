
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

from openerp.osv import osv, fields
from openerp.tools.translate import _

class hr_job_inherit(osv.osv):
    
    #~ def _common_employees(self, cr, uid, ids, name, args, context=None):
        #~ res = {}
        #~ for job in self.browse(cr, uid, ids, context=context):
            #~ nb_employees = len(job.employee_ids or [])
            #~ res[job.id] = {
                #~ 'no_of_employee': nb_employees,
                #~ 'expected_employees': nb_employees + job.no_of_recruitment,
            #~ }
        #~ return res
    _inherit = 'hr.job'
    
    def _get_attached_docs(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        attachment_obj = self.pool.get('ir.attachment')
        for job_id in ids:
            applicant_ids = self.pool.get('hr.applicant').search(cr, uid, [('job_id', '=', job_id)], context=context)
            res[job_id] = attachment_obj.search(
                cr, uid, [
                    '|',
                    '&', ('res_model', '=', 'hr.job'), ('res_id', '=', job_id),
                    '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicant_ids)
                ], context=context)
        return res
    
    def _count_all(self, cr, uid, ids, field_name, arg, context=None):
        Applicant = self.pool['hr.applicant']
        return {
            job_id: {
                'application_count': Applicant.search_count(cr,uid, [('job_id', '=', job_id)], context=context),
                'documents_count': len(self._get_attached_docs(cr, uid, [job_id], field_name, arg, context=context)[job_id])
            }
            for job_id in ids
        }

    _columns = { 
       
       'lead_id': fields.many2one('crm.lead', 'Enquiry Ref', readonly=True),
       #~ 'common_pool': fields.function(_common_employees, string="Common Pool",
            #~ help='Number of employees currently occupying this job position.',
            #~ store = {
                #~ 'hr.employee': (_get_job_position, ['job_id'], 10),
            #~ }, type='integer',
            #~ multi='_get_nbr_employees'),
       'partner_id': fields.many2one('res.partner', 'Customer', readonly=True),
       'product_id': fields.many2one('product.product', 'Product'),
       'application_count': fields.function(_count_all, type='integer', string='Applications', multi=True),     
               }
          
hr_job_inherit()

class hr_applicant_inherit(osv.osv):
    _inherit = 'hr.applicant'
    _columns = {
         
         'lead_id': fields.many2one('crm.lead', 'Enquiry Ref'),
         'partner_id': fields.many2one('res.partner', 'Customer'),
         'sponsor_id': fields.many2one('company.branch', 'Sponsor ID', required=True),
         'address_id': fields.many2one('res.partner', 'Job Location', help="Address where employees are working"),     
               }
               
    def create_employee_from_applicant(self, cr, uid, ids, context=None):
        """ Create an hr.employee from the hr.applicants """
        if context is None:
            context = {}
        hr_employee = self.pool.get('hr.employee')
        user = self.pool.get('res.users')
        model_data = self.pool.get('ir.model.data')
        act_window = self.pool.get('ir.actions.act_window')
        emp_id = False
        for applicant in self.browse(cr, uid, ids, context=context):
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = self.pool.get('res.partner').address_get(cr, uid, [applicant.partner_id.id], ['contact'])['contact']
                contact_name = self.pool.get('res.partner').name_get(cr, uid, [applicant.partner_id.id])[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                create_ctx = dict(context, mail_broadcast=True)
                # User Creation
                #~ val = {'login': applicant.partner_name, 'password': applicant.partner_name, 'name': applicant.partner_name}
                #~ relat_user = user.create(cr, uid, val, context=context)
                # Employee Creation #
                lead_br = self.pool.get('crm.lead').browse(cr, uid, applicant.lead_id.id)
                price = 0.00
                for line in lead_br.man_line:
                    if line.product_id.id == applicant.job_id.product_id.id:
                        price = line.normal_price
                emp_id = hr_employee.create(cr, uid, {'name': applicant.partner_name or contact_name,
                                                     'job_id': applicant.job_id.id,
                                                     #~ 'address_home_id': address_id,
                                                     'uom_id':applicant.job_id.product_id.uom_id.id,
                                                     'salary':price,
                                                     #~ 'user_id':relat_user,
                                                     'branch_id':applicant.sponsor_id.id,
                                                     'hours': 8.00,
                                                     'department_id': applicant.department_id.id or False,
                                                     'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                     'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                                     'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False,
                                                     }, context=create_ctx)
                self.write(cr, uid, [applicant.id], {'emp_id': emp_id}, context=context)
                self.pool['hr.job'].message_post(
                    cr, uid, [applicant.job_id.id],
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired", context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('You must define an Applied Job and a Contact Name for this applicant.'))

        action_model, action_id = model_data.get_object_reference(cr, uid, 'hr', 'open_view_employee_list')
        dict_act_window = act_window.read(cr, uid, [action_id], [])[0]
        if emp_id:
            dict_act_window['res_id'] = emp_id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

hr_applicant_inherit()

class hr_employee_inherit(osv.osv):
    _inherit = 'hr.employee'
    
    def _leaves_count(self, cr, uid, ids, field_name, arg, context=None):
        Holidays = self.pool['hr.holidays']
        return {
            employee_id: Holidays.search_count(cr,uid, [('employee_id', '=', employee_id), ('type', '=', 'add')], context=context)
            for employee_id in ids
        }
    def _default_value(self, cr, uid, ids, context=None):
        flag=self.pool.get('res.users').has_group(cr,uid,'base.group_hr_manager')
      
    #~ 
    _columns = {
       # Customer Contract
       'account_id': fields.many2one('account.analytic.account', 'Customer Contract', required=True),
       # Customer Information
       'uom_id': fields.many2one('product.uom', 'Salary Type', required=True),
       'hours': fields.float('Hours', required=True), 
       'ot_hours': fields.float('Overtime Hours'), 
       'salary': fields.float('Salary Cost', required=True),
       # Company Information
       # Passport
       'passport_no':fields.char('Passport No', size=64),
       'expiry_date':fields.date('Passport Expiry'),
       'pass_place_issue': fields.char('Place of Issue', size=64),
       'pass_issue': fields.date('Passport Issue'),
       'pass_remind': fields.date('Passport Reminder'),
       
       # Emirates
       'emirates_no': fields.char('Emirates ID No', size=64),
       'emirates_expiry':fields.date('Emirates Expiry Date'),
       'emirates_issue': fields.date('Emirates Issue'),
       'emirates_remind': fields.date('Emirates Reminder'),
       
       # Other
       'other_name': fields.char('Card Name', size=64),
       'other_no': fields.char('Card No', size=64),
       'other_issue': fields.date('Card Issue'),
       'other_expiry': fields.date('Card Expiry'),
       'other_remind': fields.date('Card Reminder'),
       
       # Visa
       'visa_no':fields.char('Visa No', size=64),
       'visa_expiry':fields.date('Visa Expiry Date'),
       'visa_type':fields.char('Visa Type', size=64),
       'visa_issue': fields.date('Visa Issue'),
       'visa_remind': fields.date('Visa Reminder'),
       
       # Labour
       'labour_no': fields.char('Labour Card No', size=64),
       'labour_expiry':fields.date('Labour Expiry Date'),
       'labour_issue': fields.date('Labour Issue'),
       'labour_remind': fields.date('Labour Reminder'),
       
       # Insurance
       'ins_comp_name': fields.char('Insurance Company Name', size=64),
       'ins_no': fields.char('Insurance No', size=64),
       'ins_issue': fields.date('Insurance Issue'),
       'ins_expiry': fields.date('Insurance Expiry'),
       'ins_remind': fields.date('Insurance Reminder'),
       
       # CINA
       'cnia_no': fields.char('CNIA No', size=64),
       'cnia_expiry':fields.date('CNIA Expiry Date'),
       'cnia_issue': fields.date('CNIA Issue'),
       'cnia_remind': fields.date('CNIA Reminder'),
       
       'branch_id':fields.many2one('company.branch', 'Sponsor ID', required=True),
       'emp_code':fields.char('Employee Code'),
       #~ 'leave_lines':fields.many2many('hr.employee.leave', 'employee_leave_rel', 'emp_id', 'leave_id', 'Leave', required=True),
       # Family Information
       'father_name': fields.char('Father Name', size=64),
       'mother_name': fields.char('Mother Name', size=64),
       'spouse_name': fields.char('Spouse Name', size=64),
       'country_id': fields.many2one('res.country', 'Country'),
       'state_id': fields.many2one('res.country.state', 'State'),
       'phone_no': fields.char('Phone No', size=15),
       
       #Account
       'bank_account_id': fields.many2one('res.partner.bank', 'Bank Account Number', domain="[('partner_id','=',address_home_id)]", help="Employee bank salary account"),
       'address_home_id': fields.many2one('res.partner', 'Home Address', required=True),
       'journal_salary_id':fields.many2one('account.journal', 'Journal', required=True),
       'debit_account_id': fields.many2one('account.account', 'Debit Account', required=True),
       'credit_account_id': fields.many2one('account.account', 'Credit Account', required=True),
       'leaves_counts': fields.function(_leaves_count, type='integer', string='Leaves'),
       'is_boolean':fields.boolean('Is Boolean'),     
       'resumption_date':fields.date('Resumption Date'),
               }
    _defaults = {
                  'is_boolean':_default_value,
               }
               
    

    def create(self, cr, uid, vals, context=None):
        branch = vals.get('branch_id')
        branch_obj = self.pool.get('company.branch')
        emp_sr = self.search(cr, uid, [('branch_id', '=', branch)], context=context)
        if emp_sr:
            emp = self.browse(cr, uid, emp_sr[0])
            br = branch_obj.browse(cr, uid, emp.branch_id.id)
            cr.execute('''
                      select lpad(
                             cast(max(cast(reverse(substring(reverse(he.emp_code) from 1 for 5)) as int)) + 1 as char)
                            ,5,'0')
                      from hr_employee he join company_branch cb on cb.id = he.branch_id
                      where cb.code='%s'
                       ''' % (br.code))
            branc = cr.fetchall()
            vals.update({'emp_code': str(br.code) + str(branc[0][0])})
        else:
            bran = branch_obj.browse(cr, uid, branch)
            vals.update({'emp_code': str(bran.code) + '0001'})
        return super(hr_employee_inherit, self).create(cr, uid, vals, context=context)

    def onchange_account_id(self, cr, uid, ids,account_id,context):
        if account_id and ids:
            cr.execute("""select id from analytic_employee_line where employee_id = %d"""%(ids[0]))
            empl=cr.fetchall()
            if not empl:
               res={
                    'employee_id':ids[0],
                    'analytic_id':account_id,
                    }
               self.pool.get('analytic.employee.line',self).create(cr,uid,res,context=context)
    
                
hr_employee_inherit()              

class hr_employee_leave(osv.osv):
    _name = 'hr.employee.leave'
    _columns = {
           'name':fields.char('Days', size=10, required=True),  
               }
hr_employee_leave()

class public_holiday(osv.osv):
    _name = 'public.holiday'
    _columns = { 
            'name': fields.char('Description', size=64),
            'date': fields.date('Date'),
            }

public_holiday()

class company_branch(osv.osv):
    _name = 'company.branch'
    _columns = {
         'name': fields.char('Company Name', size=64, required=True),
         'code': fields.char('Company Code', size=64, required=True),
         'street': fields.char('Street'),
         'street2': fields.char('Street2'),
         'zip': fields.char('Zip', size=24, change_default=True),
         'city': fields.char('City'),
         'state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
         'country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
         'email': fields.char('Email'),
         'website': fields.char('Website', size=60),
         'phone1': fields.char('Phone1', size=20),
         'phone2': fields.char('Phone2', size=20),
         'phone3': fields.char('Phone3', size=20),
         'tradeno':fields.char('Trade Lience No', size=20),
         'tidate':fields.date('TL Issue Date'),
         'tedate':fields.date('TL Expiry Date'),
         'trdate':fields.date('TL Reminder Date'),
         'ccno':fields.char('C.Commerce No', size=20),
         'ccidate':fields.date('CC Issue Date'),
         'ccedate':fields.date('CC Expiry Date'),
         'ccrdate':fields.date('CC Reminder Date'),
         
          }
          
company_branch()
