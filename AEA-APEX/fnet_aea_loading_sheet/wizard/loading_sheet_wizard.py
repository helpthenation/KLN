from openerp.osv import fields, osv
import time
import datetime
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from openerp import SUPERUSER_ID, api


class loading_sheet_wizard(osv.osv_memory):
    _name = 'loading.sheet.wizard'
    _description = 'Generate Loading Sheet'
            
    _columns = {       
        'invoice_ids'  :fields.many2many('account.invoice','invoice_wizard_rel','invoice_id','wizard_id',"Invoice"),
        }       
        
    def create(self, cr, uid, vals, context=None):    
        if context is None:
            context = {}
        active_ids = context.get('active_ids')
        res = super(loading_sheet_wizard, self).create(cr, uid, vals, context=context)
        for i in active_ids:
            cr.execute('insert into invoice_wizard_rel (invoice_id,wizard_id) values(%s,%s)',(res,i))
        return res      
    
    def print_report(self, cr, uid, ids,context=None):
        obj=self.browse(cr,uid,ids)
        data = {}
        ids=[]
        invoice_obj=self.pool.get('account.invoice').browse(cr, uid, [context.get('active_id',list())], context=context)  
        data.update({'invoice_ids':ids})    
        return {'type': 'ir.actions.report.xml',
                'report_name': 'fnet_aea_loading_sheet.report_tpt',
                'datas': data,
                 'res_model':'loading.sheet.wizard',}


