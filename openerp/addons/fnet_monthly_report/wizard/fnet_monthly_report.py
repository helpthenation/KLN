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

class fnet_monthly_report(osv.osv_memory):
    _name = 'fnet.monthly.report'
    
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

    _description = 'Monthly Sale Report'
    
    _columns = { 
          'period_id': fields.many2one('account.period', 'Select A Period'),   
          'company_id': fields.many2one('res.company', 'Company',readonly=True), 
    }

    _defaults = {
         'company_id': _get_default_company,
         'period_id':_get_period
    }
