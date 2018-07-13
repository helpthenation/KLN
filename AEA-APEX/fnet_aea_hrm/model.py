from openerp import api, fields, models, tools, _
#~ from openerp.exceptions import UserError, ValidationError
from openerp.tools.safe_eval import safe_eval
from datetime import datetime
import math
from openerp.tools.float_utils import float_round
from openerp.addons import decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import xlsxwriter
import StringIO
import base64
from dateutil.rrule import rrule, MONTHLY
    
class salary_arrears(models.Model):
    _name = 'salary.arrear'
    _rec_name='company_id'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('arrear_cal', 'Arrear Calculation'),
        ('done', 'Done'),
        
    ], default='draft')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.user.company_id.id,readonly=True)
    from_date = fields.Date('Arrear Calculation from date')
    to_date = fields.Date('Arrear Calculation to date')
    check = fields.Boolean(string='Check the box before updating',help='set the field to True after submit button is clicked')
    employee_line_ids = fields.One2many('employee.line', 'arrear_id', string='Employees Details')
    filedata = fields.Binary('Download file', readonly=True)
    filename = fields.Char('Filename', size=64, readonly=True)
    
    @api.multi
    def update_arrears(self):
        for line in self.employee_line_ids:
            line.contract_id.write({'is_arrear':True,'salary_arrear':line.arrears})
        #self.write({'state':'done'})
        
    @api.depends('employee_line_ids')
    @api.multi
    def get_fetching(self):
        print'##################################################',self
        employee_line = self.env['employee.line']
        self.env.cr.execute("""select hr.id from hr_employee as hr
                               join resource_resource as rr on hr.resource_id = rr.id
                               join res_company as rc on rr.company_id = rc.id
                               where rc.id = %d and rr.active=true and hr.id != 1"""%(self.env.user.company_id.id))
        employee =self.env.cr.dictfetchall()
        print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',self
        #~ self.env.cr.execute('''truncate table emp_details''')
        val={}
        v=[]
        for line in employee:
            val={
                'arrear_id' : self.id,
                'employee_id': line['id'],
                'contract_id': self.env['hr.contract'].search([('employee_id','=',line['id'])]).id,
                'arrears' : 0.00,
                
                }
            print'VALLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL',val    
            v=employee_line.create(val)
        self.write({'state':'arrear_cal'})

    @api.multi
    def compute_arrears_payslip(self,line,wage,payslip):
        print'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',line,wage,payslip.employee_id.name
        net=0.0
        component_value={}
        if line.contract_id.struct_id.code == 'SSS' and payslip.id:
            #~ BASIC
            current_basic=0.0
            prev_basic=0.0          
            current_basic=line.contract_id.basic
            for slip in payslip.line_ids:
                if slip.code == 'BASICS':   
                    prev_basic=slip.amount      
            basic=current_basic-prev_basic  
            component_value.update({'basic':basic})
            #~ print'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',current_basic,prev_basic
            #~ HRA
            current_hra=0.0
            prev_hra=0.0            
            current_hra=line.contract_id.hra
            for slip in payslip.line_ids:
                if slip.code == 'HRA':   
                    prev_hra=slip.amount      
            hra=current_hra-prev_hra 
            print'HRAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa',current_hra,prev_hra 
            component_value.update({'hra':hra})
            #~ SPECIAL ALLOWANCE
            current_spa=0.0
            prev_spa=0.0            
            current_spa=line.contract_id.special_allowance
            for slip in payslip.line_ids:
                if slip.code == 'SPA':   
                    prev_spa=slip.amount      
            spa=current_spa-prev_spa
            print'SPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAaa',current_spa,prev_spa
            component_value.update({'spa':spa})
            #~ Conveyance ALLOWANCE
            current_ca=0.0
            prev_ca=0.0         
            current_ca=line.contract_id.conveyance
            for slip in payslip.line_ids:
                if slip.code == 'CA':   
                    prev_spa=slip.amount      
            ca=current_ca-prev_ca
            component_value.update({'ca':ca})
            #~ Medical ALLOWANCE
            current_ma=0.0
            prev_ma=0.0         
            current_ma=line.contract_id.medical_allowance
            for slip in payslip.line_ids:
                if slip.code == 'MA':   
                    prev_spa=slip.amount      
            ma=current_ma-prev_ma
            component_value.update({'ma':ma})
            #~ Leave ALLOWANCE
            current_la=0.0
            prev_la=0.0         
            current_la=line.contract_id.leave_allowance
            for slip in payslip.line_ids:
                if slip.code == 'LA':   
                    prev_spa=slip.amount      
            la=current_la-prev_la
            component_value.update({'la':la})
            #~ CURRENT ALLOWANCE
            #~ current_alw=hra+spa+ca+ma+la
            #~ CURRENT GROSSS
            #~ current_gross=basic+hra+spa+ca+ma+la
           #~ DEDUCTIONS
            #~ EMPLOYEE PF
            #~ current_epf=0.0            
            #~ prev_epf=0.0            
            #~ if (current_basic+current_spa) <= 15000:
                #~ current_epf=round(-(current_basic+current_spa)*0.12)
            #~ else:
                #~ if (current_basic*0.12) > 1800:
                    #~ current_epf= round(-(current_basic)*0.12)
                #~ else:
                    #~ current_epf=-1800        
            #~ for slip in payslip.line_ids:
                #~ if slip.code == 'EPF':   
                    #~ prev_epf=slip.amount      
            #~ epf=current_epf-prev_epf
            #~ print'PFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',current_epf,prev_epf
            #~ component_value.update({'epf':epf})     
            #~ EMPLOYEE ESI
            #~ current_esi = 0.0
            #~ if line.contract_id.is_esi==True:
                #~ ((line.contract_id.wage/payslip.no_of_days)*payslip.lop)
                #~ current_esi=-round(((current_basic+current_alw)*0.0175)+0.5)
            #~ prev_esi = 0.0
            #~ for slip in payslip.line_ids:
                #~ if slip.code == 'EESI':
                    #~ print slip.amount,'****',
                    #~ prev_esi = (slip.amount)
            #~ if current_esi:
                #~ esi = current_esi + prev_esi
            #~ else:
                #~ esi=prev_esi
            #~ print'ESIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII',esi, current_esi,  prev_esi 
            #~ component_value.update({'esi': esi})            
            #~ PROFESSIONAL TAX
            #~ current_pt=0.0
            #~ if line.contract_id.company_id.location_code == 'TN':
                #~ if (current_gross) < 3500:
                    #~ current_pt=-0
                #~ elif((current_gross)> 3501 and ( current_gross) < 5000):
                    #~ current_pt=-17
                #~ elif((current_gross)> 5001 and ( current_gross) < 7500):
                    #~ current_pt=-39
                #~ elif((current_gross)> 7501 and ( current_gross) < 10000):
                    #~ current_pt=-85
                #~ elif((current_gross)> 10001 and ( current_gross) < 12500):
                    #~ current_pt=-127
                #~ else:
                    #~ current_pt=-183
            #~ elif line.contract_id.company_id.location_code == 'KL':
                #~ if (current_gross) < 2000:
                    #~ current_pt=-0
                #~ elif((current_gross)>= 2000 and ( current_gross) <= 2999):
                    #~ current_pt=-20
                #~ elif((current_gross)>= 3000 and ( current_gross) <= 4999):
                    #~ current_pt=-30
                #~ elif((current_gross)>= 5000 and ( current_gross) <= 7499):
                    #~ current_pt=-50
                #~ elif((current_gross)>= 7500 and ( current_gross) <= 9999):
                    #~ current_pt=-75
                #~ elif((current_gross)>= 10000 and ( current_gross) <= 12499):
                    #~ current_pt=-100
                #~ elif((current_gross)>= 12500 and ( current_gross) <= 16667):
                    #~ current_pt=-125
                #~ elif((current_gross)>= 16668 and ( current_gross) <= 20833):
                    #~ current_pt=-167
                #~ else:
                    #~ current_pt=-209
            #~ elif line.contract_id.company_id.location_code == 'KA':
                #~ if (current_gross) <= 15000:
                    #~ current_pt=-0
                #~ else:
                    #~ current_pt=-200
            #~ elif ((line.contract_id.company_id.location_code == 'AP') or (line.contract_id.company_id.location_code == 'TL')):
                #~ if (current_gross) <= 15000:
                    #~ current_pt=-0
                #~ elif((current_gross)>15000 and ( current_gross) <= 20000):
                    #~ current_pt=-150 
                #~ else:
                    #~ current_pt=-200
            #~ elif ((line.contract_id.company_id.location_code == 'OB') or (line.contract_id.company_id.location_code == 'OS')):
                #~ if (current_gross) <= 1500:
                    #~ current_pt=-0
                #~ elif((current_gross)> 1500 and ( current_gross) <= 2000):
                    #~ current_pt=-16
                #~ elif((current_gross)> 2000 and ( current_gross) <= 3000):
                    #~ current_pt=-25
                #~ elif((current_gross)> 3000 and ( current_gross) <= 4000):
                    #~ current_pt=-35
                #~ elif((current_gross)> 4000 and ( current_gross) <= 5000):
                    #~ current_pt=-45
                #~ elif((current_gross)> 5000 and ( current_gross) <= 6000):
                    #~ current_pt=-60
                #~ elif((current_gross)> 6000 and ( current_gross) <= 10000):
                    #~ current_pt=-80
                #~ elif((current_gross)> 10000 and ( current_gross) <= 15000):
                    #~ current_pt=-100
                #~ elif((current_gross)> 15000 and ( current_gross) <= 20000):
                    #~ current_pt=-150
                #~ else:
                    #~ current_pt=-200
            #~ else:
                #~ current_pt=-0.0            
            #~ prev_pt = 0.0
            #~ for slip in payslip.line_ids:
                #~ if slip.code == 'PT':
                    #~ print slip.amount,'****'
                    #~ prev_pt = (slip.amount)    
            #~ pt=current_pt-prev_pt       
            #~ component_value.update({'pt': pt})      
            #~ NET
            net=basic+spa+hra+ma+ca+la
            component_value.update({'net': net})
            print'COMPONTENT VALUEEEEEEEEEEEEEEEEEEEEE',component_value,net
            return net,component_value                                      
        
    @api.multi
    def compute_arrears(self):
        #~ print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSS',self
        from_month = datetime.strptime(self.from_date, '%Y-%m-%d').month
        from_year = datetime.strptime(self.from_date, '%Y-%m-%d').year
        to_month = datetime.strptime(self.to_date, '%Y-%m-%d').month
        to_year = datetime.strptime(self.to_date, '%Y-%m-%d').year
        date = []
        #~ #run_time = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        output = StringIO.StringIO()
        #~ # ~ url = os.path.dirname(os.path.realpath('excel_reports'))
        url = '/home/iswasu2/Downloads/'
        #~ # ~ url = '/home/muthu/Developement/new/'
        workbook = xlsxwriter.Workbook(url+'salary_arrears.xlsx')
        worksheet = workbook.add_worksheet()
        # creation of header
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'font_size': 12,
            'font_name': 'Liberation Serif',
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'white'})
        merge_format1 = workbook.add_format({
            'align': 'left',
            'font_name': 'Liberation Serif',
            'valign': 'vcenter', })
        merge_format2 = workbook.add_format({
            'bold': 1, 'align': 'center',
            'valign': 'vcenter',
            'font_name': 'Liberation Serif',
            'underline': 'underline', })
        merge_format3 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'font_name': 'Liberation Serif',
            'valign': 'vcenter',
            'fg_color': 'gray'})

        merge_format4 = workbook.add_format({
            'align': 'right',
            'num_format': '#,##0.00',
            'font_name': 'Liberation Serif',
            'valign': 'vcenter', })
        merge_format5 = workbook.add_format({
            'align': 'right',
            'font_name': 'Liberation Serif',
            'bold': 1,
            'valign': 'vcenter',
        })

        money_format = workbook.add_format({
            'align': 'right',
            'font_name': 'Liberation Serif',
            'bold': 1,
            'valign': 'vcenter',
            'num_format': '#,##0.00'})
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 10)
        #import datetime
        from_date = datetime.strptime((self.from_date), '%Y-%m-%d').strftime('%d-%m-%Y')
        to_date = datetime.strptime((self.to_date), '%Y-%m-%d').strftime('%d-%m-%Y')
        start_dt=datetime.strptime((self.from_date), '%Y-%m-%d')
        end_dt=datetime.strptime((self.to_date), '%Y-%m-%d')
        date_list=[dt.strftime("%Y-%m-01") for dt in rrule(MONTHLY, dtstart=start_dt, until=end_dt)]
        
        date_filter = ' Date from ' + from_date + ' To ' + to_date
        worksheet.merge_range('A3:J3', "Employee Arrear Sheet", merge_format2)
        worksheet.merge_range('A4:J4', date_filter, merge_format2)
        worksheet.write('A6', "S.No", merge_format3)
        worksheet.write('B6', "Employee Name", merge_format3)
        worksheet.write('C6', "Contract", merge_format3)
        worksheet.write('D6', "Basic", merge_format3)
        worksheet.write('E6', "HRA", merge_format3)
        worksheet.write('F6', "Special Allowance", merge_format3)
        worksheet.write('G6', "Conveyance allowance", merge_format3)
        worksheet.write('H6', "Medical Allowance", merge_format3)
        worksheet.write('I6', "Leave Allowance", merge_format3)
        worksheet.write('J6', "Net Arrear", merge_format3)
        #~ for val in range(from_month, int(to_month)+1):
            #~ date.append(str(datetime.strptime(self.from_date, '%Y-%m-%d').year) + '-0' + str(val) + '-' + '01')
            #~ print'FFFFFFFFFFFFFFFFFFFFFFFFFFFFF',val
        n=7
        c=1
        for line in self.employee_line_ids:
            print'*************************************',line
            employee_id=line.employee_id.id
            new_wage=line.contract_id.wage
            #current_sal = self.get_current_salary(line, date[-1])
            arrears=0
            
            from_mn=from_month
            to_mn=to_month
            testing=0
            if line.contract_id.history_line:
                for wage in line.contract_id.history_line:
                    if line.contract_id.wage==wage.old_wage:
                        testing +=1
            else:
                testing=1
            basic=0
            hra=0
            spa=0
            ca=0
            ma=0
            la=0
            net=0
            print'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',testing
            if testing==0:
                for rec_date in date_list:
                    print'RECCCCCCCCCCCCCCCCCCCCCC',rec_date
                    payslip_date=str(from_year)+'-0'+str(from_mn)+'-'+'01'
                    #pa
                    payslip_id=self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('date_from','=',rec_date)])
                    print'PAYYYYYYYYYYYYYYYYYYYYYYYY',payslip_id
                    #~ lop_day=payslip_id.lop_days
                    #~ #new_wage=round((30 - payslip_id.lop_days) * (line.contract_id.wage / 30))
                    arrears_net,component_value = self.compute_arrears_payslip(line,new_wage,payslip_id)
                    #prev_net=current_sal-arrears_net
                    basic+=component_value['basic']
                    hra += component_value['hra']
                    spa += component_value['spa']
                    ca += component_value['ca']
                    ma += component_value['ma']
                    la += component_value['la']
                    net += component_value['net']
                    arrears+=arrears_net
                    #~ from_mn+=1
                line.write({'arrears':arrears})
                worksheet.write('A' + str(n), str(c), merge_format1)
                worksheet.write('B' + str(n), line.employee_id.name, merge_format1)
                worksheet.write('C' + str(n), line.contract_id.name, merge_format1)
                worksheet.write('D' + str(n), round(basic), merge_format4)
                worksheet.write('E' + str(n), round(hra), merge_format4)
                worksheet.write('F' + str(n), round(spa), merge_format4)
                worksheet.write('G' + str(n), round(ca), merge_format4)
                worksheet.write('H' + str(n), round(ma), merge_format4)
                worksheet.write('I' + str(n), round(la), merge_format4)
                worksheet.write('J' + str(n), round(arrears), merge_format4)
                #~ c += 1
                #~ n += 1
        workbook.close()
        fo = open(url+'salary_arrears.xlsx', "rb+")
        data = fo.read()
        out = base64.encodestring(data)
        #~ print'OUTTTTTTTTTTTTTTTTTTTTTTTT',out
        self.write({'filedata': out, 'filename': 'salary_arrears.xlsx'})

    def get_salary(self,line,date):
        self.env.cr.execute('''SELECT l.code,l.total
                                FROM hr_payslip_line l
                                JOIN hr_payslip p ON l.slip_id = p.id
                                WHERE p.employee_id=%s AND p.date_from in %s
                                and l.code not in ('Wages','RCTC','FNGROSS') and l.total >0 '''%(line.employee_id.id,tuple(date)))
        salary=self.env.cr.dictfetchall()
        print salary
        #~ emp={line.employee_id.id:[]}
        #~ for rec in salary:
            #~ emp[line.employee_id.id]=
        return salary

                                    
    #~ @api.multi
    #~ def unlink(self):
        #~ if self.state != 'draft':
            #~ raise UserError(_('You cannot delete a Data'))
        #~ return super(Employee, self).unlink()

class employee_details(models.Model):
    _name='employee.line'
    
    arrear_id = fields.Many2one('salary.arrear',string="Emp Id")
    employee_id = fields.Many2one('hr.employee','Employee')
    contract_id = fields.Many2one('hr.contract','Contract')
    arrears = fields.Float(string="Arrears", digits=(16, 5),readonly=True)

    
    
