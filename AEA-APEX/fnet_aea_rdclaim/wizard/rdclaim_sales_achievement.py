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
class rdclaim_sales_achievement(osv.osv_memory):

    _name='rdclaim.sales.achievement'
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    #~ def _get_period(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ if context.get('period_id', False):
            #~ return context.get('period_id')
        #~ periods = self.pool.get('account.period').find(cr, uid, context=context)
        #~ return periods and periods[0] or False          
    _columns={
        'manager_id' : fields.many2one('res.users','Sales Manager',required=True),
        'sr_id' : fields.many2many('res.users', string='Sales Representative',required=True),
        'stockiest_ids' : fields.many2many('res.partner', string='Stokiest',required=True),
        'company_id': fields.many2one('res.company', 'Company',readonly=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category',required=True),
        'period_id':fields.many2one('account.period','Period',required=True)

    }
    _defaults = {
        'company_id': _get_default_company,
        }

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

    def onchange_sr_ids(self,cr,uid,ids,sr_id,manager_id,company_id,context=None):
        employee=[]
        if sr_id[0][2] != []:
            for i in sr_id[0][2]:
                cr.execute('''
                SELECT DISTINCT
                             res_partner.id
                              FROM res_partner
                              JOIN res_users on res_users.id = res_partner.user_id where  res_users.id =%d '''%(i))
                d = cr.fetchall()
                for j in d:
                    employee.append(j[0])
            result={
                 'value':
                     {'stockiest_ids':employee,
                     }
                   }

            return result
        elif sr_id[0][2] == []:
            if manager_id:
                cr.execute("""select 
                                        smr.member_id as mem_id
                                from crm_case_section ccs
                                join sale_member_rel smr on (smr.section_id = ccs.id)
                                where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
                d = cr.fetchall()
                dept=[]
                for i in range(len(d)):
                   cr.execute('''SELECT DISTINCT
                                 res_partner.id
                                  FROM res_partner
                                  JOIN res_users on res_users.id = res_partner.user_id where  res_users.id=%d'''%(d[i][0]))
                   s = cr.fetchall() 
                   for j in s:
                        dept.append(j[0])
                result={
                     'value':
                         {'stockiest_ids':dept,
                         }
                       }
                return result
    def fields_view_get(self, cr, uid, view_id=None, view_type='form',context=None, toolbar=False, submenu=False):
        return super(rdclaim_sales_achievement, self).\
            fields_view_get(cr, uid, view_id, view_type, context, toolbar,
                            submenu)
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids,['company_id','period_id',
                             'prod_categ_id','manager_id',
                               'sr_id',
                            'stockiest_ids',], context=context)[0])
        return data

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False
        result['period_id'] = 'period_id' in data['form'] and data['form']['period_id'] or False
        result['prod_categ_id'] = 'prod_categ_id' in data['form'] and data['form']['prod_categ_id'] or False
        result['manager_id'] = 'manager_id' in data['form'] and data['form']['manager_id'] or False
        result['sr_id'] = 'sr_id' in data['form'] and data['form']['sr_id'] or False
        result['stockiest_ids'] = 'stockiest_ids' in data['form'] and data['form']['stockiest_ids'] or False
        return result
        
    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        context = context or {}
        if context.get('xls_export'):
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.rdclaim_sales_achievement_xls',
                        'datas': data,
                        }
        else:
                return {'type': 'ir.actions.report.xml',
                        'report_name': 'fnet_aea_rdclaim.report_rdclaim_sales_achievement_webkit',
                        'datas': data,}

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['company_id','period_id',
                                                                'prod_categ_id',
                                                                'manager_id',
                                                                'sr_id',
                                                                'stockiest_ids', ], context=context)[0]
        
        used_context = self._build_contexts(cr, uid, ids, data, context=context)                                                        
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

