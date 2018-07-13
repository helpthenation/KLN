from datetime import datetime
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, tools, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import math
import csv
import calendar
    
class HrEMployee(models.Model):
    _inherit = 'hr.employee'
    
    date_of_joining  = fields.Date('DOJ.')

class HrContract(models.Model):
   
    _inherit='hr.contract'

    basic=fields.Float('Basic')
    tds=fields.Float('TDS')
    loan_deduction=fields.Float('Loan Deduction')
    gross=fields.Float('Gross')
    is_arrear=fields.Boolean("Is Arrear",default=False)
    is_esi=fields.Boolean("Is ESI")
    active=fields.Boolean('Active',default=True)
    pt=fields.Float('PT', digits=(16, 2))
    hra=fields.Float('HRA', digits=(16, 2))
    effective_date=fields.Date('Effective Date',readonly=True)
    history_line=fields.One2many('salary.history.line','contract_id','Salary History')
    salary_arrear=fields.Float('Salary Arrear', digits=(16,2),readonly=True)
    previous_arrear=fields.Float('Previous Salary Arrear', digits=(16,2),readonly=True)

    @api.onchange('basic','hra','special_allowance')
    def _onchange_gross(self):
        print"selffffffffffffff",self
        if self.basic or self.hra or self.special_allowance != 0:
            self.gross=self.basic+self.hra+self.special_allowance
            self.wage=self.basic+self.hra+self.special_allowance
                
class salary_history_line(models.Model):
    _name='salary.history.line'
    
    old_basic=fields.Char('Basic Percentage')
    old_wage=fields.Float('Wages', digits=(16, 2))
    old_gross=fields.Float('Gross', digits=(16, 2))
    old_stucture_id=fields.Many2one('hr.payroll.structure','Payroll Structure')
    contract_id=fields.Many2one('hr.contract','Contract')
    special_allowance = fields.Float('Special Allowance')
    conveyance = fields.Float('Conveyance Allowance')
    leave_allowance = fields.Float('Leave Allowance')
    medical_allowance = fields.Float('Medical Allowance')
    pt = fields.Float('PT')
    hra = fields.Float('HRA')
    #~ bonus = fields.Float('Bonus')
    tds_deduction = fields.Float('TDS')
    lunch_expense = fields.Float('Lunch Deduction')
    other_deduction_1 = fields.Float('Other Deduction1')
    other_deduction_2 = fields.Float('Other Deduction2')
    tax_deuduction = fields.Float('Income Tax deduction')
    
class salary_revision (models.Model):
    _name='salary.revision'
    
    basic=fields.Char('Basic Percentage')
    wage=fields.Float('Wages', digits=(16, 2))
    gross=fields.Float('Gross', digits=(16, 2))
    effective_date=fields.Date('Effective Date')
    stucture_id=fields.Many2one('hr.payroll.structure','Payroll Structure')
    contract_id=fields.Many2one('hr.contract','Contract')
    special_allowance = fields.Float('Special Allowance')
    conveyance = fields.Float('Conveyance Allowance')
    leave_allowance = fields.Float('Leave Allowance')
    medical_allowance = fields.Float('Medical Allowance')
    pt = fields.Float('PT')
    hra = fields.Float('HRA')
    #~ bonus = fields.Float('Bonus')
    tds_deduction = fields.Float('TDS')
    lunch_expense = fields.Float('Lunch Deduction')
    other_deduction_1 = fields.Float('Other Deduction1')
    other_deduction_2 = fields.Float('Other Deduction2')
    tax_deuduction = fields.Float('Income Tax deduction')
    
    @api.model
    def default_get(self, fields):
        print"DDDDDDDDDDDDD"
        rec = super(salary_revision, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        print self,fields,rec,active_model,active_ids
        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))

        # Checks on received invoice records
        contract = self.env[active_model].browse(active_ids)
        print"KSKSKSKSKSKSKSKSKSKSKSKSKSKSKS",contract
        print'{0:.4f}'.format(contract.basic)
        rec.update({
            'basic': contract.basic,
            'wage': contract.wage,
            'gross':contract.gross,
            'hra':contract.hra,
            'special_allowance':contract.special_allowance,
            'conveyance':contract.conveyance,
            'leave_allowance':contract.leave_allowance,
            'medical_allowance':contract.medical_allowance,
            'lunch_expense':contract.lunch_expense,
            'tax_deuduction':contract.tax_deuduction,
            'other_deduction_1':contract.other_deduction_1,
            'other_deduction_2':contract.other_deduction_2,
            'tds_deduction':contract.tds,
            'effective_date': '',
            'stucture_id': contract.struct_id.id,
            'contract_id': contract.id,
        })
        return rec
        
    @api.multi
    def update_salary(self):
        print"LLLLLLLLLLLLL"
        lines=[]
        lines.append((0,0,{
                        'old_basic':self.contract_id.basic,
                        'old_wage':self.contract_id.wage,
                        'old_gross':self.contract_id.gross,
                        'contract_id':self.contract_id.id,
                        'old_stucture_id':self.contract_id.struct_id.id,
                        'special_allowance':self.contract_id.special_allowance,
                        'conveyance':self.contract_id.conveyance,
                        'leave_allowance':self.contract_id.leave_allowance,
                        'medical_allowance':self.contract_id.medical_allowance,
                        #~ 'pt':self.contract_id.pt,
                        'hra':self.contract_id.hra,
                        #~ 'bonus':self.contract_id.bonus,
                        'lunch_expense':self.contract_id.lunch_expense,
                        'tax_deuduction':self.contract_id.tax_deuduction,
                        'other_deduction_1':self.contract_id.other_deduction_1,
                        'tds_deduction':self.contract_id.tds,
                        'other_deduction_2':self.contract_id.other_deduction_2,
                        #~ 'other_deduction':self.contract_id.other_deduction,
                           }))
        print lines
        vals={
              'history_line':lines,
              }
        self.contract_id.write(vals)
        self.contract_id.basic=self.basic
        self.contract_id.wage=self.wage
        self.contract_id.struct_id=self.stucture_id.id
        self.contract_id.effective_date=self.effective_date
        self.contract_id.special_allowance = self.special_allowance
        self.contract_id.conveyance = self.conveyance
        self.contract_id.leave_allowance = self.leave_allowance
        self.contract_id.medical_allowance = self.medical_allowance
        self.contract_id.hra= self.hra
        self.contract_id.lunch_expense = self.lunch_expense
        self.contract_id.tds = self.tds_deduction
        self.contract_id.tax_deuduction = self.tax_deuduction
        self.contract_id.other_deduction_1 = self.other_deduction_1        
        self.contract_id.other_deduction_2 = self.other_deduction_2        
        #~ if self.pt:
            #~ self.contract_id.write({'is_pt': True})
        #~ else:
            #~ self.contract_id.write({'is_pt': False})
        #~ self.contract_id.pt = self.pt
        #~ if self.hra:
            #~ self.contract_id.write({'is_hra': True})
        #~ else:
            #~ self.contract_id.write({'is_hra': False})
        #~ self.contract_id.hra = self.hra
        #~ if self.bonus:
            #~ self.contract_id.write({'is_bonus': True})
        #~ else:
            #~ self.contract_id.write({'is_bonus': False})
        #~ self.contract_id.bonus = self.bonus
        #~ if self.medical:
            #~ self.contract_id.write({'is_medical': True})
        #~ else:
            #~ self.contract_id.write({'is_medical': False})
        #~ self.contract_id.medical = self.medical
        #~ if self.conveyance:
            #~ self.contract_id.write({'is_convayance':True})
        #~ else:
            #~ self.contract_id.write({'is_convayance': False})
        #~ self.contract_id.convanyance = self.conveyance
        #~ if self.other:
            #~ self.contract_id.write({'is_other': True})
        #~ else:
            #~ self.contract_id.write({'is_other': False})

