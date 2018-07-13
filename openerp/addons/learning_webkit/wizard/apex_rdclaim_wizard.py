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
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from openerp import SUPERUSER_ID,api
from openerp.addons.report_xls import report_xls
from openerp.osv import orm
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import _
class ApexRDClaimWizard(osv.osv_memory):
    _name = 'apex.rdclaim.wizard'
    
    def _report_xls_fields(self, cr, uid, context=None):
        return [      'company_id',
                          'prod_categ_id',
                          'period_from',
                          'period_to',
                          'date_from',
                          'date_to',
                          'scheme_id',
                          'manager_id',
                          'sr_id',
                          'type',
                          'filter',]

    # Change/Add Template entries
    def _report_xls_template(self, cr, uid, context=None):
        return {}
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
  
    _description = 'RD Claim Report Wizard'
    
    _columns = { 
          'company_id': fields.many2one('res.company', 'Company'),
          'prod_categ_id':fields.many2one('product.category', 'Product Category'),
          'period_from': fields.many2one('account.period', 'Period From'),
          'period_to': fields.many2one('account.period', 'Period To'),
          'date_from':fields.date('Date From'),
          'date_to':fields.date('Date To'),
          'scheme_id':fields.many2one('rd.scheme','Select A Scheme'),
          'manager_id': fields.many2one('res.users', string='Sales Manager'),
          'sr_id': fields.many2many('res.users', string='Sales Representative'),
          'filedata':fields.binary('Download file',readonly=True),
          'filename':fields.char('Filename', size = 64, readonly=True), 
          'type':fields.selection([ ('s', '                 Consolidate Report'),('n', '                Product Wise Report')],'Select A Type Of  Report',required=True),
          'filter': fields.selection(
            [('filter_no', 'No Filters'),
             ('filter_date', 'Date'),
             ('filter_period', 'Periods')], "Filter by", required=True,
            default='filter_no'),
    }

    _defaults = {
         'company_id': _get_default_company,
         
    }
    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        res=[]  
        domain = {} 
        result = {} 
        list_li=[]
        if manager_id:                          
            cr.execute("""select 
                                smr.member_id as mem_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['mem_id'])
            
            domain = {'sr_id':[('id', 'in', tuple(list_li))]}
            result['domain']=domain
            return result

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
            print"RESSSSSSSSSSSSSSSSSSSSSSSSS",res
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
            print'periods',periods
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to':
                            end_period, 'date_from': False, 'date_to': False}
            print'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',res                
        return res    
    def export_contract_product(self, cr, uid, ids, context=None):    
          rst = self.browse(cr, uid, ids)[0]
          company=rst.company_id
          prod_categ=rst.prod_categ_id
          period_f=rst.period_from
          period_t=rst.period_to
          date_f=rst.date_from
          date_t=rst.date_to
          scheme=rst.scheme_id
          manager=rst.manager_id
          sr=rst.sr_id
          datas={'ids':context.get('active_ids', [])}
          print"DDDDDDDDDDAAAAAAAAAATTTTTTTTTAAAAAAAAAAAA",manager
          return {
            'type':'ir.actions.report.xml',
            'report_name': 'report.rdclaim.xls',
            'datas':datas,
            'res_model':'apex.rdclaim.wizard',
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'form',
            'target':'new',
            'nodestroy': True,
            'res_id':ids[0]
    }

    #~ 
    def pre_print_report(self, cr, uid, ids, data, context=None):
        data = super(ApexRDClaimWizard, self).pre_print_report(
            cr, uid, ids, data, context=context)
        # will be used to attach the report on the main account
        data['ids'] = [data['form']['scheme_id']]
        vals = self.read(cr, uid, ids,
                         ['company_id',
                          'prod_categ_id',
                          'period_from',
                          'period_to',
                          'date_from',
                          'date_to',
                          'scheme_id',
                          'manager_id',
                          'sr_id',
                          'type',
                          'filter',
                          ],
                         context=context)[0]
        data['form'].update(vals)
        return data
        #~ 




    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            print'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',data
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'apex_rdclaim_xls',
                    'datas': data}
        else:
            return super(apex_rdclaim_wizard, self)._print_report(
                cr, uid, ids, data, context=context)
ApexRDClaimWizard()
    #~ <field name="manager_id" domain="[('sale_manager', '=', True)]" on_change="onchange_manager_id(manager_id,company_id)"/>
