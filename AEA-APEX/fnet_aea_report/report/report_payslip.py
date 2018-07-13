from openerp.osv import osv
from openerp import api
import math


class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_aea_report.hr_payslip_formats'

    def leave_days(self,obj):
        leave=0
        holiday_rec=self.env['hr.holidays']
        holiday_id=holiday_rec.search([('date_to','>=',obj.date_from),('date_to','<=',obj.date_to),('employee_id','=',obj.employee_id.id)])
        for val in holiday_id:
			rec=holiday_rec.browse(val.id)
			for val in rec:
				leave=leave+val.number_of_days_temp     
        return leave
        
    def worked_days(self,obj):
        leave=0
        days=0
        holiday_rec=self.env['hr.holidays']
        holiday_id=holiday_rec.search([('date_to','>=',obj.date_from),('date_to','<=',obj.date_to),('employee_id','=',obj.employee_id.id)])
        for val in holiday_id:
			rec=holiday_rec.browse(val.id)
			for val in rec:
				leave=leave+val.number_of_days_temp     
        print 'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE'
        days=obj.no_of_days-leave
        print days
        return days
        
        
    def total_deduction(self,obj):
        total=0.0
        for rec in obj.line_ids:
            if rec.category_id.code=='DED':
                total=total+rec.total
        return total
        
    def net_salary(self,obj,pay):
        for rec in obj.line_ids:
            if pay=='NET':
                if rec.code=='NET':
                    return rec.total
            if pay=='BASIC':
                if rec.code=='BASIC':
                    return rec.total
            if pay=='hra':
                if rec.code=='hra':
                    return rec.total
            if pay=='SPL':
                if rec.code=='special_allowance':
                    return rec.total
            if pay=='LOP':
                if rec.code=='LOP':
                    return rec.total
            if pay=='convance':
                if rec.code=='convance':
                    return rec.total
            if pay=='GROSS':
                if rec.code=='GROSS':
                    return rec.total  
            if pay=='income_tax':
                if rec.code=='tax_deduction':
                    return rec.total 
            if pay=='advance':
                if rec.code=='ADV':
                    return rec.total 
            if pay=='esi':
                if rec.code=='ESI':
                    return rec.total                                                                        
            if pay=='epf':
                if rec.code=='epf':
                    return rec.total 
            if pay=='PT':
                if rec.code=='professional_tax':
                    return rec.total                                                                                                                
                    
                                                                                                                                                        
                
    @api.multi
    def render_html(self,data=None):
        
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_aea_report.hr_payslip_formats')
        pay_slip=self.env['hr.payslip'].search([('id','=',self.id)])        
        
        docargs = {                    
                'doc_ids':pay_slip,
                'doc_model': report.model,
                'docs': self,
            }
        return report_obj.render('fnet_aea_report.hr_payslip_formats', docargs)
  

            
