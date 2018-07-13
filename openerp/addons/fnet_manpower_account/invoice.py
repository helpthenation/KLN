# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval
import openerp.addons.decimal_precision as dp

class invoice_inh(osv.osv):
    _inherit = "account.invoice"
    _columns = {
         
         'res_bank_id':fields.many2one('res.partner.bank', 'Bank'),
       }
     
     
invoice_inh()
class account_move_line(osv.osv):
    _inherit="account.move.line"
    
    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result
    _columns= {
    
        'bill_no':fields.char('Bill No'),
        'ref': fields.related('move_id', 'ref', string='Reference', type='char', 
                            store = {
                                    'account.move': (_get_move_lines, ['ref'], 20)
                                }),
        'paid_to': fields.related('move_id', 'paid_to', string='Paid To', type='char', 
                            store = {
                                    'account.move': (_get_move_lines, ['paid_to'], 20)
                                }),
        'bank_date': fields.related('move_id','bank_date', string='Bank date', type='date', required=True, select=True,
                                store = {
                                    'account.move': (_get_move_lines, ['bank_date'], 20)
                                }),                                
    }
    
class account_move(osv.osv):
    _name = "account.move"
    _inherit=["account.move","mail.thread","ir.needaction_mixin"]

    def _amount_compute(self, cr, uid, ids, name, args, context, where =''):
        if not ids: return {}
        cr.execute( 'SELECT move_id, SUM(debit) '\
                    'FROM account_move_line '\
                    'WHERE move_id IN %s '\
                    'GROUP BY move_id', (tuple(ids),))
        result = dict(cr.fetchall())
        for id in ids:
            result.setdefault(id, 0.0)
        return result

    def _search_amount(self, cr, uid, obj, name, args, context):
        ids = set()
        for cond in args:
            amount = cond[2]
            if isinstance(cond[2],(list,tuple)):
                if cond[1] in ['in','not in']:
                    amount = tuple(cond[2])
                else:
                    continue
            else:
                if cond[1] in ['=like', 'like', 'not like', 'ilike', 'not ilike', 'in', 'not in', 'child_of']:
                    continue

            cr.execute("select move_id from account_move_line group by move_id having sum(debit) %s %%s" % (cond[1]),(amount,))
            res_ids = set(id[0] for id in cr.fetchall())
            ids = ids and (ids & res_ids) or res_ids
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]

    def _get_move_from_lines(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        return [line.move_id.id for line in line_obj.browse(cr, uid, ids, context=context)]    
    
    _columns= {
    
        'paid_to':fields.char('Paid To',track_visibility='onchange',states={'posted':[('readonly',True)]}),
        'bvp_no':fields.char('BPV No'),
        'vendor_code':fields.char('Vendor Code',states={'posted':[('readonly',True)]}),
        'bank_date':fields.date('Bank Date',track_visibility='onchange',states={'posted':[('readonly',True)]}),
        'date': fields.date('Date', required=True, states={'posted':[('readonly',True)]}, select=True,track_visibility='onchange'),
        'state': fields.selection(
              [('draft','Unposted'), ('approve','To Approve'),('posted','Posted')], 'Status',track_visibility='always',
              required=True, readonly=True, copy=False,
              help='All manually created new journal entries are usually in the status \'Unposted\', '
                   'but you can set the option to skip that status on the related journal. '
                   'In that case, they will behave as journal entries automatically created by the '
                   'system on document validation (invoices, bank statements...) and will be created '
                   'in \'Posted\' status.'),   
        'ref': fields.char('Reference',states={'posted':[('readonly',True)]}, copy=False,track_visibility='onchange'),
        'period_id': fields.many2one('account.period', 'Period',track_visibility='onchange', required=True, states={'posted':[('readonly',True)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', track_visibility='onchange',required=True, states={'posted':[('readonly',True)]}),
        'to_check': fields.boolean('To Review', track_visibility='onchange',help='Check this box if you are unsure of that journal entry and if you want to note it as \'to be reviewed\' by an accounting expert.'),
        'partner_id': fields.related('line_id', 'partner_id', type="many2one", relation="res.partner", string="Partner",track_visibility='always', store={
            _name: (lambda self, cr,uid,ids,c: ids, ['line_id'], 10),
            'account.move.line': (_get_move_from_lines, ['partner_id'],10)
            }),
        'amount': fields.function(_amount_compute, string='Amount', digits_compute=dp.get_precision('Account'), track_visibility='always',type='float', fnct_search=_search_amount),                        
    }
    _defaults = {
        'state': 'draft',
        'date': fields.date.context_today,
    }
    
    def button_approve(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'approve'},context=context)
        


class account_voucher(osv.osv):
    _inherit="account.voucher"
    _columns= {
    
        'bvp_no':fields.char('BPV No'),
        'vendor_code':fields.char('Vendor Code'),
        
    }
    
    def button_proforma_voucher(self, cr, uid, ids, context=None):
        if context.get('invoice_type')=='out_invoice':
            account_val=self.pool.get('account.move.line')
            account_id=account_val.search(cr,uid,[('invoice','=',context.get('invoice_id'))],context=context)
            account_rec=account_val.browse(cr,uid,account_id,context=context)
            sale_val=self.pool.get('sale.order')
            for rec in account_rec:
                sale_id=sale_val.search(cr,uid,[('name','=',rec.invoice.origin)])
                sale_rec=sale_val.browse(cr,uid,sale_id,context=context)
                account_val.write(cr, uid, rec.id, {'job_id': sale_rec.id}, context=context)         
            new_id = super(account_voucher, self).button_proforma_voucher(cr, uid,ids, context=context)
