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
from openerp.tools.translate import _
from datetime import datetime, timedelta
import time

class check_dd_map(osv.osv_memory):
    _name = 'check.dd.map'
    _description = 'DD Maping'
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Customer', readonly=True),
        'cheque_id':fields.many2one('post.date.cheque', 'Check/DD No', readonly=True),   
        'dd_date':fields.date('Date', required=True),   
        'amount':fields.float('Amount', required=True, readonly=True),
        'post_dd_line':fields.one2many('post.dd.cheque', 'cheque_id', 'Cheque Line'), 
        }
  
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(check_dd_map, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        picking = self.pool.get('cheque.details').browse(cr, uid, picking_ids[0], context=context)
        res.update({'partner_id':picking.partner_id.id, 'cheque_id':picking.cheque_id.id, 'amount':picking.amount})
        return res
        
    def dd_maping(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        if context is None: context = {}
        picking_ids = context.get('active_ids', [])
        period_pool = self.pool.get('account.period')
        picking = self.pool.get('cheque.details').browse(cr, uid, picking_ids[0], context=context)
        for line in obj.post_dd_line:
            vals = {
                   'cheque_id':obj.partner_id.id,
                   'type':line.type,
                   'name':line.name,
                   'issue_date':line.issue_date,
                   'bank_name':line.bank_name,
                   'branch_name':line.branch_name,
                   'amount':line.amount,
                   'state':'open',
                   }
            chk = self.pool.get('post.date.cheque').create(cr, uid, vals, context=context),
            self.pool.get('cheque.details').write(cr, uid, picking.id, {'against_id':chk, 'close_date':obj.dd_date, 'state':'done', 'dd':True}, context=context)
            search_periods = period_pool.find(cr, uid, line.issue_date, context=context)
            
            if line.type == 'dd':
                sr_dd = self.pool.get('account.journal').search(cr, uid, [('allow_dd_writing', '=', True), ('company_id', '=', picking.company_id.id)], context=context)
                dd = self.pool.get('account.journal').browse(cr, uid, sr_dd[0])
                val = {
                      'partner_id':picking.partner_id.id,
                      'dd_amount':line.amount,
                      'journal_id':dd.id,
                      'ńame':picking.voucher_id.number,
                      'company_id':picking.company_id.id,
                      'period_id':search_periods[0],
                      'type':'receipt',
                      'account_id':dd.default_debit_account_id.id,
                      }
                vou = self.pool.get('account.voucher').create(cr, uid, val, context=context)
            if line.type == 'chaque':
                sr_dd = self.pool.get('account.journal').search(cr, uid, [('allow_check_writing', '=', True), ('company_id', '=', picking.company_id.id)], context=context)
                dd = self.pool.get('account.journal').browse(cr, uid, sr_dd[0])
                val = {
                      'partner_id':picking.partner_id.id,
                      'dd_amount':line.amount,
                      'journal_id':dd.id,
                      'ńame':picking.voucher_id.number,
                      'company_id':picking.company_id.id,
                      'period_id':search_periods[0],
                      'type':'receipt',
                      'account_id':dd.default_debit_account_id.id,
                      }
                self.pool.get('account.voucher').create(cr, uid, val, context=context)
        return True
     
check_dd_map()

class post_dd_cheque(osv.osv_memory):
    _name = 'post.dd.cheque'
    _columns = {
         'cheque_id':fields.many2one('check.dd.map', 'Check'),
         'type': fields.selection([('cheque', 'Cheque'),('dd', 'Demand Draft')],'Type', required=True),
         'name':fields.char('Check/DD No', size=20, required=True),
         'issue_date':fields.date('Issue Date', required=True),
         'bank_name':fields.char('Bank Name', size=50),
         'branch_name':fields.char('Branch Name', size=50),
         'amount':fields.float('Amount'),
          }
          
    _defaults = {
            'state':'open',
            'type':'dd',
            }
            
    def create(self, cr, uid, vals, context=None):
        iss = vals.get('issue_date')
        today = time.strftime("%Y-%m-%d")
        if iss > today:
            raise osv.except_osv(_('Error!'), _('Please check DD Date. You wrongly mapped!'))
        return super(post_dd_cheque, self).create(cr, uid, vals, context=context)
            
post_dd_cheque()
