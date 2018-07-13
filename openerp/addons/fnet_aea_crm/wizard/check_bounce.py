# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp.osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
import time

class check_bounce_details(osv.osv_memory):
    _name = 'check.bounce.details'
    _description = 'Check Bounce'
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Customer', readonly=True),
        'cheque_id':fields.many2one('post.date.cheque', 'Check/DD No', readonly=True),   
        'bounce_date':fields.date('Bounce Date', required=True),   
        'amount':fields.float('Bank Charge on Bounce', required=True), 
        'description':fields.text('Bounce Reason', required=True), 
        }
        
    def create(self, cr, uid, vals, context=None):
        iss = vals.get('bounce_date')
        today = time.strftime("%Y-%m-%d")
        if iss > today:
            raise osv.except_osv(_('Error!'), _('Please check Cheque Date. You wrongly mapped!'))
        return super(check_bounce_details, self).create(cr, uid, vals, context=context)
  
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(check_bounce_details, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')
        picking = self.pool.get('cheque.details').browse(cr, uid, picking_ids[0], context=context)
        res.update({'partner_id':picking.partner_id.id, 'cheque_id':picking.cheque_id.id})
        return res
        
    def _journal_entries(self, cr, uid, ids, chk, context=None):
        obj = self.browse(cr, uid, ids)
        line_ids = []
        obj = self.browse(cr, uid, ids)
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        period_pool = self.pool.get('account.period')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')
        timenow = time.strftime('%Y-%m-%d')
        default_partner_id = chk.partner_id.id
        date = timenow
        search_periods = period_pool.find(cr, uid, date, context=context)
        period_id = search_periods[0]
        ban_1 = []
        ban_2 = []
        
        if chk.type == 'cheque':
            sr_bank_cr = self.pool.get('account.journal').search(cr, uid, [('allow_check_writing', '=', True),('reciept_journal', '=', True), ('company_id', '=', chk.company_id.id)], context=context)
            sr_bank_dr = self.pool.get('account.journal').search(cr, uid, [('allow_check_writing', '=', True), ('company_id', '=', chk.company_id.id)], context=context)
            bank_cr = self.pool.get('account.journal').browse(cr, uid, sr_bank_cr[0])
            bank_dr = self.pool.get('account.journal').browse(cr, uid, sr_bank_dr[0])
            ban_1.append(bank_cr)
            ban_2.append(bank_dr)
        elif chk.type == 'dd':
            sr_bank = self.pool.get('account.journal').search(cr, uid, [('allow_dd_writing', '=', True), ('company_id', '=', chk.company_id.id)], context=context)
            bank = self.pool.get('account.journal').browse(cr, uid, sr_bank[0])
            ban.append(bank)
        else:
            sr_bank = self.pool.get('account.journal').search(cr, uid, [('allow_neft_writing', '=', True), ('company_id', '=', chk.company_id.id)], context=context)
            bank = self.pool.get('account.journal').browse(cr, uid, sr_bank[0])
            ban.append(bank)
        bank_cr = ban_1[0]
        bank_dr = ban_2[0]
        rec_list = []
        # bank bounce credit
        move = {
                'narration': '/',
                'date': chk.date,
                'ref': chk.voucher_id.reference,
                'journal_id': bank_cr.id,
                'period_id': period_id,
            }
        move_id = move_pool.create(cr, uid, move, context=context)
        debit_li = {
                     'move_id':move_id,
                     'name':'/',
                     'date': timenow,
                     'partner_id':default_partner_id,
                     'account_id':chk.partner_id.property_account_receivable.id,
                     'journal_id':bank_cr.id,
                     'period_id':period_id,
                     'debit':0.0,
                     'credit':chk.amount,
             }
        val = move_line_pool.create(cr, uid, debit_li, context=context)
        rec_list.append(val)
        credit_li = {
                     'move_id':move_id,
                     'name':'Credit',
                     'date': timenow,
                     'partner_id':default_partner_id,
                     'account_id':bank_cr.default_credit_account_id.id,
                     'journal_id':bank_cr.id,
                     'period_id':period_id,
                     'debit':chk.amount,
                     'credit':0.0,
                     }
        move_line_pool.create(cr, uid, credit_li, context=context)
        
        
        # Bank bounce Debit
        move = {
                'narration': '/',
                'date': obj.bounce_date,
                'ref': '/',
                'journal_id': bank_dr.id,
                'period_id': period_id,
            }
        move_id = move_pool.create(cr, uid, move, context=context)
        debit_li = {
                     'move_id':move_id,
                     'name':'Debit',
                     'date': timenow,
                     'partner_id':default_partner_id,
                     'account_id':chk.partner_id.property_account_receivable.id,
                     'journal_id':bank_dr.id,
                     'period_id':period_id,
                     'debit':chk.amount,
                     'credit':0.0,
             }
        val = move_line_pool.create(cr, uid, debit_li, context=context)
        rec_list.append(val)
        credit_li = {
                     'move_id':move_id,
                     'name':'Credit',
                     'date': timenow,
                     'partner_id':default_partner_id,
                     'account_id':bank_dr.default_credit_account_id.id,
                     'journal_id':bank_dr.id,
                     'period_id':period_id,
                     'debit':0.0,
                     'credit':chk.amount,
                     }
        move_line_pool.create(cr, uid, credit_li, context=context)
        period_obj = self.pool.get('account.period')
        date = False
        period_id = False
        journal_id= False
        account_id = False
        date = time.strftime('%Y-%m-%d')
        ids = period_obj.find(cr, uid, dt=date, context=context)
        if ids:
            period_id = ids[0]
        move_line_pool.reconcile(cr, uid,rec_list, 'manual', account_id,period_id, journal_id, context=context)
        return True
        
    def bounce_transfer(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        print context
        picking_ids = context.get('active_ids', [])
        chk = self.pool.get('cheque.details')
        post_chk = self.pool.get('post.date.cheque')
        chk_br =chk.browse(cr, uid, picking_ids[0], context=context)
        vals = {
               'bounce_date':obj.bounce_date,
               'bounce_amount':obj.amount,
               'description':obj.description,
               'state':'bounce',
               }
        chk.write(cr, uid, picking_ids[0], vals, context=context)
        self.pool.get('account.voucher').cancel_voucher(cr, uid, chk_br.voucher_id.id, context=context)
        post_chk.write(cr, uid, obj.cheque_id.id, {'state':'bounce'}, context=context)
        self._journal_entries(cr, uid, ids, chk_br, context=context)
        return True
   
check_bounce_details()

