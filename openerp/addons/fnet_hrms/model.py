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



        
class Employee(models.Model):
    _name = 'emp.allowance'
    
    #~ @api.model
    #~ def _get_default_monthyear(self):
        #~ res = []
        #~ mymonth = datetime.datetime.now()
        #~ currentMonth = mymonth.strftime("%B")
        #~ res.append(currentMonth)
        #~ currentYear = datetime.datetime.now().year
        #~ res.append(currentYear)
        #~ strmonth = str(res[0]) 
        #~ stryear = str(res[1])
        #~ monthyear = strmonth + '-' + stryear
        #~ return monthyear
    
    month_select = fields.Selection([
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar', 'March'),
        ('apr', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('aug', 'August'),
        ('sep', 'September'),
        ('oct', 'October'),
        ('nov', 'November'),
        ('dec', 'December'),
        
    ], string='Month', index=True)
    emp_company_id = fields.Many2one('res.company',default=lambda self:self.env.user.company_id.id,readonly=True)
    check = fields.Boolean(string='Check the box before updating',help='set the field to True after submit button is clicked')
    emp_company_ids = fields.One2many('emp.details', 'emp_id', string='Employees Details')
    
    
    @api.depends('emp_company_ids')
    def get_fetching(self,emp_company_id):
        b = self.env['emp.details']
        self.env.cr.execute("""select hr.id from hr_employee as hr
                               join resource_resource as rr on hr.resource_id = rr.id
                               join res_company as rc on rr.company_id = rc.id
                               where rc.id = %d and rr.active=true order by hr.id"""%(self.emp_company_id))
        z =self.env.cr.fetchall()
        #~ self.env.cr.execute('''truncate table emp_details''')
        val={}
        v=[]
        for i in range(len(z)):
            val={
                'emp_id' : self.id,
                'employee_name': z[i][0],
                'mbl_ded' : 0.00,
                'ot_all' : 0.00,
                'tds' : 0.00,
                'other_ded' : 0.00,
                'arrears' : 0.00,
                }
            v=b.create(val)
        self.write({'check':True})
   
    def get_update(self):
        self.env.cr.execute("""select hr_employee.id,e.mbl_ded, e.tds,e.arrears,e.ot_all,e.other_ded,COALESCE (e.pt,0.0) from emp_details as e 
                           join hr_employee on e.employee_name = hr_employee.id
                           join emp_allowance on e.emp_id = emp_allowance.id
                           where emp_allowance.id =%s"""%(self.id))
        s = self.env.cr.fetchall()
        for i in s:
            self.env.cr.execute(""" update hr_contract
                                    set mobile_deduction = %s,
                                    overtime_allowance = %s,
                                    tedious_deduction = %s,
                                    other_deduction = %s,
                                    arrears = %s,
                                    pt = %s
                                    where employee_id = %s"""%(i[1],i[4],i[2],i[5],i[3],i[6],i[0]))
            if i[6] > 0.0:
                contract_rec=self.env['hr.contract'].search([('employee_id','=',i[0])]).write({'is_pt':True})
    #~ @api.multi
    #~ def unlink(self):
        #~ if self.check == True:
            #~ raise UserError(_('You cannot delete a Data'))
        #~ return super(Employee, self).unlink()

class employee_details(models.Model):
    _name='emp.details'
    
    emp_id = fields.Many2one('emp.allowance',string="Emp Id")
    employee_name = fields.Many2one('hr.employee',String="Employee Name")
    mbl_ded = fields.Float(string="mobile Deduction", digits=(16, 5))
    ot_all = fields.Float(string="OT Allowance", digits=(16, 5))
    tds = fields.Float(string="TDS", digits=(16, 5))
    other_ded = fields.Float(string="Other Deduction", digits=(16, 5))
    arrears = fields.Float(string="Arrears", digits=(16, 5))
    pt = fields.Float(string="PT", digits=(16, 5))
    
class salary_arrears(models.Model):
    _name = 'salary.arrear'
    _rec_name='company_id'
    state = fields.Selection([
        ('draft', 'Draft'),
        ('arrear_cal', 'Arrear Calculation'),
        ('done', 'Done'),
        
    ], default='draft')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self:self.env.user.company_id.id,readonly=True)
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
    def get_fetching(self,company_id):
        employee_line = self.env['employee.line']
        self.env.cr.execute("""select hr.id from hr_employee as hr
                               join resource_resource as rr on hr.resource_id = rr.id
                               join res_company as rc on rr.company_id = rc.id
                               where rc.id = %d and rr.active=true and hr.id != 1"""%(self.company_id))
        employee =self.env.cr.dictfetchall()
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
            v=employee_line.create(val)
        self.write({'state':'arrear_cal'})

    @api.multi
    def compute_arrears_payslip(self,line,wage,payslip):
        net=0.0
        component_value={}
        basic=round(((wage/30)*(30))*float(line.contract_id.basic_percentage))
        print wage,line.contract_id.basic_percentage,basic,'******************'
        current_basic=basic
        prev_basic = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'BASICS':
                prev_basic = (slip.amount/(30-payslip.lop_days)*30)
        basic = basic - prev_basic
        component_value.update({'basic':basic})
        print basic,'*******************','PREVVVVVVVVV',prev_basic,'BASIC',current_basic
        #ALLOWANCE
        bonus=0.0
        if line.contract_id.is_bonus:
            bonus = round((line.contract_id.bonus / float(30)) * (float(30)))
        else:
            if line.contract_id.struct_id.code in ('SDM Salary structure EPF','BASE','BASE(HRA)','SDM Salary structure'):
                bonus=round(((wage*0.0833)/30)*(30))
            elif line.contract_id.struct_id.code=='Salary Structure for Iswasu':
                bonus=round(((wage*0.0833)/30)*(30))
        current_bonus=bonus
        prev_bonus = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FBONUS':
                prev_bonus = (slip.amount/(30-payslip.lop_days)*30)
        if bonus:
            bonus = bonus - prev_bonus
        else:
            bonus =- prev_bonus
        component_value.update({'bonus':bonus})
        print bonus,'*******************','PREVVVVVVVVV',prev_bonus,'BONUS',current_bonus
        hra=0.0
        if line.contract_id.struct_id.code =='BASE':
            hra=round(wage*0.3)
            print hra,'HRSSSSSSSSSSSSSSSSSSSSS'
        elif line.contract_id.struct_id.code in ('BASE(HRA)'):
            hra=round(wage-current_basic-current_bonus-2004-((0.51247/26*15/12)*wage))
        elif line.contract_id.struct_id.code in ('SDM Salary structure','SDM Salary structure EPF'):
            hra=round(wage*.25)
        elif line.contract_id.struct_id.code=='Salary Structure for Iswasu':
            hra=round(wage*0.3)
        current_hra=hra
        prev_hra = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FHRA':
                prev_hra = (slip.amount/(30-payslip.lop_days)*30)
        if hra:
            hra = hra - prev_hra
        else:
            hra=- prev_hra
        component_value.update({'hra':hra})
        print hra,'*******************','PREVVVVVVVVV',prev_hra,'HRa',current_hra
        ta = 0.0
        if line.contract_id.trans_allowance:
            ta = round((line.contract_id.trans_allowance / float(30)) * (float(30)))
        current_ta=ta
        prev_ta = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'TA':
                prev_ta = (slip.amount/(30-payslip.lop_days)*30)
        if ta:
            ta = ta - prev_ta
        else:
            ta=- prev_ta
        component_value.update({'ta': ta})
        convayance = 0.0
        if line.contract_id.is_convayance:
            convayance = round((line.contract_id.convanyance / float(30)) * (float(30)))
        else:
            if line.contract_id.struct_id.code in ('BASE','Salary Structure for Iswasu','BASE(HRA)'):
                convayance = 0.0
            elif line.contract_id.struct_id.code in ('SDM Salary structure','SDM Salary structure EPF'):
                convayance=round(wage*0.075)
        current_convayance=convayance
        prev_convayance = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FCON':
                prev_convayance = (slip.amount/(30-payslip.lop_days)*30)
        if convayance:
            convayance = convayance - prev_convayance
        else:
            convayance= -prev_convayance
        medical = 0.0
        if line.contract_id.is_medical:
            medical = round((line.contract_id.medical / float(30)) * (float(30)))
        else:
            if line.contract_id.struct_id.code in ('BASE', 'Salary Structure for Iswasu','BASE(HRA)'):
                medical = 0.0
            elif line.contract_id.struct_id.code in ('SDM Salary structure EPF','SDM Salary structure'):
                medical=round(wage*0.075)
        current_medical=medical
        prev_medical = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FMEDICAL':
                prev_medical = (slip.amount/(30-payslip.lop_days)*30)
        if medical:
            medical = medical - prev_medical
        else:
            medical = - prev_medical
        # DEDUCTION
        employee_pf = 0.0
        if line.contract_id.struct_id.code in ('BASE','BASE(HRA)'):
            if (current_basic + current_bonus + ((line.contract_id.trans_allowance / float(30)) * (float(30)))) > 15000:
                employee_pf = -1800
            else:
                employee_pf = round(-(current_basic + current_bonus + ((line.contract_id.trans_allowance / float(30)) * (float(30)))) * 0.12)
        elif line.contract_id.struct_id.code in ('SDM Salary structure EPF', 'SDM Salary structure', 'Salary Structure for Iswasu'):
            if (current_basic) > 15000:
                employee_pf = -1800
            else:
                employee_pf = round(-(current_basic * 0.12))
        current_empf=employee_pf
        prev_empe_pf = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'EEPF':
                prev_empe_pf = (slip.amount/(30-payslip.lop_days)*30)
        if employee_pf:
            employee_pf = employee_pf - prev_empe_pf
        else:
            employee_pf = prev_empe_pf
        component_value.update({'emp_pf': employee_pf})
        print employee_pf,'*******************','PREVVVVVVVVV',prev_empe_pf,'PF',current_empf
        other = 0.0
        if line.contract_id.is_other:
            other = round(line.contract_id.other)
        else:
            if line.contract_id.struct_id.code in ('BASE','BASE(HRA)', 'Salary Structure for Iswasu'):
                other = 0.0
            elif line.contract_id.struct_id.code in ('SDM Salary structure EPF', 'SDM Salary structure'):
                gr = round(wage*.01682)
                other= round(wage - (current_basic + current_hra +current_medical +current_convayance +(- current_empf) +gr+ current_bonus))-1
        current_other=other
        prev_other = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FOTHER':
                prev_other = (slip.amount/(30-payslip.lop_days)*30)
        if other:
            other = other - prev_other
        else:
            other = - prev_other
        eaa=round(line.contract_id.ea_allowance)
        current_eaa=eaa
        prev_eaa = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'EAA':
                prev_eaa = (slip.amount/(30-payslip.lop_days)*30)
        if eaa:
            eaa = eaa - prev_eaa
        else:
            eaa = - prev_eaa
        data_card_allowance=0.0
        data_card_allowance=round(line.contract_id.data_card_allowance)
        currenct_data_allowance=data_card_allowance
        prev_card_alw = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FNDC':
                prev_eaa = (slip.amount/(30-payslip.lop_days)*30)
        if data_card_allowance:
            data_card_allowance = data_card_allowance - prev_card_alw
        else:
            data_card_allowance = - prev_card_alw
        #GROSS
        gross=0.0
        current_gross=0.0
        arr=0.0
        for slip in payslip.line_ids:
            if slip.code == 'FNARR':
                arr=slip.amount
        if line.contract_id.struct_id.code in ('BASE','BASE(HRA)'):
            gross = (basic + (bonus + hra)+ta+arr)
            print (current_basic+current_bonus+current_hra+ta),'&&&&&&&&&&&&&&&&'
            current_gross = (current_basic +current_bonus + current_hra+ta)
            print current_gross
        elif line.contract_id.struct_id.code in ('SDM Salary structure','SDM Salary structure EPF'):
            gross = (basic + (bonus + hra+arr))
            current_gross = (current_basic + (current_bonus + current_hra+ta))
        elif line.contract_id.struct_id.code=='Salary Structure for Iswasu':
            gross = (basic + (bonus + hra + ta + convayance + medical + other+arr))
            current_gross = (current_basic + (current_bonus + current_hra+ta))
        print gross,'*******************','PREVVVVVVVVV',current_gross,'GROSS'
        #DEDUCTION
        pt = 0.0
        if line.contract_id.is_pt == True:
            pt = -line.contract_id.pt
        else:
            if (current_gross) < 3500:
                pt = -0
            elif ((current_gross) > 3501 and (current_gross) < 5000):
                pt = -17
            elif ((current_gross) > 5001 and (current_gross) < 7500):
                pt = -39
            elif ((current_gross) > 7501 and (current_gross) < 10000):
                pt = -85
            elif ((current_gross) > 10001 and (current_gross) < 12500):
                pt = -127
            else:
                pt = -183
        prev_pt = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'FPT':
                prev_pt = (slip.amount/(30-payslip.lop_days)*30)
        if pt:
            pt = pt - prev_pt
        else:
            pt=prev_pt
        esi = 0.0
        if line.contract_id.is_esi==True:
            if line.contract_id.struct_id.code in ('SDM Salary structure', 'SDM Salary structure EPF'):
                esi = round(-((current_basic + current_hra + current_ta  + current_convayance + current_medical + currenct_data_allowance+current_other+current_eaa) + current_bonus) * 0.0175)
            elif line.contract_id.struct_id.code in ('BASE','BASE(HRA)'):
                esi = round(-(current_basic + current_hra + current_ta  + current_convayance + current_medical + current_other + current_bonus) * 0.0175)
            else:
                esi=0.0
        else:
            esi = 0.0
        prev_esi = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'ESI':
                print slip.amount,'****',esi
                prev_esi = (slip.amount/(30-payslip.lop_days)*30)
        if esi:
            esi = esi -prev_esi
        else:
            esi=prev_esi
        component_value.update({'esi': esi})
        print esi,'*******************','PREVVVVVVVVV',prev_esi,'ESI'
        other_ded = round(-line.contract_id.other_deduction)
        prev_other_ded = 0.0
        for slip in payslip.line_ids:
            if slip.code == 'OD':
                prev_other_ded = (slip.amount/(30-payslip.lop_days)*30)
        if other_ded:
            other_ded = other_ded - prev_other_ded
        else:
            other_ded=prev_other_ded
        print payslip.lop_days,'*************************'
        if line.contract_id.struct_id.code  in ('BASE','BASE(HRA)'):
            net = round((gross + (esi + employee_pf ))/30 * (30-payslip.lop_days))
        elif line.contract_id.struct_id.code in ('SDM Salary structure', 'SDM Salary structure EPF'):
            net = round((gross + (esi + employee_pf ))/30 * (30-payslip.lop_days))
        elif line.contract_id.struct_id.code == 'Salary Structure for Iswasu':
            net = round((gross + (employee_pf ))/30 * (30-payslip.lop_days))
        component_value.update({'net': net})
        print net,'*******************'
        return net,component_value
        
    @api.multi
    def compute_arrears(self):
        from_month = datetime.strptime(self.from_date, '%Y-%m-%d').month
        from_year = datetime.strptime(self.from_date, '%Y-%m-%d').year
        to_month = datetime.strptime(self.to_date, '%Y-%m-%d').month
        to_year = datetime.strptime(self.to_date, '%Y-%m-%d').year
        date = []
        #run_time = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        output = StringIO.StringIO()
        # ~ url = os.path.dirname(os.path.realpath('excel_reports'))
        url = '/home/ubuntu/odoo/'
        # ~ url = '/home/muthu/Developement/new/'
        workbook = xlsxwriter.Workbook(url + 'salary_arrears.xlsx')
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

        date_filter = ' Date from ' + from_date + ' To ' + to_date
        worksheet.merge_range('A3:J3', "Employee Arrear Sheet", merge_format2)
        worksheet.merge_range('A4:J4', date_filter, merge_format2)
        worksheet.write('A6', "S.No", merge_format3)
        worksheet.write('B6', "Employee Name", merge_format3)
        worksheet.write('C6', "Contract", merge_format3)
        worksheet.write('D6', "Basic", merge_format3)
        worksheet.write('E6', "Bonus", merge_format3)
        worksheet.write('F6', "Hra", merge_format3)
        worksheet.write('G6', "Travel allowance", merge_format3)
        worksheet.write('H6', "Employee PF", merge_format3)
        worksheet.write('I6', "ESI", merge_format3)
        worksheet.write('J6', "Net Arrear", merge_format3)
        for val in range(from_month, int(to_month)+1):
            date.append(str(datetime.strptime(self.from_date, '%Y-%m-%d').year) + '-0' + str(val) + '-' + '01')
        n=7
        c=1
        for line in self.employee_line_ids:
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
            bonus=0
            hra=0
            ta=0
            epf=0
            esi=0
            net=0
            if testing==0:
                while (from_mn<=to_mn):
                    payslip_date=str(from_year)+'-0'+str(from_mn)+'-'+'01'
                    #pa
                    payslip_id=self.env['hr.payslip'].search([('employee_id','=',line.employee_id.id),('date_from','=',payslip_date)])
                    lop_day=payslip_id.lop_days
                    #new_wage=round((30 - payslip_id.lop_days) * (line.contract_id.wage / 30))
                    arrears_net,component_value = self.compute_arrears_payslip(line,new_wage,payslip_id)
                    #prev_net=current_sal-arrears_net
                    basic+=component_value['basic']
                    bonus += component_value['bonus']
                    epf += component_value['emp_pf']
                    esi += component_value['esi']
                    hra += component_value['hra']
                    ta += component_value['ta']
                    net += component_value['net']
                    arrears+=arrears_net
                    from_mn+=1
                line.write({'arrears':arrears})
                worksheet.write('A' + str(n), str(c), merge_format1)
                worksheet.write('B' + str(n), line.employee_id.name, merge_format1)
                worksheet.write('C' + str(n), line.contract_id.name, merge_format1)
                worksheet.write('D' + str(n), round(basic), merge_format4)
                worksheet.write('E' + str(n), round(bonus), merge_format4)
                worksheet.write('F' + str(n), round(hra), merge_format4)
                worksheet.write('G' + str(n), round(ta), merge_format4)
                worksheet.write('H' + str(n), round(epf), merge_format4)
                worksheet.write('I' + str(n), round(esi), merge_format4)
                worksheet.write('J' + str(n), round(arrears), merge_format4)
                c += 1
                n += 1
        workbook.close()
        fo = open(url + 'salary_arrears.xlsx', "rb+")
        data = fo.read()
        out = base64.encodestring(data)
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

    
    
