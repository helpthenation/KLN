# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
class hr_contract(models.Model):
    _inherit = "hr.contract"
    
    @api.multi
    @api.depends('balance_amount','no_month')
    def _is_loan_complete(self):
        for rec in self:
            if rec.no_month == 0 and rec.balance_amount == 0.0:
                rec.is_loan_completed = False
            else:
                rec.is_loan_completed = True  
    
    @api.multi
    @api.depends('date_start')
    def _get_doj(self):
        for rec in self:
            rec.doj = rec.date_start                
    
    max_percent =  fields.Float(string="Max. Loan Amount Percentage")       
    loan_amount = fields.Float(string="Loan Amount", readonly=True)
    balance_amount = fields.Float(string="Amount To Pay", readonly=True)
    total_paid_amount = fields.Float(string="Amount Paid", readonly=True)
    no_month = fields.Integer(string="Payment Duration", readonly=True)
    is_loan_completed=fields.Boolean('Loan Completed',compute='_is_loan_complete',default=True,store=True)
    as_on_date = fields.Date('Service Days Calculated Upto')
    service_days = fields.Integer('Service Days Earned')
    total_working_days = fields.Integer('Total Working Days')
    doj=fields.Date('Date Of Join',compute='_get_doj',store=True)
    avail_eos=fields.Boolean('Avail End Of Period Benefit')
    prev_service_days=fields.Integer('Prev. Service Days')

    @api.multi
    def compute_eos_days(self):
        for rec in self:
            today = datetime.datetime.now().date()            
            start_date = datetime.datetime.strptime(rec.doj, "%Y-%m-%d")
            as_on_dates = datetime.datetime.strptime(rec.as_on_date, "%Y-%m-%d")
            rec.total_working_days = (datetime.datetime.now() - start_date).days
            work_years =  today.year - start_date.year
            self.env.cr.execute("""select sum(hh.number_of_days_temp) as days 
                                                from hr_holidays hh
                                                join hr_holidays_status hhs on (hhs.id = hh.holiday_status_id)            
                                                where hh.type='remove' and hhs.code = 'UL'
                                                and hh.date_from::date >= '%s' 
                                                and hh.date_to::date <= '%s' 
                                                and hh.employee_id = %d """%(rec.as_on_date,today,rec.employee_id.id))
            absent = self.env.cr.dictfetchone()
            absent_days = absent['days'] or 0.0
            print'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',(datetime.datetime.now() - as_on_dates).days
            if work_years > 5:
                rec.service_days = round(rec.service_days +(((datetime.datetime.now() - as_on_dates).days - absent_days) * 0.0821917))                      
            else:
                rec.service_days = round(rec.service_days + (((datetime.datetime.now() - as_on_dates).days - absent_days) * 0.05753424))                                    
            rec.as_on_date = today
    
    #~ @api.multi
    #~ @api.onchange('avail_eos')
    #~ def _onchange_avail_eos(self):
        #~ rule = self.env['mline.payroll.rule']
        #~ eos_rule = rule.search([('code', '=', 'EOS')])
        #~ if self.avail_eos == True:
            #~ sal_id=self.env['hr.contract.line'].search([('contract_id', '=', self._origin.id),('rule_id','=',eos_rule.id)],limit=1, order='id desc')
            #~ if sal_id:                                                   
                #~ self.env.cr.execute('''delete from hr_contract_line where contract_id = %d and rule_id =%d '''%(self._origin.id,eos_rule.id))
            #~ else:
                #~ self.env.cr.execute("""insert into hr_contract_line
                #~ (contract_id,amount,rule_id,create_uid,create_date)
                #~ VALUES (%d,%d,%d,'%s','%s')"""
                #~ %(self._origin.id,(round(float((self.gross * 0.6)/30.0) * self.service_days)),eos_rule.id,self._uid,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))                                     
        #~ elif self.avail_eos == False:    
            #~ self.env.cr.execute('''delete from hr_contract_line where contract_id = %d and rule_id =%d '''%(self._origin.id,eos_rule.id))           
                    #~ 
