from openerp import api, fields, models,_
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
import calendar
import base64
from openerp.exceptions import except_orm
class enquiry_remainder(models.Model):
    _name='enquiry.remainder'
    
    remainder_receiver_mail = fields.Many2many('res.users','enquriy_remainder_mail_list','rem_id','user_id',string="Receiver Email ID")
    
class crm_lead(models.Model):
    _inherit='crm.lead'

    
    @api.model
    @api.multi
    def remind_send_mail(self):
        self.env.cr.execute('''select user_id from enquriy_remainder_mail_list''')
        user_rec=self.env.cr.dictfetchall()
        for rec in user_rec:
            rec_id=[]
            print'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',rec
            user_obj=self.env['res.users'].browse(rec['user_id'])
            if datetime.now().date().strftime('%A') != 'Thursday':
                enquiry_obj = self.env['crm.lead'].search([('submission_date','=',datetime.now().date()),('company_id','=',user_obj.company_id.id)])           
                if enquiry_obj:
                    rec_id.append(enquiry_obj.ids[0])
            elif datetime.now().date().strftime('%A') == 'Thursday':
                enquiry_obj = self.env['crm.lead'].search([('submission_date','in',(datetime.now().date(),datetime.now().date() + timedelta(days=2),datetime.now().date() + timedelta(days=3))),('company_id','=',user_obj.company_id.id)])               
                if enquiry_obj:
                    rec_id.append(enquiry_obj.ids[0])
            mail_mail = self.env['mail.mail']
            mail_ids=[]
            template_obj = self.env['email.template']
            if rec_id != []:
                for i in rec_id:
                    pdf = self.env['report'].sudo().get_pdf(self.env['crm.lead'].browse(rec_id[0]), 'fnet_mline_remainder.report_enquiry')
                    att= self.env['ir.attachment'].create({
                        'datas_fname': str(datetime.now().date().strftime("%d-%m-%Y"))+' - Enquiry Closing Today',
                        'name': str(datetime.now().date())+' - Enquiry Closing Today',
                        'type': 'binary',
                        'datas': base64.encodestring(pdf),
                        'res_model': 'crm.lead',
                        'res_id': rec_id[0],
                        'mimetype': 'application/x-pdf'
                    })
                    print'AAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaaa',att.id
                    try:
                        email_from = 'admin@multiline.ae'
                        email_to = user_obj.login
                        reply_to = ''
                        subject = str(datetime.now().date().strftime("%d-%m-%Y"))+' - Enquiry Closing Today'
                        body = _("Dear %s, <br/>"%(user_obj.name))
                        body += _("<br/>Attached Enquiries Are closing Today '%s' . Kindly Submit Your Valuable Quote For The Attached Enquiries."%(datetime.now().date().strftime("%d-%m-%Y")))
                        footer="With Regards,<br/>IT Admin<br/>"
                        mail_ids.append(mail_mail.create({
                        'email_from': email_from,
                        'email_to': email_to,
                        'reply_to': reply_to,
                        'record_name':'Enquiry Remainder',
                        'subject': subject,
                        'attachment_ids':[(6,0,[att.id])],
                        'body_html':'''<span  style="font-size:14px"><br/>
                        <br/>%s<br/>
                        <br/>%s</span>''' %(body,footer),
                        }))
                        for j in range(len(mail_ids)):
                            print'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj',j
                            mail_ids[j].send(self)
                    except Exception,z :
                        print "Exception", z
                #~ raise except_orm(_("Employee Payslip Mail Has Been Send Successfully!!!"))
        return None


    @api.model
    @api.multi
    def remind_tomarrow_mail(self):
        self.env.cr.execute('''select user_id from enquriy_remainder_mail_list''')
        user_rec=self.env.cr.dictfetchall()
        for rec in user_rec:
            rec_id=[]
            print'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',rec
            user_obj=self.env['res.users'].browse(rec['user_id'])
            if (datetime.now().date() + timedelta(days=+1)).strftime('%A') != 'Thursday':
                enquiry_obj = self.env['crm.lead'].search([('submission_date','=',datetime.now().date()+timedelta(days=+1)),('company_id','=',user_obj.company_id.id)])           
                if enquiry_obj:
                    rec_id.append(enquiry_obj.ids[0])
            elif (datetime.now().date() + timedelta(days=+1)).strftime('%A') == 'Thursday':
                enquiry_obj = self.env['crm.lead'].search([('submission_date','in',(datetime.now().date()+timedelta(days=+1),datetime.now().date() + timedelta(days=3),datetime.now().date() + timedelta(days=4))),('company_id','=',user_obj.company_id.id)])               
                if enquiry_obj:
                    rec_id.append(enquiry_obj.ids[0])
            mail_mail = self.env['mail.mail']
            mail_ids=[]
            template_obj = self.env['email.template']
            if rec_id != []:
                for i in rec_id:
                    pdf = self.env['report'].sudo().get_pdf(self.env['crm.lead'].browse(rec_id[0]), 'fnet_mline_remainder.report_enquiry_tomarrow')
                    att= self.env['ir.attachment'].create({
                        'datas_fname': str(datetime.now().date())+' - Enquiry Closing Tomarrow',
                        'name': str(datetime.now().date())+' - Enquiry Closing Tomarrow',
                        'type': 'binary',
                        'datas': base64.encodestring(pdf),
                        'res_model': 'crm.lead',
                        'res_id': rec_id[0],
                        'mimetype': 'application/x-pdf'
                    })
                    print'AAAAAAAAAAAAAAAAAAAAAAAAaaaaaaaaaaaaaaaa',att.id
                    try:
                        email_from = 'admin@multiline.ae'
                        email_to = user_obj.login
                        reply_to = ''
                        subject = str((datetime.now().date()+timedelta(days=+1)).strftime("%d-%m-%Y"))+' - Enquiry Closing'
                        body = _("Dear Team, <br/>")
                        body += _("<br/>Kindly Submit Your Valuable Quote For The Attached Enquiries.")
                        footer="With Regards,<br/>IT Admin<br/>"
                        mail_ids.append(mail_mail.create({
                        'email_from': email_from,
                        'email_to': email_to,
                        'reply_to': reply_to,
                        'record_name':'Tomarrow Enquiry Remainder',
                        'subject': subject,
                        'attachment_ids':[(6,0,[att.id])],
                        'body_html':'''<span  style="font-size:14px"><br/>
                        <br/>%s<br/>
                        <br/>%s</span>''' %(body,footer),
                        }))
                        for j in range(len(mail_ids)):
                            print'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj',j
                            mail_ids[j].send(self)
                    except Exception,z :
                        print "Exception", z
                #~ raise except_orm(_("Employee Payslip Mail Has Been Send Successfully!!!"))
        return None
