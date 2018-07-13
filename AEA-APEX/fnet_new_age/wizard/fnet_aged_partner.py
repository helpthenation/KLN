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

from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from lxml import etree
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

class fnet_aged_partner(osv.osv_memory):
    _name='fnet.aged.partner'
    #~ _inherit = 'account.common.partner.report'
    def onchange_chart_id(self, cr, uid, ids, chart_account_id=False, context=None):
        res = {}
        if chart_account_id:
            company_id = self.pool.get('account.account').browse(cr, uid, chart_account_id, context=context).company_id.id
            now = time.strftime('%Y-%m-%d')
            domain = [('company_id', '=', company_id), ('date_start', '<=', now), ('date_stop', '>=', now)]
            fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
            res['value'] = {'company_id': company_id, 'fiscalyear_id': fiscalyears and fiscalyears[0] or False}
        return res

    _columns = {
        'manager_id': fields.many2many('res.users', string='Sales Manager'),
        'sr_id': fields.many2many('res.users', string='Sales Representative'),
        'stockiest_ids' : fields.many2many('res.partner', string='Stokiest'),
        'payment_term': fields.many2one('account.payment.term', 'Payment Term',required=True),
        'chart_account_id': fields.many2one('account.account', 'Chart of Account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        'company_id': fields.related('chart_account_id', 'company_id', type='many2one', relation='res.company', string='Company', readonly=True),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),
        'date_from': fields.date("Start Date"),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),
        'result_selection': fields.selection([('customer','Receivable Accounts'),
                                              ('supplier','Payable Accounts'),
                                              ('customer_supplier','Receivable and Payable Accounts')],
                                              "Partner's", required=True),                                
        'period_length':fields.integer('Period Length1 (days)', required=True),
        'period_length1':fields.integer('Period Length2 (days)', required=True),
        'period_length2':fields.integer('Period Length3 (days)', required=True),
        'period_length3':fields.integer('Period Length4 (days)', required=True),
        'period_length4':fields.integer('Period Length5 (days)', required=True),
        'direction_selection': fields.selection([('past','Past'),
                                                 ('future','Future')],
                                                 'Analysis Direction', required=True),
        'selection': fields.selection([('sales','Sales Person'),
                                              ('executive','Stockiest'),
                                              ('all','All'),
                                              ('team','Sales Manager')],
                                              "Selection's", required=True),        
        'journal_ids': fields.many2many('account.journal', 'account_aged_trial_balance_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
    }

    def _check_company_id(self, cr, uid, ids, context=None):
        for wiz in self.browse(cr, uid, ids, context=context):
            company_id = wiz.company_id.id
            if wiz.fiscalyear_id and company_id != wiz.fiscalyear_id.company_id.id:
                return False
        return True

    _constraints = [
        (_check_company_id, 'The fiscalyear, periods or chart of account chosen have to belong to the same company.', ['chart_account_id','fiscalyear_id',]),
    ]

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:context = {}
        res = super(fnet_aged_partner, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context.get('active_model', False) == 'account.account':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='chart_account_id']")
            for node in nodes:
                node.set('readonly', '1')
                node.set('help', 'If you print the report from Account list/form view it will not consider Charts of account')
                setup_modifiers(node, res['fields']['chart_account_id'])
            res['arch'] = etree.tostring(doc)
        return res


    def _get_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', user.company_id.id)], limit=1)
        return accounts and accounts[0] or False
    def onchange_date_from(self,cr,uid,ids,date_from,context=None):
        res={}
        user_obj = self.pool['res.users']
        company = user_obj.browse(cr, uid, uid, context=context).company_id
        fyear_obj = self.pool['account.fiscalyear']
        dt_obj=datetime.strptime(date_from, '%Y-%m-%d')
        today = dt_obj.strftime(DATE_FORMAT)
        fyear_ids = fyear_obj.search(
            cr, uid,
            [('date_start', '<=', today),
             ('date_stop', '>=', today),
             ('company_id', '=', company.id)],
            limit=1,
            context=context)
        if fyear_ids:
            fiscal= fyear_ids[0]
            res['value'] = {'fiscalyear_id': fiscal or False}
        return res 
    def onchange_selection(self, cr, uid, ids,selection,context=None):
        result={}
        result={'value':{'sr_id':False,'manager_id':False,'stockiest_ids':False}}
        return result       
    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<=', now), ('date_stop', '>=', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False


    _defaults = {
            'period_length': 7,
            'period_length1': 14,
            'period_length2': 21,
            'period_length3': 28,
            'period_length4': 45,
            'fiscalyear_id': _get_fiscalyear,
            'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'fnet.aged.partner',context=c),
            'chart_account_id': _get_account,
            'target_move': 'posted',
            'result_selection': 'customer',
            'date_from': lambda *a: time.strftime('%Y-%m-%d'),
            'direction_selection': 'past',   
            'selection': 'all',   
    }

    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['fiscalyear'] = 'fiscalyear_id' in data['form'] and data['form']['fiscalyear_id'] or False
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['chart_account_id'] = 'chart_account_id' in data['form'] and data['form']['chart_account_id'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        result['result_selection'] = 'result_selection' in data['form'] and data['form']['result_selection'] or ''
        if data['form']['selection'] == 'team':
            result['manager_id'] = 'manager_id' in data['form'] and data['form']['manager_id'] or False
        elif data['form']['selection'] == 'sales':
            result['sr_id'] = 'sr_id' in data['form'] and data['form']['sr_id'] or False    
        elif data['form']['selection'] == 'executive':
            result['executive'] = 'executive' in data['form'] and data['form']['executive'] or False                
        return result

    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids,[
                           'date_from',  'fiscalyear',  'company_id', 'selection', 'stockiest_ids',  'sr_id', 'manager_id',
                             'journal_ids',
                              'state','result_selection',
                               'period_length',
                            'direction_selection','chart_account_id',], context=context)[0])
        return data
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['payment_term','selection', 'stockiest_ids',  'sr_id', 'manager_id','direction_selection','journal_ids','chart_account_id','target_move','company_id','date_from','period_length','period_length1','period_length2','period_length3','period_length4'])[0])
        day=self.pool['account.payment.term.line']
        fyear_ids=day.search(cr, uid, [('payment_id', '=', data['form']['payment_term'][0])], context=context)
        term=int(day.browse(cr,uid,fyear_ids).days)+1
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        period_length  = data['form']['period_length']
        period_length1 = data['form']['period_length1']
        period_length2 = data['form']['period_length2']
        period_length3 = data['form']['period_length3']
        period_length4 = data['form']['period_length4']
        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")
        if period_length<=0 and period_length1 <=0 and period_length2 <=0 and period_length3 <=0 and period_length4 <=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))
        if data['form']['direction_selection'] == 'past':
            stop = start - relativedelta(days=term)
            res[str(5)] = {
                'name': ( str(1) + '-' + str(term)),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=data['form']['period_length'])
            res[str(4)] = {
                'name': ( str(1+term) + '-' + str(data['form']['period_length'])),
                'stop':start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=data['form']['period_length1'])
            res[str(3)] = {
                'name': (str(int(data['form']['period_length']) + 1) + '-' + str(data['form']['period_length1'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=data['form']['period_length2'])
            res[str(2)] = {
                'name': (str(int(data['form']['period_length1']) + 1) + '-' + str(data['form']['period_length2'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=data['form']['period_length3'])        
            res[str(1)] = {
                'name': (str(int(data['form']['period_length2']) + 1) + '-' + str(data['form']['period_length3'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop - relativedelta(days=1)
            stop = start - relativedelta(days=data['form']['period_length4']) 
            res[str(0)] = {
                'name': (str(data['form']['period_length4']+1) + '+'),
                'stop': start.strftime('%Y-%m-%d'),
                'start': False,
            }
        else:   
            stop = start + relativedelta(days=term)
            res[str(5)] = {
                'name': ( str(1) + '-' + str(term)),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop + relativedelta(days=1)
            stop = start + relativedelta(days=data['form']['period_length'])
            res[str(4)] = {
                'name': ( str(1+term) + '-' + str(data['form']['period_length'])),
                'stop':start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop + relativedelta(days=1)
            stop = start + relativedelta(days=data['form']['period_length1'])
            res[str(3)] = {
                'name': (str(int(data['form']['period_length']) + 1) + '-' + str(data['form']['period_length1'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop + relativedelta(days=1)
            stop = start + relativedelta(days=data['form']['period_length2'])
            res[str(2)] = {
                'name': (str(int(data['form']['period_length1']) + 1) + '-' + str(data['form']['period_length2'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop + relativedelta(days=1)
            stop = start + relativedelta(days=data['form']['period_length3'])        
            res[str(1)] = {
                'name': (str(int(data['form']['period_length2']) + 1) + '-' + str(data['form']['period_length3'])),
                'stop': start.strftime('%Y-%m-%d'),
                'start': stop.strftime('%Y-%m-%d') or False,
            }
            start = stop + relativedelta(days=1)
            stop = start + relativedelta(days=data['form']['period_length4']) 
            res[str(0)] = {
                'name': (str(data['form']['period_length4']+1) + '+'),
                'stop': start.strftime('%Y-%m-%d'),
                'start': False,
            }
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        return self.pool['report'].get_action(cr, uid, [], 'fnet_new_age.report_fnetagedpartnerbalance', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['result_selection','selection', 'stockiest_ids',  'sr_id', 'manager_id','direction_selection','period_length','period_length1','period_length2','period_length3','period_length4','date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'chart_account_id', 'target_move','selection'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
