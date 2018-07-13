from openerp import api, models,_

from openerp.osv import osv,fields

from openerp.tools.amount_to_text_en import amount_to_text

from datetime import datetime
from itertools import groupby
from operator import itemgetter
import re
from  amt_to_txt  import Number2Words	
class ParticularReport(models.AbstractModel):
   
    _name = 'report.fnet_gst_invoice.report_invoices'
    def get_com(self,obj):
       na = obj.company_id.name
       if na[0:3] == 'AEA':
           na = 'Associated Electrical Agencies'
       else:
           na = 'Apex Agencies'
       return na
    def numToWords(self,obj,amt,join=True):
        num = amt
        wGenerator = Number2Words()
        return wGenerator.convertNumberToWords(num)
      
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_gst_invoice.report_invoices')
        leave_form=self.env['account.invoice'].browse(self._ids)
        docargs = {
            'doc': leave_form,
            'doc_model': report.model,
            'docs': self,
            'doc_ids':self._ids,
        }
        return report_obj.render('fnet_gst_invoice.report_invoices', docargs)
