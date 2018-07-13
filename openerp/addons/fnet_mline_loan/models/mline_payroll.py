from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.osv import osv

class mline_payroll(osv.osv):
    _inherit = 'mline.payroll'

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False, payslip_type=False,context=None):
        res = super(mline_payroll,self).onchange_employee_id(cr, uid, ids, date_from, date_to, employee_id=employee_id, contract_id=contract_id, context=context)
        loan_obj = self.pool.get('hr.loan')
        loan_line_obj = self.pool.get('hr.loan.line')
        loan_ids = loan_obj.search(cr ,uid ,[('employee_id','=',employee_id),('state','=','done'),])
        loan_total = 0.0
        print'LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL',loan_ids
        input_ids=[]
        if payslip_type == 'general':
            if loan_ids:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search(cr ,uid ,[('loan_id','=',loan_id),
                                                              #~ ('paid_date','>=',date_from),
                                                              ('paid_date','<=',date_to),
                                                              ('paid','=',False),
                                                              ])
                    if line_ids:
                        for loan in loan_line_obj.browse(cr ,uid ,line_ids):
                            loan_total = loan.paid_amount                        
                            print'LOOOOOOOOOOOOOOO',loan
                            input_ids.append((0,0,{'name': 'Loan', 'code': 'LOAN', 'amount': loan_total, 'contract_id': contract_id,'loan_id':loan.id}))
                            res['value'].update({
                                            'input_line_ids': input_ids,
                                })   
                        print'DDDDD###################',res                 
                        return res  
    #~ @api.one
    #~ def compute_total_paid_loan(self):
        #~ total = 0.00
        #~ for line in self.loan_ids:
            #~ if line.paid == True:
                #~ total += line.paid_amount
        #~ self.total_amount_paid = total
    #~ 
    #~ loan_ids = fields.One2many('hr.loan.line', 'payroll_id', string="Loans")
    #~ total_amount_paid = fields.Float(string="Total Loan Amount", compute= 'compute_total_paid_loan')
    #~ 
    #~ @api.multi
    #~ def get_loan(self):
        #~ array = []
        #~ loan_ids = self.env['hr.loan.line'].search([('employee_id','=',self.employee_id.id),('paid','=',False)]) 
        #~ for loan in loan_ids:
            #~ array.append(loan.id)
        #~ self.loan_ids = array
        #~ return array
        #~ 
    #~ @api.model
    #~ def hr_verify_sheet(self):
        #~ self.compute_sheet()
        #~ array = []
        #~ for line in self.loan_ids:
            #~ if line.paid:
                #~ array.append(line.id)
                #~ line.action_paid_amount()
            #~ else:
                #~ line.payroll_id = False
        #~ self.loan_ids = array
        #~ return self.write({'state': 'verify'})
