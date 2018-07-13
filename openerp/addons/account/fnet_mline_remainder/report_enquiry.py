from openerp import api, fields, models
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
import calendar
class ParticularReport(models.AbstractModel):
    _name = 'report.fnet_mline_remainder.report_enquiry'


    def get_lines(self,obj):
        data_line=[]
        print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',(datetime.now().date() + timedelta(days=+1)).strftime('%A')
        if datetime.now().date().strftime('%A') != 'Thursday':
            enquiry_obj = self.env['crm.lead'].search([('submission_date','=',datetime.now().date()),('company_id','=',obj.company_id.id)])
            for rec in enquiry_obj:
                if rec.stage_id.probability < 40:
					lines={
					'creation_date':rec.date,
					'enquiry':rec.seq_no,
					'name':rec.name,
					'partner':rec.partner_id.name,
					'sale_person':rec.user_id.name,
					'state':rec.stage_id.name,
					}
					data_line.append(lines)
        elif datetime.now().date().strftime('%A') == 'Thursday':
            enquiry_obj = self.env['crm.lead'].search([('submission_date','in',(datetime.now().date(),datetime.now().date() + timedelta(days=2),datetime.now().date() + timedelta(days=3))),('company_id','=',obj.company_id.id)])   
            for rec in enquiry_obj:
                if rec.stage_id.probability < 40:
                    lines={
                    'creation_date':rec.date,
                    'enquiry':rec.seq_no,
                    'name':rec.name,
                    'partner':rec.partner_id.name,
                    'sale_person':rec.user_id.name,
                    'state':rec.stage_id.name,
                    }
                    data_line.append(lines)                    
        return data_line        
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_remainder.report_enquiry')
        crm_obj=self.env['crm.lead'].browse(self.ids)
        #~ sale_order=self.env['sale.order'].search([('name','=',stock_pick.origin)])
        for order in crm_obj.browse(self.ids):
            docargs = {
                'doc_ids': crm_obj,
                #~ 'sale':sale_order,
                'doc_model': report.model,
                'docs': self,
            }

            return report_obj.render('fnet_mline_remainder.report_enquiry', docargs)

