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

class dd_bounce_rep(osv.osv_memory):
    _name = 'dd.bounce.rep'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _description = 'Demand Draft Bounce Details Reports'
    _columns = {
        'cus_type': fields.selection([('customer', 'Customer'),('supplier', 'Supplier')], 'Type', required=True),
        'district_ids':fields.many2many('res.country.district', 'district_report_rel2', 'rep_id', 'district_id', 'District'),
        'partner_ids':fields.many2many('res.partner', 'partner_report_rel2', 'rep_id', 'partner_id', 'Customer'),
        'company_id': fields.many2one('res.company', 'Company'),
        'from_date': fields.date('From Date', required=True),
        'to_date': fields.date('To Date', required=True),
        'landscape': fields.boolean("Landscape Mode"),
    }

    _defaults = {
         'company_id': _get_default_company,
         'cus_type':'customer',
         'from_date': lambda *a: time.strftime('%Y-%m-01'),
         'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
         'landscape': True,
         
    }
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        #~ result['type'] = 'type' in data['form'] and data['form']['type'] or ''       
        #~ result['from_date'] = 'from_date' in data['form'] and data['form']['from_date'] or ''       
        #~ result['to_date'] = 'to_date' in data['form'] and data['form']['to_date'] or ''       
        #~ result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False       
        #~ result['partner_ids'] = 'partner_ids' in data['form'] and data['form']['partner_ids'] or False       
        #~ result['district_ids'] = 'district_ids' in data['form'] and data['form']['district_ids'] or False       
        return result
    
    def _print_report(self, cr, uid, ids, data, context=None):
        return self.pool['report'].get_action(cr, uid, [], 'fnet_aea_report.report_dd_bounce', data=data, context=context)
    
    def wiz_print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['landscape','from_date', 'to_date', 'district_ids','partner_ids','type','company_id'], context=context)[0]
        data['form'].update(self.read(cr, uid, ids, ['landscape'])[0])
        for field in ['partner_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        for field in ['district_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']
            
        used_context = self._build_contexts(cr, uid, ids, data, context=context)        
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
