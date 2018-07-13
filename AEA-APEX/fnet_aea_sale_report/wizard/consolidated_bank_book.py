# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
import time
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class consolidated_bank_book(osv.osv_memory):
    _name = 'bank.book'
    
    def _get_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    def _get_default_company(self, cr, uid, context=None):
        company_list=[]
        company_ids = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if company_ids==1:
            val=self.pool.get('res.company').search(cr, uid,[])
            rec=[i for i in val if i!=company_ids ]
            company_list.extend(rec)
        else:
            company_list.append(company_ids)
        return company_list
        
    #~ #This function automatically sets the currency to EUR.
    #~ def _get_period(self, cr, uid, context=None):
        #~ res = self.pool.get('account.period').search(cr, uid, [], context=context)
        #~ return res and res[0] or False        
        
    _description = 'Consolidated Bank book'
    _columns = {
        'from_date': fields.date('From Date', required=True),
        'company_ids':fields.many2many('res.company', 'company_report_consolidated_bank', 'bank_id', 'company_id', 'Company'),
        'to_date': fields.date('To Date', required=True),
        'landscape': fields.boolean("Landscape Mode"),
        'company_id': fields.many2one('res.company', 'Company'),

    }

    _defaults = {
         'company_ids': _get_default_company,
         'company_id': _get_company,
         'from_date': lambda *a: time.strftime('%Y-%m-01'),
         'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
         'landscape': True,
         
    }
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        return result
    
    def _print_report(self, cr, uid, ids, data, context=None):
        return self.pool['report'].get_action(cr, uid, [], 'fnet_aea_sale_report.report_consolidated_bank_book', data=data, context=context)
    
    def wiz_print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['landscape','from_date', 'to_date','company_ids'], context=context)[0]
        data['form'].update(self.read(cr, uid, ids, ['landscape'])[0])
        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']
            
        used_context = self._build_contexts(cr, uid, ids, data, context=context)        
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)


class consolidated_bank_journal(osv.osv):

    _name = 'bank.journal'
    
    _columns={    
        'name':fields.char('Name',required=True),
        'active':fields.boolean('Active'),
        'bank_line':fields.one2many('bank.line','line_id','Choose Journal')
    }

    _defaults = {
         'active': True,
         
    }
    
class bank_line(osv.osv):
    
    _name = 'bank.line'
    
    _columns={    
        'line_id':fields.many2one('bank.journal', 'Bank Journal'),
        'journal_id':fields.many2one('account.journal', 'Journal',required=True),
        'company_id':fields.many2one('res.company','Company',required=True),
    }
   
    def onchange_journal_id(self, cr, uid, ids,journal_id,context):
        if not journal_id:
            return False
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        vals = {'value':{} }
        vals['value'].update({'company_id':journal.company_id.id})
        return vals
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
