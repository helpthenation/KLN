import openerp
from openerp import models,fields,api,_ 
import time
from datetime import datetime, date
#~ from odoo.exceptions import ValidationError,except_orm,UserError
import xlsxwriter
import StringIO
import base64
import csv 

class hr_employee(models.Model):
    _inherit='hr.employee'
    
    date_of_joining=fields.Date('Joining Date ')
    pf_number=fields.Char('PF Number',size=25)
    pf_uan_number=fields.Char('PF UAN Number',size=25)
    grade = fields.Many2one('employee.grade', string='Grade')
    branch_site = fields.Many2one('employee.branch.site', string='Branch/Site')
    esi_number=fields.Char('ESI Number',size=25)
    ins_policy_renewal=fields.Date('Insurance Policy Renewal Date')
    employeeid=fields.Char('Employee ID',size=10,required=True)
    name_of_parent=fields.Char('Parent Name',size=25)
    name_of_spouse=fields.Char('Spouse Name',size=25)
    wedding_date=fields.Date('Wedding Date')
    
    @api.one
    def get_update(self):
        with open('/home/ubuntu/employee_pf.csv') as f:
            reader = csv.DictReader(f)
            for row in reader:
                emp_rec=self.env['hr.employee'].search([('employeeid','=',row['employee_id'])])
                #~ contract_rec=self.env['hr.contract'].search([('employee_id','=',emp_rec.id)])
                #~ contract_rec.write({'salary_arrear':row['arrear'],'is_arrear':True})
                emp_rec.write({'pf_number':row['pf'],'pf_uan_number':row['uan'],'esi_number':row['esi']})
                
    @api.one    
    @api.constrains('wedding_date')
    def wedding_date_check(self):
        if self.wedding_date and self.birthday:
           if self.wedding_date <= self.birthday or self.wedding_date >date.today().isoformat():
              raise ValidationError("Error!\nYou should select correct date only%s"%(self.wedding_date))
        else:
            return True 
    #~ @api.one    
    #~ @api.constrains('ins_policy_renewal') 
    #~ def check_renewal_date(self):
        #~ if self.ins_policy_renewal:    
           #~ if self.ins_policy_renewal < date.today().isoformat():
              #~ raise ValidationError("Error!\nYou should select future date only%s"%(self.ins_policy_renewal))
        #~ else:
           #~ return True  
           
class employee_grade(models.Model):
    _name = 'employee.grade'
    name = fields.Char(string='Name')

class employee_branch_site(models.Model):
    _name = 'employee.branch.site'
    name = fields.Char(string='Name')

class hr_payslip_run(models.Model):
    
    _inherit='hr.payslip.run'
    
    filedata=fields.Binary('Download file',readonly=True)
    filename=fields.Char('Filename', size = 64, readonly=True)
                   
    def confirm_payslip(self):
        for rec in self.slip_ids:
            rec.action_payslip_done()
            self.close_payslip_run()
            
    def salary_excel_eport(self):
        url="/home/ubuntu/odoo/report/"
        workbook = xlsxwriter.Workbook(url+'salary.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':11,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'font_size':11,
                                             'underline': 'underline',})
        merge_format1 = workbook.add_format({
                                              'align': 'center',
                                              'font_size':11,
                                             'valign': 'vcenter',})
        merge_format3 = workbook.add_format({
                                            'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'font_size':11,
                                            'valign': 'vcenter',
                                            'fg_color': 'gray'})
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 20)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 20)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        worksheet.set_column('M:M', 20)
        worksheet.set_column('N:N', 20)
        worksheet.set_column('O:O', 20)
        worksheet.set_column('P:P', 20)
        worksheet.set_column('Q:Q', 20)
        worksheet.set_column('R:R', 20)
        worksheet.set_column('S:S', 20)
        worksheet.set_column('T:T', 20)
        worksheet.set_column('U:U', 20)
        worksheet.set_column('V:V', 20)
        worksheet.set_column('W:W', 20)
        worksheet.set_column('X:X', 20)
        worksheet.set_column('Y:Y', 20)
        worksheet.set_column('Z:Z', 20)
        worksheet.set_column('AA:AA', 20)
        month=datetime.strptime(self.date_start,'%Y-%m-%d').strftime("%B")
        worksheet.merge_range('A1:C1', self.env['res.company']._company_default_get('fnet_hrms').name, merge_format)
        worksheet.merge_range('A2:C2', 'Salary Statement for '+ month, merge_format)
        worksheet.write('A4',"S.No",merge_format3)
        worksheet.write('B4',"Employee ID",merge_format3)
        worksheet.write('C4',"Employee Name",merge_format3)
        worksheet.write('D4',"Pay days",merge_format3)
        worksheet.write('E4',"Present days",merge_format3)
        worksheet.write('F4',"BASIC",merge_format3)
        worksheet.write('G4',"HRA",merge_format3)
        worksheet.write('H4',"BONUS",merge_format3)
        worksheet.write('I4',"TRA ALW",merge_format3)
        worksheet.write('J4',"MED ALW",merge_format3)
        worksheet.write('K4',"CON ALW",merge_format3)
        worksheet.write('L4',"OTHER ALW",merge_format3)
        worksheet.write('M4',"EA ALW",merge_format3)
        worksheet.write('N4',"DATA CARD ALW",merge_format3)
        worksheet.write('O4',"ARRERS",merge_format3)
        worksheet.write('P4',"OT LIST",merge_format3)
        worksheet.write('Q4',"TOTAL EARNINGS",merge_format3)
        worksheet.write('R4',"PF",merge_format3)
        worksheet.write('S4',"Employer PF",merge_format3)
        worksheet.write('T4',"ESI",merge_format3)
        worksheet.write('U4',"Employer ESI",merge_format3)
        worksheet.write('V4',"Gratuity",merge_format3)
        worksheet.write('W4',"PT",merge_format3)
        worksheet.write('X4',"TDS",merge_format3)
        worksheet.write('Y4',"ADVANCE",merge_format3)
        worksheet.write('Z4',"MOD DED",merge_format3)
        worksheet.write('AA4',"OTHER DED",merge_format3)
        worksheet.write('AB4',"TOTAL DED",merge_format3)
        worksheet.write('AC4',"NET AMOUNT",merge_format3)
        worksheet.write('AD4',"PF NO.",merge_format3)
        worksheet.write('AE4',"ESI NO.",merge_format3)
        worksheet.write('AF4',"UAN NO.",merge_format3)
        n=5
        c=1
        for line in self.slip_ids:
            worksheet.write('A'+str(n),str(c) ,merge_format1)
            worksheet.write('B'+str(n), line.employee_id.employeeid,merge_format1)
            worksheet.write('C'+str(n), line.employee_id.name,merge_format1)
            worksheet.write('D'+str(n), 30 ,merge_format1)
            worksheet.write('E'+str(n), line.contract_id.new_employee - line.lop_days if line.contract_id.is_new_emp else 30 - line.lop_days,merge_format1)
            worksheet.write('F'+str(n), self.get_basic(self.id,line.id) if self.get_basic(self.id,line.id) else ' ',merge_format1)
            worksheet.write('G'+str(n), self.get_hra(self.id,line.id) if self.get_hra(self.id,line.id) else ' ',merge_format1)
            worksheet.write('H'+str(n), self.get_bonus(self.id,line.id) if self.get_bonus(self.id,line.id) else ' ',merge_format1)
            worksheet.write('I'+str(n), self.get_tra_alw(self.id,line.id) if self.get_tra_alw(self.id,line.id) else ' ' ,merge_format1)
            worksheet.write('J'+str(n), self.get_med_alw(self.id,line.id) if self.get_med_alw(self.id,line.id) else ' ',merge_format1)
            worksheet.write('K'+str(n), self.get_con_alw(self.id,line.id) if self.get_con_alw(self.id,line.id) else ' ',merge_format1)
            worksheet.write('L'+str(n), self.get_other_alw(self.id,line.id) if self.get_other_alw(self.id,line.id) else ' ',merge_format1)
            worksheet.write('M'+str(n), self.get_ea_alw(self.id,line.id) if self.get_ea_alw(self.id,line.id) else ' ',merge_format1)
            worksheet.write('N'+str(n), self.get_data_alw(self.id,line.id) if self.get_data_alw(self.id,line.id) else ' ',merge_format1)
            worksheet.write('O'+str(n), self.get_arrear(self.id,line.id) if self.get_arrear(self.id,line.id) else ' ',merge_format1)
            worksheet.write('P'+str(n), self.get_ot(self.id,line.id) if self.get_ot(self.id,line.id) else ' ',merge_format1)
            worksheet.write('Q'+str(n), self.get_earnings(self.id,line.id) if self.get_earnings(self.id,line.id) else ' ',merge_format1)
            worksheet.write('R'+str(n), -self.get_pf(self.id,line.id) if type(self.get_pf(self.id,line.id)) == float else '' ,merge_format1)
            worksheet.write('S'+str(n), -self.get_epf(self.id,line.id) if type(self.get_epf(self.id,line.id)) == float else '' ,merge_format1)
            worksheet.write('T'+str(n), -self.get_esi(self.id,line.id) if type(self.get_esi(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('U'+str(n), -self.get_eesi(self.id,line.id) if type(self.get_eesi(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('V'+str(n), -self.get_gty(self.id,line.id) if type(self.get_gty(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('W'+str(n), -self.get_pt(self.id,line.id) if type(self.get_pt(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('X'+str(n), -self.get_tds(self.id,line.id) if type(self.get_tds(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('Y'+str(n), -self.get_advance(self.id,line.id) if type(self.get_advance(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('Z'+str(n), -self.get_mob_ded(self.id,line.id) if type(self.get_mob_ded(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('AA'+str(n), -self.get_od(self.id,line.id) if type(self.get_od(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('AB'+str(n), -self.get_total_ded(self.id,line.id) if type(self.get_total_ded(self.id,line.id)) == float else ' ' ,merge_format1)
            worksheet.write('AC'+str(n), self.get_net(self.id,line.id) ,merge_format1)
            worksheet.write('AD'+str(n), line.employee_id.pf_number if line.employee_id.pf_number else ' ',merge_format1)
            worksheet.write('AE'+str(n), line.employee_id.esi_number if line.employee_id.esi_number else ' ' ,merge_format1)
            worksheet.write('AF'+str(n), line.employee_id.pf_uan_number if line.employee_id.pf_uan_number else ' ',merge_format1)
            n=n+1
            c=c+1 
        worksheet.write('E'+str(n),"Total",merge_format3)
        worksheet.write('F'+str(n),self.get_basic(self.id,[]) if self.get_basic(self.id,[]) else ' ',merge_format1)
        worksheet.write('G'+str(n),self.get_hra(self.id,[]) if self.get_hra(self.id,[]) else ' ',merge_format1)
        worksheet.write('H'+str(n),self.get_bonus(self.id,[]) if self.get_bonus(self.id,[]) else ' ',merge_format1)
        worksheet.write('I'+str(n),self.get_tra_alw(self.id,[]) if self.get_tra_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('J'+str(n),self.get_med_alw(self.id,[]) if self.get_med_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('K'+str(n),self.get_con_alw(self.id,[]) if self.get_con_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('L'+str(n),self.get_other_alw(self.id,[]) if self.get_other_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('M'+str(n),self.get_ea_alw(self.id,[]) if self.get_ea_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('N'+str(n),self.get_data_alw(self.id,[]) if self.get_data_alw(self.id,[]) else ' ',merge_format1)
        worksheet.write('O'+str(n),self.get_arrear(self.id,[]) if self.get_arrear(self.id,[]) else ' ',merge_format1)
        worksheet.write('P'+str(n),self.get_ot(self.id,[]) if self.get_ot(self.id,[]) else ' ',merge_format1)
        worksheet.write('Q'+str(n),self.get_earnings(self.id,[]) if self.get_earnings(self.id,[]) else ' ',merge_format1)
        worksheet.write('R'+str(n),-self.get_pf(self.id,[]) if self.get_pf(self.id,[]) else ' ',merge_format1)
        worksheet.write('S'+str(n),-self.get_epf(self.id,[]) if self.get_epf(self.id,[]) else ' ',merge_format1)
        worksheet.write('T'+str(n),-self.get_esi(self.id,[]) if self.get_esi(self.id,[]) else ' ',merge_format1)
        worksheet.write('U'+str(n),-self.get_eesi(self.id,[]) if self.get_eesi(self.id,[]) else ' ',merge_format1)
        worksheet.write('V'+str(n),-self.get_gty(self.id,[]) if self.get_gty(self.id,[]) else ' ',merge_format1)
        worksheet.write('W'+str(n),-self.get_pt(self.id,[]) if self.get_pt(self.id,[]) else ' ',merge_format1)
        worksheet.write('X'+str(n),-self.get_tds(self.id,[]) if self.get_tds(self.id,[]) else ' ',merge_format1)
        worksheet.write('Y'+str(n),-self.get_advance(self.id,[]) if self.get_advance(self.id,[]) else ' ',merge_format1)
        worksheet.write('Z'+str(n),-self.get_mob_ded(self.id,[]) if self.get_mob_ded(self.id,[]) else ' ',merge_format1)
        worksheet.write('AA'+str(n),-self.get_od(self.id,[]) if self.get_od(self.id,[]) else ' ',merge_format1)
        worksheet.write('AB'+str(n),-self.get_total_ded(self.id,[]) if self.get_total_ded(self.id,[]) else ' ',merge_format1)
        worksheet.write('AC'+str(n),self.get_net(self.id,[]),merge_format1)
        workbook.close()
        fo = open(url+'salary.xlsx', "rb+")
        data=fo.read()
        out=base64.encodestring(data)
        self.write({'filedata':out,'filename':'salary_statement_for_'+ month +'.xls'})

    def get_net(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNNET' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNNET' AND r.id =%d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
                
    def get_other_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FOTHER' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FOTHER' AND r.id =%d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
    def get_ea_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EAA' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EAA' AND r.id =%d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]

            
    def get_total_ded(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id JOIN hr_salary_rule_category hr on (hr.id=l.category_id) 
                                    WHERE hr.code='DED' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall() 
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id  JOIN hr_salary_rule_category hr on (hr.id=l.category_id)
                                    WHERE hr.code='DED' AND r.id =%d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()

            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_pt(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FPT' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FPT' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_od(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='OD' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='OD' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_mob_ded(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='MD' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='MD' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_advance(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='SA' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='SA' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_tds(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='TDS' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='TDS' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_esi(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='ESI' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='ESI' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
                
    def get_eesi(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='ESI2' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='ESI2' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_gty(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='GR' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return -(s1[0][0])
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='GR' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return -(s1[0][0])
                
    def get_pf(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EEPF' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EEPF' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
                
    def get_epf(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EPF' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='EPF' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_earnings(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNGROSS' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNGROSS' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_ot(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNOT' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNOT' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_arrear(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNARR' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNARR' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_data_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNDC' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FNDC' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_con_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FCON' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FCON' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_med_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FMEDICAL' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FMEDICAL' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_tra_alw(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='TA' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='TA' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
            
    def get_bonus(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FBONUS' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FBONUS' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]

    def get_basic(self,run_id,pay_id):
        if pay_id == []:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                               WHERE l.code='BASICS' AND r.id = %d'''%(run_id))
            s1=self.env.cr.fetchall()
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='BASICS' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
    
    def get_hra(self,run_id,pay_id):
        if pay_id==[]:
            self.env.cr.execute('''SELECT sum(total) FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FHRA' AND r.id =%d'''%(run_id))
            s1=self.env.cr.fetchall()            
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]
        else:
            self.env.cr.execute('''SELECT total FROM hr_payslip_line l JOIN hr_payslip p ON l.slip_id = p.id JOIN hr_payslip_run r ON  r.id = p.payslip_run_id
                                   WHERE l.code='FHRA' AND r.id = %d AND p.id =%d'''%(run_id,pay_id))
            s1=self.env.cr.fetchall()
            if s1 == [] or s1[0] == None:
                return ' '
            else:
                return s1[0][0]

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    active=fields.Boolean('Active',default=True)
    is_hra=fields.Boolean('Is HRA',default=False)
    is_pt=fields.Boolean('Is PT',default=False)
    is_bonus=fields.Boolean('Is Bonus',default=False)
    is_medical=fields.Boolean('Is Medical',default=False)
    is_convayance=fields.Boolean('Is convayance',default=False)
    is_travel_added=fields.Boolean('Is TA Not in Basic',default=False)
    is_other=fields.Boolean('Is Other Allownace',default=False)
    is_resigned=fields.Boolean('Is Resigned',default=False)
    is_arrear=fields.Boolean('Is salary Revised',default=False)
    pt=fields.Float('PT', digits=(16, 5))
    medical=fields.Float('Medical', digits=(16, 5))
    convanyance=fields.Float('Conveyance', digits=(16, 5))
    other=fields.Float('Other Allownace',digits=(16, 5))
    hra=fields.Float('HRA', digits=(16, 5))
    bonus=fields.Float('Bonus', digits=(16, 5))
    effective_date=fields.Date('Effective Date',readonly=True)
    history_line=fields.One2many('salary.history.line','contract_id','Salary History')
    salary_arrear=fields.Float('Salary Arrear', digits=(16, 5),readonly=True)

    
class salary_history_line(models.Model):
    _name='salary.history.line'
    
    old_basic=fields.Char('Basic Percentage')
    old_wage=fields.Float('Wages', digits=(16, 5))
    old_stucture_id=fields.Many2one('hr.payroll.structure','Payroll Structure')
    contract_id=fields.Many2one('hr.contract','Contract')
    travel_allowance = fields.Float('Travel Allowance')
    ea_allowance = fields.Float('EA Allowance')
    data_allowance = fields.Float('Data Card Allowance')
    overtime_allowance = fields.Float('Overtime Allowance')
    pt = fields.Float('PT')
    hra = fields.Float('HRA')
    bonus = fields.Float('Bonus')
    medical = fields.Float('Medical')
    conveyance = fields.Float('Conveyance ')
    other = fields.Float('Other Allowance ')
    tds_deduction = fields.Float('TDS')
    mobile_deduction = fields.Float('Mobile Deduction')
    other_deduction = fields.Float('Other Deduction')
    
class salary_revision (models.Model):
    _name='salary.revision'
    
    basic=fields.Char('Basic Percentage')
    wage=fields.Float('Wages', digits=(16, 5))
    effective_date=fields.Date('Effective Date')
    stucture_id=fields.Many2one('hr.payroll.structure','Payroll Structure')
    contract_id=fields.Many2one('hr.contract','Contract')
    travel_allowance=fields.Float('Travel Allowance',digits=(16, 5))
    ea_allowance=fields.Float('EA Allowance',digits=(16, 5))
    data_allowance=fields.Float('Data Card Allowance',digits=(16, 5))
    overtime_allowance=fields.Float('Overtime Allowance',digits=(16, 5))
    pt=fields.Float('PT',digits=(16, 5))
    hra=fields.Float('HRA',digits=(16, 5))
    bonus = fields.Float('Bonus',digits=(16, 5))
    medical = fields.Float('Medical',digits=(16, 5))
    conveyance=fields.Float('Conveyance ',digits=(16, 5))
    other = fields.Float('Other Allowance ',digits=(16, 5))
    tds_deduction=fields.Float('TDS',digits=(16, 5))
    mobile_deduction=fields.Float('Mobile Deduction',digits=(16, 5))
    other_deduction=fields.Float('Other Deduction',digits=(16, 5))
    @api.model
    def default_get(self, fields):
        print"DDDDDDDDDDDDD"
        rec = super(salary_revision, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        print self,fields,rec,active_model,active_ids
        # Checks on context parameters
        #~ if not active_model or not active_ids:
            #~ raise UserError(_("Programmation error: wizard action executed without active_model or active_ids in context."))

        # Checks on received invoice records
        contract = self.env[active_model].browse(active_ids)
        print"KSKSKSKSKSKSKSKSKSKSKSKSKSKSKS",contract
        print'{0:.4f}'.format(contract.basic_percentage)
        rec.update({
            'basic': contract.basic_percentage,
            'wage': contract.wage,
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
                        'old_basic':self.contract_id.basic_percentage,
                        'old_wage':self.contract_id.wage,
                        'contract_id':self.contract_id.id,
                        'old_stucture_id':self.contract_id.struct_id.id,
                        'travel_allowance':self.contract_id.trans_allowance,
                        'ea_allowance':self.contract_id.ea_allowance,
                        'data_allowance':self.contract_id.data_card_allowance,
                        'overtime_allowance':self.contract_id.overtime_allowance,
                        'pt':self.contract_id.pt,
                        'hra':self.contract_id.hra,
                        'bonus':self.contract_id.bonus,
                        'medical':self.contract_id.medical,
                        'convayance':self.contract_id.convanyance,
                        'other':self.contract_id.other,
                        'tds_deduction':self.contract_id.tedious_deduction,
                        'mobile_deduction':self.contract_id.mobile_deduction,
                        'other_deduction':self.contract_id.other_deduction,
                           }))
        print lines
        vals={
              'history_line':lines,
              }
        self.contract_id.write(vals)
        self.contract_id.basic_percentage=self.basic
        self.contract_id.wage=self.wage
        self.contract_id.struct_id=self.stucture_id.id
        self.contract_id.effective_date=self.effective_date
        self.contract_id.trans_allowance = self.travel_allowance
        self.contract_id.ea_allowance = self.ea_allowance
        self.contract_id.data_card_allowance = self.data_allowance
        self.contract_id.overtime_allowance = self.overtime_allowance
        if self.pt:
            self.contract_id.write({'is_pt': True})
        else:
            self.contract_id.write({'is_pt': False})
        self.contract_id.pt = self.pt
        if self.hra:
            self.contract_id.write({'is_hra': True})
        else:
            self.contract_id.write({'is_hra': False})
        self.contract_id.hra = self.hra
        if self.bonus:
            self.contract_id.write({'is_bonus': True})
        else:
            self.contract_id.write({'is_bonus': False})
        self.contract_id.bonus = self.bonus
        if self.medical:
            self.contract_id.write({'is_medical': True})
        else:
            self.contract_id.write({'is_medical': False})
        self.contract_id.medical = self.medical
        if self.conveyance:
            self.contract_id.write({'is_convayance':True})
        else:
            self.contract_id.write({'is_convayance': False})
        self.contract_id.convanyance = self.conveyance
        if self.other:
            self.contract_id.write({'is_other': True})
        else:
            self.contract_id.write({'is_other': False})
        self.contract_id.other= self.other
        self.contract_id.tedious_deduction = self.tds_deduction
        self.contract_id.mobile_deduction = self.mobile_deduction
        self.contract_id.other_deduction = self.other_deduction
