import base64
import datetime
import logging
import psycopg2
import threading

from email.utils import formataddr
from datetime import datetime
from openerp import _, api, fields, models
from openerp import tools
from openerp.addons.base.ir.ir_mail_server import MailDeliveryException
from openerp.tools.safe_eval import safe_eval
#~ from openerp.exceptions import UserError, AccessError

class Res_Partner(models.Model):
    _inherit='res.partner'

    call_meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_counts_call')

    @api.one
    def _compute_meeting_counts_call(self):
        self.env.cr.execute("""select cp.partner_id
                                from crm_phonecall as cp
                                where cp.partner_id = %d """%(self.id))
        part = self.env.cr.fetchall()
        if part !=[]:
            self.call_meeting_count = len(part)
        else:
            print'.'

    def action_view_call(self):
        action = self.env.ref('crm_voip.crm_phonecall_view')
        result = action.read()[0]
        result['domain'] = [('partner_id', 'in', self.ids)]
        return result


#~ class hr_payslip(models.Model):
    #~ _inherit='hr.payslip'

    #~ @api.multi
    #~ def compute_sheet(self):
        #~ self.env.cr.execute("""select date_from,date_to,state,employee_id from hr_payslip where employee_id = %d"""%(self.employee_id))
        #~ s = self.env.cr.fetchall()
        #~ self.env.cr.execute("""select employee_id from hr_payslip where employee_id = %d"""%(self.employee_id))
        #~ emp = self.env.cr.fetchall()
        #~ self.env.cr.execute("SELECT EXTRACT(month FROM date_from) from hr_payslip where date_from = '%s'"""%(self.date_from))
        #~ date = self.env.cr.fetchall()
        #~ self.env.cr.execute("""select date_from from hr_payslip where employee_id = %d and EXTRACT(MONTH FROM date_from) = %s"""%(self.employee_id,date[0][0]))
        #~ date = self.env.cr.fetchall()
        #~ for i in s:
            #~ if i[2] == 'draft':
                #~ if self.date_from == i[0]:
                    #~ if self.date_to == i[1]:
                        #~ if len(emp)>1 and len(date)>1:
                            #~ raise UserError(_('This payslip is already generated for the current Employee !!!.'))
        #~ for payslip in self:
            #~ number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            #~ #delete old payslip lines
            #~ payslip.line_ids.unlink()
            #~ # set the list of contract for which the rules have to be applied
            #~ # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
            #~ contract_ids = payslip.contract_id.ids or \
                #~ self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
            #~ lines = [(0, 0, line) for line in self.get_payslip_lines(contract_ids, payslip.id)]
            #~ payslip.write({'line_ids': lines, 'number': number})
        #~ return True
