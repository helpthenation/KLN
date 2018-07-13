
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
from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from lxml import etree
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

class aged_partner_balance(osv.osv_memory):
    _name="aged.partner.balance"
    _description = 'Account Aged Trial balance Report'
  
    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = {}
        if chart_account_id:
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            now = time.strftime('%Y-%m-%d')
            domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
            fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
            res['value'] = {'company_id': company_id, 'fiscalyear_id': fiscalyears and fiscalyears[0] or False}
        return res
        
    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'date_from': fields.date("Start Date"),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),
        'period_length':fields.integer('Period Length1 (days)', required=True),
        'period_length1':fields.integer('Period Length2 (days)', required=True),
        'period_length2':fields.integer('Period Length3 (days)', required=True),
        'period_length3':fields.integer('Period Length4 (days)', required=True),
        'period_length4':fields.integer('Period Length5 (days)', required=True),
        'result_selection': fields.selection([('customer','Receivable Accounts'),
                                              ('supplier','Payable Accounts'),
                                              ('customer_supplier','Receivable and Payable Accounts')],
                                              "Partner's", required=True),
        'period_from': fields.many2one('account.period', 'From Period'),
        'period_to': fields.many2one('account.period', 'End Period'),
        'direction_selection': fields.selection([('sales','Sales Person'),
                                              ('executive','Stockiest'),
                                              ('team','Sales Officer')],
                                              "Selection's", required=True),
        'journal_ids': fields.many2many('account.journal', 'fnet_aged_trial_balance_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }
    
    def _check_company_id(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            company_id = wiz.company_id.id
            if wiz.fiscalyear_id and company_id != wiz.fiscalyear_id.company_id.id:
                return False
            if wiz.period_from and company_id != wiz.period_from.company_id.id:
                return False
            if wiz.period_to and company_id != wiz.period_to.company_id.id:
                return False
        return True

    _constraints = [
        (_check_company_id, 'The fiscalyear, periods or chart of account chosen have to belong to the same company.', ['chart_account_id','fiscalyear_id','period_from','period_to']),
    ]
    
    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False
    
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        return result
    
    def _get_all_journal(self, cr, uid, context=None):
        return self.pool.get('account.journal').search(cr, uid ,[])
    
    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'aged.partner.balance':
            company_id = self.pool.get('aged.partner.balance').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False
                  
    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
        'period_length': 7,
        'period_length1': 14,
        'period_length2': 21,
        'period_length3': 28,
        'period_length4': 45,
        'journal_ids': _get_all_journal,
        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.common.report',context=c),
        'chart_account_id': _get_account,
        'target_move': 'posted',
        'result_selection': 'customer',
        'direction_selection': 'sales',
    }
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['result_selection'], context=context)[0])
        return data
        
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['direction_selection','journal_ids','chart_account_id','target_move','company_id','date_from','period_length','period_length1','period_length2','period_length3','period_length4'])[0])

        period_length  = data['form']['period_length']
        period_length1 = data['form']['period_length1']
        period_length2 = data['form']['period_length2']
        period_length3 = data['form']['period_length3']
        period_length4 = data['form']['period_length4']
        if period_length<=0 and period_length1 <=0 and period_length2 <=0 and period_length3 <=0 and period_length4 <=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        res[str(4)] = {
			'name': ( str(1) + '-' + str(data['form']['period_length'])),
            'stop': data['form']['period_length'],
            'start': 1,
        }
        res[str(3)] = {
			'name': (str(int(data['form']['period_length']) + 1) + '-' + str(data['form']['period_length1'])),
            'stop': int(data['form']['period_length1']),
            'start': int(data['form']['period_length']) + 1,
        }
        res[str(2)] = {
			'name': (str(int(data['form']['period_length1']) + 1) + '-' + str(data['form']['period_length2'])),
            'stop': int(data['form']['period_length2']),
            'start': int(data['form']['period_length1']) + 1,
        }
        res[str(1)] = {
			'name': (str(int(data['form']['period_length2']) + 1) + '-' + str(data['form']['period_length3'])),
            'stop': int(data['form']['period_length3']),
            'start': int(data['form']['period_length2']) + 1,
        }
        res[str(0)] = {
			'name': (str(data['form']['period_length4']) + '+'),
            'stop': int(data['form']['period_length4']),
            'start': int(data['form']['period_length3']) + 1,
        }
        
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        return self.pool['report'].get_action(cr, uid, [], 'fnet_aea_function.report_aged_partner_invoice', data=data, context=context)
        
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['result_selection','direction_selection','period_length','period_length1','period_length2','period_length3','period_length4','date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
