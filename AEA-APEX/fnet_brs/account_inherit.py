# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from itertools import groupby
import itertools
from operator import itemgetter
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)
class account_moves(osv.osv):
    _name = "account.moves"
    _description = "Account Entry"
    _order = 'id desc'

    def account_assert_balanced(self, cr, uid, context=None):
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        cr.execute("""\
            SELECT      move_id
            FROM        account_moves_lines
            WHERE       state = 'valid'
            GROUP BY    move_id
            HAVING      abs(sum(debit) - sum(credit)) >= %s
            """ % (10 ** (-max(5, prec))))
        assert len(cr.fetchall()) == 0, \
            "For all Journal Items, the state is valid implies that the sum " \
            "of credits equals the sum of debits"
        return True

    def account_move_prepare(self, cr, uid, journal_id, date=False, ref='', company_id=False, context=None):
        '''
        Prepares and returns a dictionary of values, ready to be passed to create() based on the parameters received.
        '''
        if not date:
            date = fields.date.today()
        period_obj = self.pool.get('account.period')
        if not company_id:
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            company_id = user.company_id.id
        if context is None:
            context = {}
        #put the company in context to find the good period
        ctx = context.copy()
        ctx.update({'company_id': company_id})
        return {
            'journal_id': journal_id,
            'date': date,
            'period_id': period_obj.find(cr, uid, date, context=ctx)[0],
            'ref': ref,
            'company_id': company_id,
        }

    def name_get(self, cursor, user, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not ids:
            return []
        res = []
        data_move = self.pool.get('account.moves').browse(cursor, user, ids, context=context)
        for move in data_move:
            if move.state=='draft':
                name = '*' + str(move.id)
            else:
                name = move.name
            res.append((move.id, name))
        return res

    def _get_period(self, cr, uid, context=None):
        ctx = dict(context or {})
        period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
        return period_ids[0]

    def _amount_compute(self, cr, uid, ids, name, args, context, where =''):
        if not ids: return {}
        cr.execute( 'SELECT move_id, SUM(debit) '\
                    'FROM account_moves_lines '\
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

            cr.execute("select move_id from account_moves_lines group by move_id having sum(debit) %s %%s" % (cond[1]),(amount,))
            res_ids = set(id[0] for id in cr.fetchall())
            ids = ids and (ids & res_ids) or res_ids
        if ids:
            return [('id', 'in', tuple(ids))]
        return [('id', '=', '0')]

    def _get_move_from_lines(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.moves.lines')
        return [line.move_id.id for line in line_obj.browse(cr, uid, ids, context=context)]

    _columns = {
        'name': fields.char('Number', required=True, copy=False),
        'ref': fields.char('Reference', copy=False),
        'period_id': fields.many2one('account.period', 'Period', required=True, states={'posted':[('readonly',True)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, states={'posted':[('readonly',True)]}),
        'state': fields.selection(
              [('draft','Unposted'), ('posted','Posted')], 'Status',
              required=True, readonly=True, copy=False,
              help='All manually created new journal entries are usually in the status \'Unposted\', '
                   'but you can set the option to skip that status on the related journal. '
                   'In that case, they will behave as journal entries automatically created by the '
                   'system on document validation (invoices, bank statements...) and will be created '
                   'in \'Posted\' status.'),
        'line_id': fields.one2many('account.moves.lines', 'move_id', 'Entries',
                                   states={'posted':[('readonly',True)]},
                                   copy=True),
        'to_check': fields.boolean('To Review', help='Check this box if you are unsure of that journal entry and if you want to note it as \'to be reviewed\' by an accounting expert.'),
        'partner_id': fields.related('line_id', 'partner_id', type="many2one", relation="res.partner", string="Partner", store={
            _name: (lambda self, cr,uid,ids,c: ids, ['line_id'], 10),
            'account.moves.lines': (_get_move_from_lines, ['partner_id'],10)
            }),
        'amount': fields.function(_amount_compute, string='Amount', digits_compute=dp.get_precision('Account'), type='float', fnct_search=_search_amount),
        'date': fields.date('Date', required=True, states={'posted':[('readonly',True)]}, select=True),
        'narration':fields.text('Internal Note'),
        'company_id': fields.related('journal_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
        'balance': fields.float('balance', digits_compute=dp.get_precision('Account'), help="This is a field only used for internal purpose and shouldn't be displayed"),
    }

    _defaults = {
        'name': '/',
        'state': 'draft',
        'period_id': _get_period,
        'date': fields.date.context_today,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }

    def _check_centralisation(self, cursor, user, ids, context=None):
        for move in self.browse(cursor, user, ids, context=context):
            if move.journal_id.centralisation:
                move_ids = self.search(cursor, user, [
                    ('period_id', '=', move.period_id.id),
                    ('journal_id', '=', move.journal_id.id),
                    ])
                if len(move_ids) > 1:
                    return False
        return True

    _constraints = [
        (_check_centralisation,
            'You cannot create more than one move per period on a centralized journal.',
            ['journal_id']),
    ]

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)
        obj=self.browse(cr,uid,ids)
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        if obj.name =='/':
            new_name = False
            journal = obj.journal_id

            if invoice and invoice.internal_number:
                new_name = invoice.internal_number
            else:
                new_name = obj_sequence.get(cr, uid,'consolidate.seq.code')
            if new_name:
                self.write(cr, uid, [obj.id], {'name':new_name})   
        cr.execute("""select name,credit,date,company_id,account_id from account_moves_lines where move_id = %d and credit > 0"""%(obj.id))           
        moves_credit_lines=cr.dictfetchall()
        if moves_credit_lines != []:
            sorted_lines=sorted(moves_credit_lines,key=itemgetter('company_id'))
            grouped_lines={}
            for key,value in itertools.groupby(sorted_lines,key=itemgetter('company_id')):
                for i in value:
                    grouped_lines.setdefault(key, []).append(i)        
            for key,value in grouped_lines.iteritems():        
                acc_id=[]
                journal_id=journal_obj.search(cr,uid,[('type','=','bank'),('company_id','=',key),('code','like','%BP%')],limit=1)    
                account_id=account_obj.search(cr,uid,[('code','=','1214213'),('company_id','=',key)],limit=1)    
                account_ids=account_obj.search(cr,uid,[('code','=','1214212'),('company_id','=',key)],limit=1)    
                comp_obj=self.pool.get('res.company').browse(cr,uid,key)
                na = comp_obj.name
                if na[0:3] == 'AEA':
                    acc_id=account_ids
                else:
                    acc_id=account_id
                cr.execute("""SELECT id as id FROM account_period
                WHERE '%s' between date_start::date and date_stop::date and company_id=%d limit 1"""%(obj.date,key))
                period_id=cr.dictfetchone()
                move_vals = {
                'name': '/',
                'date': obj.date,
                'ref': obj.ref,
                'period_id': period_id['id'] or False,
                'journal_id': journal_id[0],
                'state': 'draft',
                'company_id':key,
                'is_consolidated':True,
                'consolidate_cheque_no':obj.name
                }
                move_id = move_obj.create(cr, uid, move_vals, context)
                credit_amt=0.0
                if len(value) > 1:
                    for val in value:
                        credit_amt += val['credit']
                        move_line_vals = {
                            'name': val['name'],
                            'ref': obj.ref,
                            'move_id': move_id,
                            'account_id': val['account_id'],
                            'debit':val['credit'],
                            'credit':0.0,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':val['company_id'],
                        }
                        move_line_obj.create(cr, uid, move_line_vals, context)    
                    move_line_vals2 = {
                            'name': 'BANK CREDIT',
                            'ref': obj.ref,
                            'move_id': move_id,
                            'account_id': acc_id[0],
                            'debit':0.0,
                            'credit':credit_amt,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':val['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals2, context)     
                else:
                    move_line_vals = {
                            'name': value[0]['name'],
                            'ref': 'Money Plus Card Amount Recd.',
                            'move_id': move_id,
                            'account_id': value[0]['account_id'],
                            'debit':value[0]['credit'],
                            'credit':0.0,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':value[0]['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals, context)    
                    move_line_vals2 = {
                            'name': 'BANK CREDIT',
                            'ref': 'Money Plus Card Amount Recd.',
                            'move_id': move_id,
                            'account_id': acc_id[0],
                            'debit':0.0,
                            'credit':value[0]['credit'],
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':value[0]['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals2, context)                     
        #~ DEBIT LINESSSSSSSSSSSSSSSSSSSSSS
        cr.execute("""select name,debit,date,company_id,account_id from account_moves_lines where move_id = %d and debit > 0"""%(obj.id))           
        moves_debit_lines=cr.dictfetchall()
        if moves_debit_lines != []:
            sorted_lines=sorted(moves_debit_lines,key=itemgetter('company_id'))
            grouped_lines={}
            for key,value in itertools.groupby(sorted_lines,key=itemgetter('company_id')):
                for i in value:
                    grouped_lines.setdefault(key, []).append(i)        
            for key,value in grouped_lines.iteritems():        
                acc_id=[]
                journal_id=journal_obj.search(cr,uid,[('type','=','bank'),('company_id','=',key),('code','like','%BP%')],limit=1)    
                account_id=account_obj.search(cr,uid,[('code','=','1214213'),('company_id','=',key)],limit=1)    
                account_ids=account_obj.search(cr,uid,[('code','=','1214212'),('company_id','=',key)],limit=1)    
                comp_obj=self.pool.get('res.company').browse(cr,uid,key)
                na = comp_obj.name
                if na[0:3] == 'AEA':
                    acc_id=account_ids
                else:
                    acc_id=account_id
                cr.execute("""SELECT id as id FROM account_period
                WHERE '%s' between date_start::date and date_stop::date and company_id=%d limit 1"""%(obj.date,key))
                period_id=cr.dictfetchone()
                move_vals = {
                'name': '/',
                'date': obj.date,
                'ref': obj.ref,
                'period_id': period_id['id'] or False,
                'journal_id': journal_id[0],
                'state': 'draft',
                'company_id':key,
                'is_consolidated':True,
                'consolidate_cheque_no':obj.name
                }
                move_id = move_obj.create(cr, uid, move_vals, context)
                debit_amt=0.0
                if len(value) > 1:
                    for val in value:
                        debit_amt += val['debit']
                        move_line_vals = {
                            'name': val['name'],
                            'ref': obj.ref,
                            'move_id': move_id,
                            'account_id': val['account_id'],
                            'debit':0.0,
                            'credit':debit_amt,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':val['company_id'],
                        }
                        move_line_obj.create(cr, uid, move_line_vals, context)    
                    move_line_vals2 = {
                            'name': 'BANK Debit',
                            'ref': obj.ref,
                            'move_id': move_id,
                            'account_id': acc_id[0],
                            'debit':debit_amt,
                            'credit':0.0,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':val['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals2, context)     
                else:
                    move_line_vals = {
                            'name': value[0]['name'],
                            'ref': obj.ref,
                            'move_id': move_id,
                            'account_id': value[0]['account_id'],
                            'debit':0.0,
                            'credit':value[0]['debit'],
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':value[0]['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals, context)    
                    move_line_vals2 = {
                            'name': 'BANK DEBIT',
                            'ref': 'Money Plus Card Amount Recd.',
                            'move_id': move_id,
                            'account_id': acc_id[0],
                            'debit':value[0]['debit'],
                            'credit':0.0,
                            'period_id': period_id['id'] or False,
                            'journal_id': journal_id[0],
                            'amount_currency':  0.0,
                            'date': obj.date,
                            'analytic_account_id': False,
                            'company_id':value[0]['company_id'],
                        }
                    move_line_obj.create(cr, uid, move_line_vals2, context)                                                                     
        cr.execute('UPDATE account_moves '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        self.invalidate_cache(cr, uid, ['state', ], valid_moves, context=context)
        return True

    def button_validate(self, cursor, user, ids, context=None):
        #~ for move in self.browse(cursor, user, ids, context=context):
            #~ # check that all accounts have the same topmost ancestor
            #~ top_common = None
            #~ for line in move.line_id:
                #~ account = line.account_id
                #~ top_account = account
                #~ while top_account.parent_id:
                    #~ top_account = top_account.parent_id
                #~ if not top_common:
                    #~ top_common = top_account
                #~ elif top_account.id != top_common.id:
                    #~ raise osv.except_osv(_('Error!'),
                                         #~ _('You cannot validate this journal entry because account "%s" does not belong to chart of accounts "%s".') % (account.name, top_common.name))
        return self.post(cursor, user, ids, context=context)

    def button_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if not line.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if ids:
            cr.execute('UPDATE account_moves '\
                       'SET state=%s '\
                       'WHERE id IN %s', ('draft', tuple(ids),))
            self.invalidate_cache(cr, uid, context=context)
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        c = context.copy()
        c['novalidate'] = True
        result = super(account_moves, self).write(cr, uid, ids, vals, c)
        self.validate(cr, uid, ids, context=context)
        return result

    def create(self, cr, uid, vals, context=None):
        context = dict(context or {})
        if vals.get('line_id'):
            if vals.get('journal_id'):
                for l in vals['line_id']:
                    if not l[0]:
                        l[2]['journal_id'] = vals['journal_id']
                context['journal_id'] = vals['journal_id']
            if 'period_id' in vals:
                for l in vals['line_id']:
                    if not l[0]:
                        l[2]['period_id'] = vals['period_id']
                context['period_id'] = vals['period_id']
            else:
                default_period = self._get_period(cr, uid, context)
                for l in vals['line_id']:
                    if not l[0]:
                        l[2]['period_id'] = default_period
                context['period_id'] = default_period

            c = context.copy()
            c['novalidate'] = True
            c['period_id'] = vals['period_id'] if 'period_id' in vals else self._get_period(cr, uid, context)
            c['journal_id'] = vals['journal_id']
            if 'date' in vals: c['date'] = vals['date']
            result = super(account_moves, self).create(cr, uid, vals, c)
            tmp = self.validate(cr, uid, [result], context)
            journal = self.pool.get('account.journal').browse(cr, uid, vals['journal_id'], context)
            if journal.entry_posted and tmp:
                self.button_validate(cr,uid, [result], context)
        else:
            result = super(account_moves, self).create(cr, uid, vals, context)
        return result

    def unlink(self, cr, uid, ids, context=None):
        context = dict(context or {})
        if isinstance(ids, (int, long)):
            ids = [ids]
        toremove = []
        obj_move_line = self.pool.get('account.moves.lines')
        for move in self.browse(cr, uid, ids, context=context):
            if move['state'] != 'draft':
                raise osv.except_osv(_('User Error!'),
                        _('You cannot delete a posted journal entry "%s".') % \
                                move['name'])
            for line in move.line_id:
                if line.invoice:
                    raise osv.except_osv(_('User Error!'),
                            _("Move cannot be deleted if linked to an invoice. (Invoice: %s - Move ID:%s)") % \
                                    (line.invoice.number,move.name))
            line_ids = map(lambda x: x.id, move.line_id)
            context['journal_id'] = move.journal_id.id
            context['period_id'] = move.period_id.id
            obj_move_line._update_check(cr, uid, line_ids, context)
            obj_move_line.unlink(cr, uid, line_ids, context=context)
            toremove.append(move.id)
        result = super(account_moves, self).unlink(cr, uid, toremove, context)
        return result

    def _compute_balance(self, cr, uid, id, context=None):
        move = self.browse(cr, uid, id, context=context)
        amount = 0
        for line in move.line_id:
            amount+= (line.debit - line.credit)
        return amount

    def _centralise(self, cr, uid, move, mode, context=None):
        assert mode in ('debit', 'credit'), 'Invalid Mode' #to prevent sql injection
        currency_obj = self.pool.get('res.currency')
        account_moves_lines_obj = self.pool.get('account.moves.lines')
        context = dict(context or {})

        if mode=='credit':
            account_id = move.journal_id.default_debit_account_id.id
            mode2 = 'debit'
            if not account_id:
                raise osv.except_osv(_('User Error!'),
                        _('There is no default debit account defined \n' \
                                'on journal "%s".') % move.journal_id.name)
        else:
            account_id = move.journal_id.default_credit_account_id.id
            mode2 = 'credit'
            if not account_id:
                raise osv.except_osv(_('User Error!'),
                        _('There is no default credit account defined \n' \
                                'on journal "%s".') % move.journal_id.name)

        # find the first line of this move with the current mode
        # or create it if it doesn't exist
        cr.execute('select id from account_moves_lines where move_id=%s and centralisation=%s limit 1', (move.id, mode))
        res = cr.fetchone()
        if res:
            line_id = res[0]
        else:
            context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
            line_id = account_moves_lines_obj.create(cr, uid, {
                'name': _(mode.capitalize()+' Centralisation'),
                'centralisation': mode,
                'partner_id': False,
                'account_id': account_id,
                'move_id': move.id,
                'journal_id': move.journal_id.id,
                'period_id': move.period_id.id,
                'date': move.period_id.date_stop,
                'debit': 0.0,
                'credit': 0.0,
            }, context)

        # find the first line of this move with the other mode
        # so that we can exclude it from our calculation
        cr.execute('select id from account_moves_lines where move_id=%s and centralisation=%s limit 1', (move.id, mode2))
        res = cr.fetchone()
        if res:
            line_id2 = res[0]
        else:
            line_id2 = 0

        cr.execute('SELECT SUM(%s) FROM account_moves_lines WHERE move_id=%%s AND id!=%%s' % (mode,), (move.id, line_id2))
        result = cr.fetchone()[0] or 0.0
        cr.execute('update account_moves_lines set '+mode2+'=%s where id=%s', (result, line_id))
        account_moves_lines_obj.invalidate_cache(cr, uid, [mode2], [line_id], context=context)

        #adjust also the amount in currency if needed
        cr.execute("select currency_id, sum(amount_currency) as amount_currency from account_moves_lines where move_id = %s and currency_id is not null group by currency_id", (move.id,))
        for row in cr.dictfetchall():
            currency_id = currency_obj.browse(cr, uid, row['currency_id'], context=context)
            if not currency_obj.is_zero(cr, uid, currency_id, row['amount_currency']):
                amount_currency = row['amount_currency'] * -1
                account_id = amount_currency > 0 and move.journal_id.default_debit_account_id.id or move.journal_id.default_credit_account_id.id
                cr.execute('select id from account_moves_lines where move_id=%s and centralisation=\'currency\' and currency_id = %slimit 1', (move.id, row['currency_id']))
                res = cr.fetchone()
                if res:
                    cr.execute('update account_moves_lines set amount_currency=%s , account_id=%s where id=%s', (amount_currency, account_id, res[0]))
                    account_moves_lines_obj.invalidate_cache(cr, uid, ['amount_currency', 'account_id'], [res[0]], context=context)
                else:
                    context.update({'journal_id': move.journal_id.id, 'period_id': move.period_id.id})
                    line_id = account_moves_lines_obj.create(cr, uid, {
                        'name': _('Currency Adjustment'),
                        'centralisation': 'currency',
                        'partner_id': False,
                        'account_id': account_id,
                        'move_id': move.id,
                        'journal_id': move.journal_id.id,
                        'period_id': move.period_id.id,
                        'date': move.period_id.date_stop,
                        'debit': 0.0,
                        'credit': 0.0,
                        'currency_id': row['currency_id'],
                        'amount_currency': amount_currency,
                    }, context)

        return True

    #
    # Validate a balanced move. If it is a centralised journal, create a move.
    #
    def validate(self, cr, uid, ids, context=None):
        if context and ('__last_update' in context):
            del context['__last_update']

        valid_moves = [] #Maintains a list of moves which can be responsible to create analytic entries
        obj_analytic_line = self.pool.get('account.analytic.line')
        obj_move_line = self.pool.get('account.moves.lines')
        obj_precision = self.pool.get('decimal.precision')
        prec = obj_precision.precision_get(cr, uid, 'Account')
        for move in self.browse(cr, uid, ids, context):
            journal = move.journal_id
            amount = 0
            line_ids = []
            line_draft_ids = []
            company_id = None
            # makes sure we don't use outdated period
            #~ obj_move_line._update_journal_check(cr, uid, journal.id, move.period_id.id, context=context)
            for line in move.line_id:
                amount += line.debit - line.credit
                line_ids.append(line.id)
                if line.state=='draft':
                    line_draft_ids.append(line.id)

                if not company_id:
                    company_id = line.account_id.company_id.id
                #~ if not company_id == line.account_id.company_id.id:
                    #~ raise osv.except_osv(_('Error!'), _("Cannot create moves for different companies."))

                if line.account_id.currency_id and line.currency_id:
                    if line.account_id.currency_id.id != line.currency_id.id and (line.account_id.currency_id.id != line.account_id.company_id.currency_id.id):
                        raise osv.except_osv(_('Error!'), _("""Cannot create move with currency different from ..""") % (line.account_id.code, line.account_id.name))

            if round(abs(amount), prec) < 10 ** (-max(5, prec)):
                # If the move is balanced
                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move)

                # Check whether the move lines are confirmed

                if not line_draft_ids:
                    continue
                # Update the move lines (set them as valid)

                obj_move_line.write(cr, uid, line_draft_ids, {
                    'state': 'valid'
                }, context=context)

                account = {}
                account2 = {}

                if journal.type in ('purchase','sale'):
                    for line in move.line_id:
                        code = amount = 0
                        key = (line.account_id.id, line.tax_code_id.id)
                        if key in account2:
                            code = account2[key][0]
                            amount = account2[key][1] * (line.debit + line.credit)
                        elif line.account_id.id in account:
                            code = account[line.account_id.id][0]
                            amount = account[line.account_id.id][1] * (line.debit + line.credit)
                        if (code or amount) and not (line.tax_code_id or line.tax_amount):
                            obj_move_line.write(cr, uid, [line.id], {
                                'tax_code_id': code,
                                'tax_amount': amount
                            }, context=context)
            elif journal.centralisation:
                # If the move is not balanced, it must be centralised...

                # Add to the list of valid moves
                # (analytic lines will be created later for valid moves)
                valid_moves.append(move)

                #
                # Update the move lines (set them as valid)
                #
                self._centralise(cr, uid, move, 'debit', context=context)
                self._centralise(cr, uid, move, 'credit', context=context)
                obj_move_line.write(cr, uid, line_draft_ids, {
                    'state': 'valid'
                }, context=context)
            else:
                # We can't validate it (it's unbalanced)
                # Setting the lines as draft
                not_draft_line_ids = list(set(line_ids) - set(line_draft_ids))
                if not_draft_line_ids:
                    obj_move_line.write(cr, uid, not_draft_line_ids, {
                        'state': 'draft'
                    }, context=context)
        # Create analytic lines for the valid moves
        for record in valid_moves:
            obj_move_line.create_analytic_lines(cr, uid, [line.id for line in record.line_id], context)

        valid_moves = [move.id for move in valid_moves]
        return len(valid_moves) > 0 and valid_moves or False
        
class account_moves_lines(osv.osv):
    _name = "account.moves.lines"
    _description = "Journal Items"     


    def on_create_write(self, cr, uid, id, context=None):
        if not id:
            return []
        ml = self.browse(cr, uid, id, context=context)
        domain = (context or {}).get('on_write_domain', [])
        return self.pool.get('account.moves.lines').search(cr, uid, domain + [['id', 'in', [l.id for l in ml.move_id.line_id]]], context=context)

    def _balance(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        c = context.copy()
        c['initital_bal'] = True
        sql = """SELECT l1.id, COALESCE(SUM(l2.debit-l2.credit), 0)
                    FROM account_moves_lines l1 LEFT JOIN account_moves_lines l2
                    ON (l1.account_id = l2.account_id
                      AND l2.id <= l1.id
                      AND """ + \
                self._query_get(cr, uid, obj='l2', context=c) + \
                ") WHERE l1.id IN %s GROUP BY l1.id"

        cr.execute(sql, [tuple(ids)])
        return dict(cr.fetchall())

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.ref:
                result.append((line.id, (line.move_id.name or '')+' ('+line.ref+')'))
            else:
                result.append((line.id, line.move_id.name))
        return result

    def _balance_search(self, cursor, user, obj, name, args, domain=None, context=None):
        if context is None:
            context = {}
        if not args:
            return []

        where = ' AND '.join(
            '(abs(sum(debit-credit)) %s %%s)' % operator
            for field, operator, value in args
        )
        params = tuple(value for field, operator, value in args)

        cursor.execute('SELECT id, SUM(debit-credit) FROM account_moves_lines \
                     GROUP BY id, debit, credit having '+where, params)
        res = cursor.fetchall()
        if not res:
            return [('id', '=', '0')]
        return [('id', 'in', [x[0] for x in res])]
               
    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.moves').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result
    def create_analytic_lines(self, cr, uid, ids, context=None):
        acc_ana_line_obj = self.pool.get('account.analytic.line')
        for obj_line in self.browse(cr, uid, ids, context=context):
            if obj_line.analytic_lines:
                acc_ana_line_obj.unlink(cr,uid,[obj.id for obj in obj_line.analytic_lines])
            if obj_line.analytic_account_id:
                if not obj_line.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (obj_line.journal_id.name, ))
                vals_line = self._prepare_analytic_line(cr, uid, obj_line, context=context)
                acc_ana_line_obj.create(cr, uid, vals_line)
        return True
    _columns = {
        'name': fields.char('Name', required=True),
        'quantity': fields.float('Quantity', digits=(16,2), help="The optional quantity expressed by this line, eg: number of product sold. The quantity is not a legal requirement but is very useful for some reports."),
        'product_uom_id': fields.many2one('product.uom', 'Unit of Measure'),
        'product_id': fields.many2one('product.product', 'Product'),
        'debit': fields.float('Debit', digits_compute=dp.get_precision('Account')),
        'credit': fields.float('Credit', digits_compute=dp.get_precision('Account')),
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete="cascade", domain=[('type','<>','view'), ('type', '<>', 'closed')], select=2),
        'move_id': fields.many2one('account.moves', 'Journal Entry', ondelete="cascade", help="The move of this entry line.", select=2, required=True, auto_join=True),
        'narration': fields.related('move_id','narration', type='text', relation='account.moves', string='Internal Note'),
        'ref': fields.related('move_id', 'ref', string='Reference', type='char', store=True),
        'statement_id': fields.many2one('account.bank.statement', 'Statement', help="The bank statement used for bank reconciliation", select=1, copy=False),
        #~ 'reconcile_id': fields.many2one('account.move.reconcile', 'Reconcile', readonly=True, ondelete='set null', select=2, copy=False),
        #~ 'reconcile_partial_id': fields.many2one('account.move.reconcile', 'Partial Reconcile', readonly=True, ondelete='set null', select=2, copy=False),
        #~ 'reconcile_ref': fields.function(_get_reconcile, type='char', string='Reconcile Ref', oldname='reconcile', store={
                    #~ 'account.move.line': (lambda self, cr, uid, ids, c={}: ids, ['reconcile_id','reconcile_partial_id'], 50),'account.move.reconcile': (_get_move_from_reconcile, None, 50)}),
        'amount_currency': fields.float('Amount Currency', help="The amount expressed in an optional other currency if it is a multi-currency entry.", digits_compute=dp.get_precision('Account')),
        #~ 'amount_residual_currency': fields.function(_amount_residual, string='Residual Amount in Currency', multi="residual", help="The residual amount on a receivable or payable of a journal entry expressed in its currency (maybe different of the company currency)."),
        #~ 'amount_residual': fields.function(_amount_residual, string='Residual Amount', multi="residual", help="The residual amount on a receivable or payable of a journal entry expressed in the company currency."),
        'currency_id': fields.many2one('res.currency', 'Currency', help="The optional other currency if it is a multi-currency entry."),
        'journal_id': fields.related('move_id', 'journal_id', string='Journal', type='many2one', relation='account.journal', required=True, select=True,
                                store = {
                                    'account.moves': (_get_move_lines, ['journal_id'], 20)
                                }),
        'period_id': fields.related('move_id', 'period_id', string='Period', type='many2one', relation='account.period', required=True, select=True,
                                store = {
                                    'account.moves': (_get_move_lines, ['period_id'], 20)
                                }),
        'blocked': fields.boolean('No Follow-up', help="You can check this box to mark this journal item as a litigation with the associated partner"),
        'partner_id': fields.many2one('res.partner', 'Partner', select=1, ondelete='restrict'),
        'date_maturity': fields.date('Due date', select=True ,help="This field is used for payable and receivable journal entries. You can put the limit date for the payment of this line."),
        'date': fields.related('move_id','date', string='Effective date', type='date', required=True, select=True,
                                store = {
                                    'account.moves': (_get_move_lines, ['date'], 20)
                                }),
        'date_created': fields.date('Creation date', select=True),
        'analytic_lines': fields.one2many('account.analytic.line', 'move_id', 'Analytic lines'),
        'centralisation': fields.selection([('normal','Normal'),('credit','Credit Centralisation'),('debit','Debit Centralisation'),('currency','Currency Adjustment')], 'Centralisation', size=8),
        'balance': fields.function(_balance, fnct_search=_balance_search, string='Balance'),
        'state': fields.selection([('draft','Unbalanced'), ('valid','Balanced')], 'Status', readonly=True, copy=False),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Account', help="The Account can either be a base tax code or a tax code account."),
        'tax_amount': fields.float('Tax/Base Amount', digits_compute=dp.get_precision('Account'), select=True, help="If the Tax account is a tax code account, this field will contain the taxed amount.If the tax account is base tax code, "\
                    "this field will contain the basic amount(without tax)."),
        #~ 'invoice': fields.function(_invoice, string='Invoice',
            #~ type='many2one', relation='account.invoice', fnct_search=_invoice_search),
        'account_tax_id':fields.many2one('account.tax', 'Tax', copy=False),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'company_id': fields.related('account_id', 'company_id', type='many2one', relation='res.company',
                            string='Company', store=True, readonly=True)
    }

    def _get_date(self, cr, uid, context=None):
        if context is None:
            context or {}
        period_obj = self.pool.get('account.period')
        dt = time.strftime('%Y-%m-%d')
        if context.get('journal_id') and context.get('period_id'):
            cr.execute('SELECT date FROM account_moves_lines ' \
                    'WHERE journal_id = %s AND period_id = %s ' \
                    'ORDER BY id DESC limit 1',
                    (context['journal_id'], context['period_id']))
            res = cr.fetchone()
            if res:
                dt = res[0]
            else:
                period = period_obj.browse(cr, uid, context['period_id'], context=context)
                dt = period.date_start
        return dt

    def _get_currency(self, cr, uid, context=None):
        if context is None:
            context = {}
        if not context.get('journal_id', False):
            return False
        cur = self.pool.get('account.journal').browse(cr, uid, context['journal_id']).currency
        return cur and cur.id or False

    def _get_period(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        if context.get('period_id', False):
            return context['period_id']
        account_period_obj = self.pool.get('account.period')
        ids = account_period_obj.find(cr, uid, context=context)
        period_id = False
        if ids:
            period_id = ids[0]
        return period_id

    def _get_journal(self, cr, uid, context=None):
        """
        Return journal based on the journal type
        """
        context = context or {}
        if context.get('journal_id', False):
            return context['journal_id']
        journal_id = False

        journal_pool = self.pool.get('account.journal')
        if context.get('journal_type', False):
            jids = journal_pool.search(cr, uid, [('type','=', context.get('journal_type'))])
            if not jids:
                model, action_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'account', 'action_account_journal_form')
                msg = _("""Cannot find any account journal of "%s" type for this company, You should create one.\n Please go to Journal Configuration""") % context.get('journal_type').replace('_', ' ').title()
                raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
            journal_id = jids[0]
        return journal_id


    _defaults = {
        'blocked': False,
        'centralisation': 'normal',
        'date': _get_date,
        'date_created': fields.date.context_today,
        'state': 'draft',
        'currency_id': _get_currency,
        'journal_id': _get_journal,
        'credit': 0.0,
        'debit': 0.0,
        'amount_currency': 0.0,
        'account_id': lambda self, cr, uid, c: c.get('account_id', False),
        'period_id': _get_period,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.move.line', context=c)
    }
    _order = "date desc, id desc"
    _sql_constraints = [
        ('credit_debit1', 'CHECK (credit*debit=0)',  'Wrong credit or debit value in accounting entry !'),
        ('credit_debit2', 'CHECK (credit+debit>=0)', 'Wrong credit or debit value in accounting entry !'),
    ]

    def _auto_init(self, cr, context=None):
        res = super(account_moves_lines, self)._auto_init(cr, context=context)
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = \'account_moves_lines_journal_id_period_id_index\'')
        if not cr.fetchone():
            cr.execute('CREATE INDEX account_moves_lines_journal_id_period_id_index '
                       'ON account_moves_lines (journal_id, period_id, state, create_uid, id DESC)')
        cr.execute('SELECT indexname FROM pg_indexes WHERE indexname = %s', ('account_moves_lines_date_id_index',))
        if not cr.fetchone():
            cr.execute('CREATE INDEX account_moves_lines_date_id_index ON account_moves_lines (date DESC, id desc)')
        return res

    def _check_no_view(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            if l.account_id.type in ('view', 'consolidation'):
                return False
        return True

    def _check_no_closed(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)
        for l in lines:
            if l.account_id.type == 'closed':
                raise osv.except_osv(_('Error!'), _('You cannot create journal items on a closed account %s %s.') % (l.account_id.code, l.account_id.name))
        return True


    def _check_date(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if l.journal_id.allow_date:
                if not time.strptime(l.date[:10],'%Y-%m-%d') >= time.strptime(l.period_id.date_start, '%Y-%m-%d') or not time.strptime(l.date[:10], '%Y-%m-%d') <= time.strptime(l.period_id.date_stop, '%Y-%m-%d'):
                    return False
        return True

    def _check_currency(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if l.account_id.currency_id:
                if not l.currency_id or not l.currency_id.id == l.account_id.currency_id.id:
                    return False
        return True

    def _check_currency_and_amount(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if (l.amount_currency and not l.currency_id):
                return False
        return True

    def _check_currency_amount(self, cr, uid, ids, context=None):
        for l in self.browse(cr, uid, ids, context=context):
            if l.amount_currency:
                if (l.amount_currency > 0.0 and l.credit > 0.0) or (l.amount_currency < 0.0 and l.debit > 0.0):
                    return False
        return True

    _constraints = [
        (_check_no_view, 'You cannot create journal items on an account of type view or consolidation.', ['account_id']),
        (_check_no_closed, 'You cannot create journal items on closed account.', ['account_id']),
        (_check_date, 'The date of your Journal Entry is not in the defined period! You should change the date or remove this constraint from the journal.', ['date']),
        (_check_currency, 'The selected account of your Journal Entry forces to provide a secondary currency. You should remove the secondary currency on the account or select a multi-currency view on the journal.', ['currency_id']),
        (_check_currency_and_amount, "You cannot create journal items with a secondary currency without recording both 'currency' and 'amount currency' field.", ['currency_id','amount_currency']),
        (_check_currency_amount, 'The amount expressed in the secondary currency must be positive when account is debited and negative when account is credited.', ['amount_currency']),
    ]

    #TODO: ONCHANGE_ACCOUNT_ID: set account_tax_id
    def onchange_currency(self, cr, uid, ids, account_id, amount, currency_id, date=False, journal=False, context=None):
        context = dict(context or {})
        account_obj = self.pool.get('account.account')
        journal_obj = self.pool.get('account.journal')
        currency_obj = self.pool.get('res.currency')
        if (not currency_id) or (not account_id):
            return {}
        result = {}
        acc = account_obj.browse(cr, uid, account_id, context=context)
        if (amount>0) and journal:
            x = journal_obj.browse(cr, uid, journal).default_credit_account_id
            if x: acc = x
        context = dict(context)
        context.update({
                'date': date,
                'res.currency.compute.account': acc,
            })
        v = currency_obj.compute(cr, uid, currency_id, acc.company_id.currency_id.id, amount, context=context)
        result['value'] = {
            'debit': v > 0 and v or 0.0,
            'credit': v < 0 and -v or 0.0
        }
        return result

    def onchange_partner_id(self, cr, uid, ids, move_id, partner_id, account_id=None, debit=0, credit=0, date=False, journal=False, context=None):
        partner_obj = self.pool.get('res.partner')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        val = {}
        val['date_maturity'] = False

        if not partner_id:
            return {'value':val}
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        jt = False
        if journal:
            jt = journal_obj.browse(cr, uid, journal, context=context).type
        part = partner_obj.browse(cr, uid, partner_id, context=context)

        payment_term_id = False
        if jt and jt in ('purchase', 'purchase_refund') and part.property_supplier_payment_term:
            payment_term_id = part.property_supplier_payment_term.id
        elif jt and part.property_payment_term:
            payment_term_id = part.property_payment_term.id
        if payment_term_id:
            res = payment_term_obj.compute(cr, uid, payment_term_id, 100, date)
            if res:
                val['date_maturity'] = res[0][0]
        if not account_id:
            id1 = part.property_account_payable.id
            id2 =  part.property_account_receivable.id
            if jt:
                if jt in ('sale', 'purchase_refund'):
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
                elif jt in ('purchase', 'sale_refund'):
                    val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
                elif jt in ('general', 'bank', 'cash'):
                    if part.customer:
                        val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id2)
                    elif part.supplier:
                        val['account_id'] = fiscal_pos_obj.map_account(cr, uid, part and part.property_account_position or False, id1)
                if val.get('account_id', False):
                    d = self.onchange_account_id(cr, uid, ids, account_id=val['account_id'], partner_id=part.id, context=context)
                    val.update(d['value'])
        return {'value':val}

    def onchange_account_id(self, cr, uid, ids, account_id=False, partner_id=False, context=None):
        account_obj = self.pool.get('account.account')
        partner_obj = self.pool.get('res.partner')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        val = {}
        if account_id:
            res = account_obj.browse(cr, uid, account_id, context=context)
            tax_ids = res.tax_ids
            if tax_ids and partner_id:
                part = partner_obj.browse(cr, uid, partner_id, context=context)
                tax_id = fiscal_pos_obj.map_tax(cr, uid, part and part.property_account_position or False, tax_ids, context=context)[0]
            else:
                tax_id = tax_ids and tax_ids[0].id or False
            val['account_tax_id'] = tax_id
        return {'value': val}
    #
    # type: the type if reconciliation (no logic behind this field, for info)
    #
    # writeoff; entry generated for the difference between the lines
    #
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('fiscalyear'):
            args.append(('period_id.fiscalyear_id', '=', context.get('fiscalyear', False)))
        if context and context.get('next_partner_only', False):
            if not context.get('partner_id', False):
                partner = self.list_partners_to_reconcile(cr, uid, context=context)
                if partner:
                    partner = partner[0]
            else:
                partner = context.get('partner_id', False)
            if not partner:
                return []
            args.append(('partner_id', '=', partner[0]))
        return super(account_moves_lines, self).search(cr, uid, args, offset, limit, order, context, count)
