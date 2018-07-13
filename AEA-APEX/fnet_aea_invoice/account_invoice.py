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


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    has_outstanding_credit=fields.Boolean(string="HAS OUTSTANDING BALANCE")
    amount_unreconcile=fields.Float(compute='_compute_amount_unreconcile',string='amount')
    
        
    @api.multi
    @api.depends('partner_id')
    def _compute_amount_unreconcile(self):
        print'DDDDDDDDDDDDDDDDDDDDDDDDD',self.state
        print'DDDDDDDDDDDDDDDDDDDDDDDDD',self.partner_id
        total=[]
        if self.partner_id and self.state == 'draft':
            print'$$$$$$$$$$$$$$$$$$$$$$',self.partner_id.credit
            
        for line in self:
            partner = self.env['res.partner'].search([('id', '=', line.partner_id.id)])
            self.env.cr.execute("""
                                SELECT l.partner_id as partner_id,l.credit as amount,l.reconcile_partial_id as reconcile_partial_id,l.reconcile_id
                    FROM account_move_line AS l, account_account, account_move am 
                    JOIN account_journal AS aj ON(aj.id=am.journal_id)
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                    AND (account_account.type IN ('receivable','payable'))
                    AND account_account.active
                    AND (l.partner_id = %d)
                    AND l.reconcile_id is NULL 
                    and l.credit > 0
                    ORDER BY l.date::DATE desc """%(line.partner_id.id))
            d=self.env.cr.dictfetchall()
            print'ddddddddddddddddddddddddddddd',d
            if d != []:
                for i in d:
                    if i['reconcile_partial_id'] != None:
                        self.env.cr.execute('''SELECT SUM(l.debit-l.credit) as amount
                                                       FROM account_move_line AS l, account_move AS am
                                                       WHERE l.move_id = am.id  
                                                       AND l.reconcile_partial_id = %s'''%(i['reconcile_partial_id']))
                        dd=self.env.cr.dictfetchall()
                        print'2DDDDD@@@@@@@@@@',dd
                        if dd != []:
                            for i in dd:    
                                total.append(abs(i['amount']))                          
                    else:
                        print'TOTTTTTTTTTTTTTTTTTTTT', total                        
                        total.append(abs(i['amount']))
        print'(((((((((((((((((((((((((((((((((((((((((((',total
        if total != []:
            self.amount_unreconcile=sum(total)
            print'SSSSSSSSSSSSSSSSSSSSSSS',sum(total)
            self.has_outstanding_credit=True
            self.write({'amount_unreconcile':sum(total),'has_outstanding_credit':True})
        else:
            self.has_outstanding_credit=False    
            self.write({'has_outstanding_credit':False})           
   
