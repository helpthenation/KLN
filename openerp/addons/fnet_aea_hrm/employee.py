from openerp.osv import fields, osv
import datetime 
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

class hr_contract(osv.osv):

    _inherit = 'hr.contract'


    def _payment_term(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.advance_amount and line.monthly_deduction:
                res[line.id] = round(line.advance_amount/line.monthly_deduction)
        return res
        
    _columns={        
        'advance_amount':fields.float('Salary Advance'),
        'loan_date':fields.date('Loan Date'),
        'loan_detect':fields.boolean('Detect Loan Amount'),
        'monthly_deduction':fields.float('Monthly Deduction',default=0.0),
        'payment_term':fields.function(_payment_term, string='Payment Term',type='float',digits_compute=dp.get_precision('Discount'),store=True,help='Total number of month to pay for Loan amount'),
        'lunch_expense':fields.float('Lunch Expense'),
        'tax_deuduction':fields.float('Income Tax deduction'),
        'other_deduction_1':fields.float('Other deduction 1'),
        'other_deduction_2':fields.float('Other deduction 2'),
        'hra':fields.float('HRA'),
        'special_allowance':fields.float('Special Allowance'),
        'conveyance':fields.float('Conveyance Allowance'),
        'leave_allowance':fields.float('Leave Allowance'),
        'medical_allowance':fields.float('Medical Allowance'),
        'company_id':fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }
    
    def create(self, cr, uid, vals, context=None):     
        wage_amount=0.0
        if vals.get('basic') and vals.get('hra') and vals.get('special_allowance'):
            wage_amount=vals.get('basic') + vals.get('hra') + vals.get('special_allowance')
            if vals.get('basic') + vals.get('hra') + vals.get('special_allowance') < 21000:
                vals.update({'is_esi':True})
            else:
                vals.update({'is_esi':False}) 
        elif vals.get('wage') != 0.0:
            if vals.get('wage') < 21000:
                vals.update({'is_esi':True})
            else:
                vals.update({'is_esi':False})                   
        print'VALSSSSSSSSSSSSSSSSSSSSSSSSSSSs',vals   
        vals.update({'wage':wage_amount})          
        res=super(hr_contract, self).create(cr, uid, vals, context=context)
        return res   
               
class hr_payslip(osv.osv):
    
    _inherit='hr.payslip'
    
    _columns={
        'lop':fields.float('LOP',readonly=True),
        'no_of_days':fields.float('No of days',readonly=True),
    }

            
    def create(self, cr, uid, vals, context=None):
        from_dt = datetime.strptime(vals.get('date_from'), '%Y-%m-%d')
        to_dt = datetime.strptime(vals.get('date_to'), '%Y-%m-%d')
        delta=to_dt-from_dt
        emp_id=vals.get('employee_id')
        holiday_rec=self.pool.get('hr.holidays')
        holiday_id=holiday_rec.search(cr,uid,[('holiday_status_id','=',4),('date_to','>=',vals.get('date_from')),('date_to','<=',vals.get('date_to')),('employee_id','=',emp_id)],context=context)
        rec=holiday_rec.browse(cr,uid,holiday_id,context=context)
        lop=0.0
        for val in rec:
            lop=lop+val.number_of_days_temp
        vals.update({'lop':lop,'no_of_days':delta.days+1})
        new_id = super(hr_payslip, self).create(cr, uid, vals, context=context)
        return new_id
        
    def hr_verify_sheet(self,cr,uid,ids,context=None):
        print'############################'
        new_id = super(hr_payslip, self).hr_verify_sheet(cr, uid,ids,context=context)
        for payslip in self.browse(cr, uid, ids, context=context):
            mon_pay = datetime.strptime(payslip.date_from,'%Y-%m-%d').month
            contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            contract_val=self.pool.get('hr.contract')
            contract_rec=contract_val.browse(cr,uid,contract_ids,context=context)
            new_adv=0.0
            new_term=0.0
            if contract_rec.advance_amount >0 and contract_rec.payment_term > 0:
                new_adv=contract_rec.advance_amount-contract_rec.monthly_deduction
                new_term=new_term-1
                contract_val.write(cr, uid, contract_ids, {'advance_amount': new_adv, 'payment_term': new_term,}, context=context)    
            if mon_pay in [3,9]:
                if contract_rec.wage >= 21000:
                    contract_val.write(cr, uid, contract_ids, {'is_esi':False}, context=context)   
            if contract_rec.is_arrear:
                    contract_val.write(cr, uid, contract_ids, {'is_arrear':False,'salary_arrear':0.0,'previous_arrear':contract_rec.salary_arrear}, context=context)              
        return self.write(cr, uid, ids, {'state': 'verify'}, context=context)
        
    def cancel_sheet(self, cr, uid, ids, context=None):
        rec=super(hr_payslip, self).cancel_sheet(cr, uid,ids,context=context)
        for payslip in self.browse(cr, uid, ids, context=context):
            contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            contract_val=self.pool.get('hr.contract')
            contract_rec=contract_val.browse(cr,uid,contract_ids,context=context)
            new_adv=0.0
            new_term=0.0
            if contract_rec.advance_amount > 0 and contract_rec.payment_term > 0:
                new_adv=contract_rec.advance_amount+contract_rec.monthly_deduction
                new_term=new_term+1
                contract_val.write(cr, uid, contract_ids, {'advance_amount': new_adv, 'payment_term': new_term,}, context=context)
        #~ for payslip in self.browse(cr, uid, ids, context=context).line_ids:
              
        return rec

    def refund_sheet(self, cr, uid, ids, context=None):
        rec=super(hr_payslip, self).refund_sheet(cr, uid,ids,context=context)
        obj=self.browse(cr, uid, ids, context=context)
        for payslip in self.browse(cr, uid, ids, context=context).line_ids:
            print'%%%%%%%%%%%%%%%%%%%%',payslip.amount
            if payslip.code=='ARR' and payslip.amount > 0.0:
                contract_val=self.pool.get('hr.contract')
                contract_val.write(cr,uid,obj.contract_id.id,{'is_arrear':True,'salary_arrear':payslip.amount}, context=context)
        return rec      
class hr_employee(osv.osv):
    
    _inherit='hr.employee'
    
    _columns={
        'tkn_no':fields.char('Tkn.No'),
        'uan_no':fields.char('UAN No'),
        'aadhar_no':fields.char('Aadhar No'),
        'pan_no':fields.char('PAN No'),
        'pf_no':fields.char('P.F.No'),
        'esi_no':fields.char('E.S.I.No'),
        'father_name':fields.char('F/H Name'),
        'date_of_joining':fields.date('D.O.J'),
        'emp_code':fields.char('Employee Code'),
        'emp_street':fields.char('Street'),
        'emp_street1':fields.char('Street2'),
        'emp_country':fields.many2one('res.country','Country'),
        'emp_state':fields.many2one('res.country','State'),
        'emp_zip':fields.char('ZIP',size=24),
        'emp_city': fields.char('City'),       
        'company_id':fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }
    
    
class hr_payslip_run(osv.osv):
    
    _inherit='hr.payslip.run'
    
   
    _columns={    
        'company_id': fields.many2one('res.company', 'Company'),
    }   

    _defaults = {
        'company_id': lambda self, cr, uid, context: \
                self.pool.get('res.users').browse(cr, uid, uid,
                    context=context).company_id.id,
    }    
