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
import xlwt
from xlsxwriter.workbook import Workbook
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from openerp import SUPERUSER_ID,api
from openerp.addons.report_xls import report_xls
import time
from lxml import etree

from openerp.osv.orm import setup_modifiers


class rdclaim_wizard(osv.osv_memory):
    _name = 'rdclaim.wizard'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False        

    _description = 'RD Claim Report XLS'
    
    _columns = { 
          'period_from': fields.many2one('account.period', 'Period From'),
          'period_to': fields.many2one('account.period', 'Period To'),
          'date_from':fields.date('Date From'),
          'date_to':fields.date('Date To'), 
          'company_id': fields.many2one('res.company', 'Company',readonly=True),
          'prod_categ_id':fields.many2one('product.category', 'Product Category'),
          'scheme_id':fields.many2one('rd.scheme','Select A Scheme'),
          'manager_id': fields.many2one('res.users', string='Sales Manager',required=True),
          'sr_id': fields.many2many('res.users', string='Sales Representative',required=True),
          'type':fields.selection([ ('s', '                 Consolidate Report'),('n', '                Product Wise Report')],'Select A Type Of  Report',required=True,default='s'),
          'filter': fields.selection(
            [('filter_no', 'No Filters'),
             ('filter_date', 'Date'),
             ('filter_period', 'Periods')], "Filter by", 
            default='filter_no'),
    }

    _defaults = {
         'company_id': _get_default_company,
         #~ 'manager_id':_get_manager_ids
    }
    def onchange_scheme_id(self, cr, uid, ids,scheme_id,context=None):
        sch_per=self.pool.get('rd.scheme').browse(cr,uid,scheme_id)
        if scheme_id:
            result={
                 'value':
                     {
                      'prod_categ_id':sch_per.prod_categ_id.id,                      
                     }}
            return result            
    def onchange_type(self, cr, uid, ids,types,context=None):
        result={}
        result={'value':{'prod_categ_id':False,'scheme_id':False,'manager_id':False,'sr_id':False,'filter':'filter_no'}}
        return result
        
        
    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        res = {}
        domain = []
        result = {} 
        list_li=[]
        if manager_id:                         
            cr.execute("""select 
                                    smr.member_id as mem_id
                            from crm_case_section ccs
                            join sale_member_rel smr on (smr.section_id = ccs.id)
                            where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            sid=[]
            for fid in line_list:
                list_li.append(fid['mem_id'])
            result={
                 'value':
                     {
                      'sr_id':list_li,                      
                     },
                 'domain': {'sr_id':[('id', 'in', tuple(list_li))]}  
                   }

            return result
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:context = {}
        res = super(rdclaim_wizard, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context.get('active_model', False) == 'rdclaim.wizard':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='company_id']")
            for node in nodes:
                node.set('readonly', '1')
                node.set('help', 'If you print the report from Account list/form view it will not consider Charts of account')
                setup_modifiers(node, res['fields']['company_id'])
            res['arch'] = etree.tostring(doc)
        return res
    def onchange_filter(self, cr, uid, ids, filter='filter_no',context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': False,
                'date_to': False,
            }
        if filter == 'filter_date':
            date_from, date_to = time.strftime(
                    '%Y-01-01'), time.strftime('%Y-%m-%d')
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': date_from,
                'date_to': date_to
            }

        if filter == 'filter_period':
            start_period = end_period = False
            cr.execute('''
                    SELECT * FROM (SELECT p.id
                               FROM account_period p                               
                               WHERE COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               
                               WHERE 
                                p.date_start < NOW()
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''')
            periods = [i[0] for i in cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to':
                            end_period, 'date_from': False, 'date_to': False}            
        return res        
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids,[
                           'date_from',  'date_to', 
                            'period_from', 'period_to',
                             'filter', 'company_id',
                             'prod_categ_id',
                              'scheme_id','manager_id',
                               'sr_id',
                            'type',], context=context)[0])
        return data

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False
        result['prod_categ_id'] = 'prod_categ_id' in data['form'] and data['form']['prod_categ_id'] or False
        result['scheme_id'] = 'scheme_id' in data['form'] and data['form']['scheme_id'] or False
        result['manager_id'] = 'manager_id' in data['form'] and data['form']['manager_id'] or False
        result['sr_id'] = 'sr_id' in data['form'] and data['form']['sr_id'] or False
        result['type'] = 'type' in data['form'] and data['form']['type'] or ''
        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
        if data['form']['filter'] == 'filter_period':
            if not data['form']['period_from'] or not data['form']['period_to']:
                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period.'))
            result['period_from'] = data['form']['period_from']
            result['period_to'] = data['form']['period_to']
        return result
    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        context = context or {}
        if data['form']['type']=='n':
            if context.get('xls_export'):
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.rdclaim_xls',
                        'datas': data,}
            else:
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.report_rdclaim_webkit',
                        'datas': data,
                         'res_model':'rdclaim.wizard',}
        elif data['form']['type']=='s':
            if context.get('xls_export'):
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.rdclaim_consolidated_xls',
                        'datas': data,
                         'res_model':'rdclaim.wizard',}
            else:               
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.report_rdclaim_consolidate_webkit',
                        'datas': data,
                         'res_model':'rdclaim.wizard',}
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, [
        'date_from',  'date_to', 
                                                               'period_from', 'period_to',
                                                                'filter', 'company_id',
                                                                'prod_categ_id',
                                                                'scheme_id','manager_id',
                                                                  'sr_id',
                                                                  'type', ], context=context)[0]
        for field in ['period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

