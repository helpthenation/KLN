from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
class hr_loan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _description= "HR Loan Request"
    
    
    @api.one        
    def _compute_amount(self):
        total_paid_amount = 0.00
        for loan in self:
            for line in loan.loan_line_ids:
                if line.paid == True:
                    total_paid_amount +=line.paid_amount
            
            balance_amount =loan.loan_amount - total_paid_amount
            self.total_amount = loan.loan_amount
            self.balance_amount = balance_amount
            self.total_paid_amount = total_paid_amount
            
    @api.multi
    @api.depends('employee_id.contract_ids')
    def _get_employee_basic(self):
         for rec in self:
            for val in rec.employee_id.contract_ids:
                rec.emp_salary = val.gross * 0.6                
    #~ @api.one
    #~ def _get_old_loan(self):
        #~ old_amount = 0.00
        #~ for loan in self.search([('employee_id','=',self.employee_id.id)]):
            #~ if loan.id != self.id:
                #~ old_amount += loan.balance_amount
        #~ self.loan_old_amount = old_amount
        
    name = fields.Char(string="Loan Name", default="/", readonly=True)
    date = fields.Date(string="Loan Date Request", default=fields.Date.today(), readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    parent_id = fields.Many2one('hr.employee', related= "employee_id.parent_id", string="Manager")
    department_id = fields.Many2one('hr.department',readonly=True, string="Department")
    job_id = fields.Many2one('hr.job', readonly=True, string="Job Position")
    sponsor_id = fields.Many2one('company.branch', readonly=True, string="Sponsor ID")
    emp_code = fields.Char(readonly=True, string="Employee Code")
    emp_salary = fields.Float(string="Employee Salary",compute='_get_employee_basic', readonly=True,store=True)
    #~ loan_old_amount = fields.Float(string="Old Loan Amount Not Paid", compute='_get_old_loan')
    loan_amount = fields.Float(string="Loan Amount", required=True)
    total_amount = fields.Float(string="Total Amount", readonly=True, compute='_compute_amount')
    balance_amount = fields.Float(string="Amount To Pay", compute='_compute_amount')
    total_paid_amount = fields.Float(string="Amount Paid", compute='_compute_amount')
    no_month = fields.Integer(string="Payment Duration", default=1)
    payment_start_date = fields.Date(string="Payment Start Date", required=True, default=fields.Date.today())
    payment_end_date = fields.Date(string="Payment End Date", required=True,)
    loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', string="Loan Line", index=True)
    entry_count = fields.Integer(string="Entry Count", compute = 'compute_entery_count')
    move_id = fields.Many2one('account.move', string="Entry Journal", readonly=True)
    payment_method = fields.Many2one('loan.payments','Payment Method',help='Payment method for loan')
    is_journal_generated = fields.Boolean('Journal Created',default=False)
    state = fields.Selection([
        ('draft','Draft'),
        ('hr_approved','HR Approval'),
        ('approve','Manager Approval'),
        ('cancel','Rejected'),
        ('done','Sanctioned'),
    ], string="State", default='draft', track_visibility='onchange', copy=False,)
    

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.loan.req') or ' '
        emp_id = vals.get('employee_id')
        contract_obj = self.env['hr.contract']
        emp_obj = self.env['hr.employee']
        search_contract = contract_obj.search([('employee_id', '=', emp_id)])
        if not search_contract:
            raise except_orm('Error!', 'Define a contract for the employee')
        for each_contract in search_contract:
            if not each_contract.max_percent:
                raise except_orm('Error!', 'Max percentage or advance days are not provided')       
            adv = vals.get('loan_amount') 
            basic = vals.get('emp_salary')   
            amt = (each_contract.max_percent * basic) / 100
            if adv > basic:
                raise except_orm('Error!', 'Loan amount is greater than Basic Amount!!!')
            if adv > amt:
                raise except_orm('Error!', 'Loan amount is greater than allotted')                                                 
        
        loan_date = vals.get('date')
        all_loans = self.search([('employee_id','=',emp_id)])
        if all_loans:
            all_loan_ids = []
            for i in all_loans:
                all_loan_ids.append(i.id)
            loan_lines = self.env['hr.loan.line'].search([('loan_id','in',all_loan_ids)]) 
            for line in loan_lines:
                loan_obj=self.env['hr.loan.line'].browse(line.id)
                if loan_date <= loan_obj.paid_date:
                    raise except_orm('Error!',
                        'There is a loan in progress '+ str(loan_obj.loan_id.name))
        res = super(hr_loan, self).create(vals)
        return res
        
    @api.multi
    def write(self, vals):
        emp_id = self.employee_id.id
        loan_amount = self.loan_amount
        emp_salary = self.emp_salary
        if 'employee_id' in vals:
            emp_id = vals.get('employee_id')
        if 'loan_amount' in vals:
            loan_amount = vals.get('loan_amount')
        if 'emp_salary' in vals:
            emp_salary = vals.get('emp_salary')            
        contract_obj = self.env['hr.contract']
        search_contract = contract_obj.search([('employee_id', '=', emp_id)])
        if not search_contract:
            raise except_orm('Error!', 'Define a contract for the employee')
        for each_contract in search_contract:
            if not each_contract.max_percent:
                raise except_orm('Error!', 'Max percentage or advance days are not provided')       
            amt = (each_contract.max_percent * emp_salary) / 100
            if loan_amount > emp_salary:
                raise except_orm('Error!', 'Loan amount is greater than Basic Amount!!!')
            if loan_amount > amt:
                raise except_orm('Error!', 'Loan amount is greater than allotted')                                                  
        res = super(hr_loan, self).write(vals)
        return res      
              
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel'):
                raise except_orm('Error!' ,'You can not delete a loan request which not in Draft or Cancel State')                 
        return super(hr_loan, self).unlink()
            
    @api.one
    def check_previous_loans_payments(self):
        current_loan = self.browse(ids)[0]
        loan_date = current_loan.start_date
        all_loans = self.search(cr ,uid ,[('employee_id','=',current_loan.employee_id.id),('id','!=',ids[0])])
        if all_loans:
            loan_lines = self.pool.get('hr.loan.line').search(cr ,uid ,[('loan_id','in',all_loans)]) 
            for line in self.pool.get('hr.loan.line').browse(cr ,uid ,loan_lines):
                if loan_date <= line.discount_date:
                    raise osv.except_osv(_('Error!'),
                        _('There is a loan in progress '+ str(line.loan_id.name)))
                        
                         
    @api.one
    def action_submit(self):
        self.state = 'hr_approved'   

    @api.one
    def action_forward(self):
        self.state = 'approve'   
                 
    @api.one
    def action_refuse(self):
        self.state = 'cancel'
        contract_obj = self.env['hr.contract']
        if self.move_id:
            self.env.cr.execute("delete from account_move_line where move_id =%d"%(self.move_id.id))
            self.env.cr.execute("delete from account_move where id =%d"%(self.move_id.id))
        for loan in self:
            if loan.loan_amount <= 0:
                raise except_orm(_('Error!'),
                                    _('Please Set Amount'))             
            if loan.employee_id.contract_id:
                contract_id=contract_obj.browse(loan.employee_id.contract_id.id)
                vals={
                    'loan_amount':0,
                    'balance_amount':0,
                    'total_paid_amount':0,
                    'no_month':0,
                    'is_loan_completed':False,      
                }
                contract_id.write(vals)
                rule = self.env['mline.payroll.rule']
                loan_rule = rule.search([('code', '=', 'LOAN')])
                contract_vals={
                        'contract_id': contract_id.id,
                        'rule_id':loan_rule.id,
                        'amount': -(round(float(loan.loan_amount) / loan.no_month)),              
                }   
                sal_id=self.env['hr.contract.line'].search([('contract_id', '=', contract_id.id),('rule_id','=',loan_rule.id)],limit=1, order='id desc')
                if sal_id:                                                   
                    sal_id.unlink()        
        
    @api.one
    def action_set_to_draft(self):
        self.state = 'draft'
        contract_obj = self.env['hr.contract']
        if self.move_id:
            self.env.cr.execute("delete from account_move_line where move_id =%d"%(self.move_id.id))
            self.env.cr.execute("delete from account_move where id =%d"%(self.move_id.id))
        for loan in self:
            if loan.loan_amount <= 0:
                raise except_orm(_('Error!'),
                                    _('Please Set Amount'))             
            if loan.employee_id.contract_id:
                contract_id=contract_obj.browse(loan.employee_id.contract_id.id)
                vals={
                    'loan_amount':0,
                    'balance_amount':0,
                    'total_paid_amount':0,
                    'no_month':0,
                    'is_loan_completed':False,      
                }
                contract_id.write(vals)
                rule = self.env['mline.payroll.rule']
                loan_rule = rule.search([('code', '=', 'LOAN')])
                contract_vals={
                        'contract_id': contract_id.id,
                        'rule_id':loan_rule.id,
                        'amount': -(round(float(loan.loan_amount) / loan.no_month)),              
                }   
                sal_id=self.env['hr.contract.line'].search([('contract_id', '=', contract_id.id),('rule_id','=',loan_rule.id)],limit=1, order='id desc')
                if sal_id:                                                   
                    sal_id.unlink()                   
    
    @api.onchange('payment_start_date','no_month')
    def _onchange_start_date(self):
        if self.payment_start_date and self.no_month:
            self.payment_end_date = datetime.strptime(self.payment_start_date,'%Y-%m-%d') + relativedelta(months=+self.no_month-1)            
    

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        old_amount = 0.00
        if self.employee_id:    
                self.job_id = self.employee_id.job_id.id
                self.sponsor_id = self.employee_id.branch_id.id
                self.emp_code = self.employee_id.emp_code
                self.department_id = self.employee_id.department_id.id
        else:
                self.job_id = False
                self.sponsor_id = False
                self.emp_code = False
                self.department_id = False         
            #~ for loan in self.search([('employee_id','=',employee_id)]):
                #~ if loan.id != self.id:
                    #~ old_amount += loan.balance_amount
            #~ return {
                #~ 'value':{
                    #~ 'loan_old_amount':old_amount}
            #~ }

            
    @api.one
    def action_approve(self):
        self.state = 'done'
        if not self.payment_method:
            raise except_orm('Warning', "Please Set Payment Method")
        if not self.loan_line_ids:
            raise except_orm('Warning', 'You must compute Loan Request before Approved')
        can_close = False
        loan_obj = self.env['hr.loan']
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        contract_obj = self.env['hr.contract']
        created_move_ids = []
        loan_ids = []
        for loan in self:
            if loan.loan_amount <= 0:
                raise except_orm(_('Error!'),
                                    _('Please Set Amount'))             
            if loan.employee_id.contract_id:
                contract_id=contract_obj.browse(loan.employee_id.contract_id.id)
                vals={
                    'loan_amount':loan.loan_amount,
                    'balance_amount':loan.balance_amount,
                    'total_paid_amount':loan.total_paid_amount,
                    'no_month':loan.no_month,
                    'is_loan_completed':True,      
                }
                contract_id.write(vals)
                rule = self.env['mline.payroll.rule']
                loan_rule = rule.search([('code', '=', 'LOAN')])
                contract_vals={
                        'contract_id': contract_id.id,
                        'rule_id':loan_rule.id,
                        'amount': -(round(float(loan.loan_amount) / loan.no_month)),              
                }   
                sal_id=self.env['hr.contract.line'].search([('contract_id', '=', contract_id.id),('rule_id','=',loan_rule.id)],limit=1, order='id desc')
                if not sal_id:                                                   
                    self.env['hr.contract.line'].create(contract_vals)       
                elif sal_id:
                    sal_id.write(contract_vals)    
        return True
    
    @api.one        
    def action_generate_journal(self):  
        if not self.payment_method:
            raise except_orm('Warning', "Please Set Payment Method")
        if not self.loan_line_ids:
            raise except_orm('Warning', 'You must compute Loan Request before Approved')
        if self.move_id:
            raise except_orm('Warning', 'Journal Entry Already Generated!!!')
        can_close = False
        loan_obj = self.env['hr.loan']
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        contract_obj = self.env['hr.contract']
        created_move_ids = []
        loan_ids = []
        for loan in self:
            loan_request_date = loan.date
            period_ids =period_obj.with_context().find(loan_request_date).id
            company_currency = loan.employee_id.company_id.currency_id.id
            current_currency = self.env.user.company_id.currency_id.id
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.payment_method.journal_id.id
            if amount <= 0:
                raise except_orm(_('Error!'),
                                    _('Please Set Amount'))         
            move_vals = {
                'name': loan_name,
                'date': loan_request_date,
                'ref': reference,
                'period_id': period_ids or False,
                'journal_id': journal_id,
                'state': 'posted',
                }
            move_id = move_obj.create(move_vals)
            move_line_vals = {
                'name': loan_name,
                'ref': reference,
                'move_id': move_id.id,
                'account_id': loan.payment_method.debit_account_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids or False,
                'journal_id': journal_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency':  0.0,
                'date': loan_request_date,
                'analytic_account_id': loan.payment_method.analytic_account_id.id or False,
            }
            move_line_obj.create(move_line_vals)
            move_line_vals2 = {
                'name': loan_name,
                'ref': reference,
                'move_id': move_id.id,
                'account_id': loan.payment_method.credit_account_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids or False,
                'journal_id': journal_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': 0.0,
                'date': loan_request_date,
                'analytic_account_id':False
            }
            move_line_obj.create(move_line_vals2)            
            self.write({'move_id': move_id.id,'is_journal_generated':True})           
    
    @api.multi
    def compute_loan_line(self):
        loan_line = self.env['hr.loan.line']
        loan_line.search([('loan_id','=',self.id)]).unlink()
        for loan in self:
            date_start_str = datetime.strptime(loan.payment_start_date,'%Y-%m-%d')
            counter = 1
            amount_per_time = loan.loan_amount / loan.no_month
            for i in range(1, loan.no_month + 1):
                line_id = loan_line.create({
                    'paid_date':date_start_str, 
                    'paid_amount': amount_per_time,
                    'employee_id': loan.employee_id.id,
                    'loan_id':loan.id})
                counter += 1
                date_start_str = date_start_str + relativedelta(months = 1)                
        return True
    

    @api.model
    @api.multi
    def compute_entery_count(self):
        count = 0
        entry_count = self.env['account.move.line'].search_count([('loan_id','=',self.id)])
        self.entry_count = entry_count
    
    @api.multi
    def button_reset_balance_total(self):
        total_paid_amount = 0.00
        for loan in self:
            for line in loan.loan_line_ids:
                if line.paid == True:
                    total_paid_amount +=line.paid_amount
            balance_amount =loan.loan_amount - total_paid_amount
            self.write({'total_paid_amount':total_paid_amount,'balance_amount':balance_amount})
            
            
class hr_loan_line(models.Model):
    _name="hr.loan.line"
    _description = "HR Loan Request Line"
    
    
    paid_date = fields.Date(string="Payment Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    paid_amount= fields.Float(string="Paid Amount", required=True)
    paid = fields.Boolean(string="Paid")
    notes = fields.Text(string="Notes")
    loan_id =fields.Many2one('hr.loan', string="Loan Ref.", ondelete='cascade')
    payroll_id = fields.Many2one('mline.payroll', string="Payslip Ref.")
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.paid == True:
                raise except_orm('Error!' ,'You can not delete loan line which was paided')
        return super(hr_loan_line, self).unlink()
            
    @api.one
    def action_paid_amount(self):
        context = self._context
        can_close = False
        loan_obj = self.env['hr.loan']
        period_obj = self.env['account.period']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        created_move_ids = []
        loan_ids = []
        for line in self:
            if line.loan_id.state != 'done':
                raise except_orm('Warning', "Loan Request must be approved")
            #~ paid_date = line.paid_date
            #~ period_ids =period_obj.with_context().find(paid_date).id
            #~ company_currency = line.employee_id.company_id.currency_id.id
            #~ current_currency = self.env.user.company_id.currency_id.id
            #~ amount = line.paid_amount
            #~ loan_name = line.employee_id.name
            #~ reference = line.loan_id.name
            #~ journal_id = line.loan_id.journal_id.id
            #~ move_vals = {
                #~ 'name': loan_name,
                #~ 'date': paid_date,
                #~ 'ref': reference,
                #~ 'period_id': period_ids or False,
                #~ 'journal_id': journal_id,
                #~ 'state': 'posted',
                #~ }
            #~ move_id = move_obj.create(move_vals)
            #~ move_line_vals = {
                #~ 'name': loan_name,
                #~ 'ref': reference,
                #~ 'move_id': move_id.id,
                #~ 'account_id': line.loan_id.emp_account_id.id,
                #~ 'debit': 0.0,
                #~ 'credit': amount,
                #~ 'period_id': period_ids or False,
                #~ 'journal_id': journal_id,
                #~ 'currency_id': company_currency != current_currency and  current_currency or False,
                #~ 'amount_currency':  0.0,
                #~ 'date': paid_date,
                #~ 'loan_id':line.loan_id.id,
            #~ }
            #~ move_line_obj.create(move_line_vals)
            #~ move_line_vals2 = {
                #~ 'name': loan_name,
                #~ 'ref': reference,
                #~ 'move_id': move_id.id,
                #~ 'account_id': line.loan_id.treasury_account_id.id,
                #~ 'credit': 0.0,
                #~ 'debit': amount,
                #~ 'period_id': period_ids or False,
                #~ 'journal_id': journal_id,
                #~ 'currency_id': company_currency != current_currency and  current_currency or False,
                #~ 'amount_currency': 0.0,
                #~ 'date': paid_date,
                #~ 'loan_id':line.loan_id.id,
            #~ }
            #~ move_line_obj.create(move_line_vals2)
            self.write({'paid': True})
        return True
        
    
    
    
class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    @api.model
    @api.multi
    def _compute_loans(self):
        count = 0
        loan_remain_amount = 0.00
        loan_ids = self.env['hr.loan'].search([('employee_id','=',self.id),('state','=','done')])
        for loan in loan_ids:
            loan_remain_amount +=loan.balance_amount
            count +=1
        self.loan_count = count
        self.loan_amount = loan_remain_amount
    
    
    loan_amount= fields.Float(string="loan Amount", compute ='_compute_loans')
    loan_count = fields.Integer(string="Loan Count", compute = '_compute_loans')
    
    
class account_move_line(models.Model):
    _inherit = "account.move.line"
    
    loan_id = fields.Many2one('hr.loan', string="Loan")
    
    
class loans_payments(models.Model):
    _name = "loan.payments"
    
    name = fields.Char('Name', required=True,help='Payment name')
    debit_account_id = fields.Many2one('account.account','Debit Account', required=True,help='Debit account for journal entry')
    credit_account_id = fields.Many2one('account.account','Credit Account', required=True,help='Credit account for journal entry')
    journal_id = fields.Many2one('account.journal','Journal', required=True,help='Journal for journal entry')
    analytic_account_id = fields.Many2one('account.analytic.account','Analytic Account',help='Analytic account for journal entry')
            
