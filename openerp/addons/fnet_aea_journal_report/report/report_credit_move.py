from openerp import api, models,_

from openerp.osv import osv,fields

from openerp.tools.amount_to_text_en import amount_to_text

from datetime import datetime
from itertools import groupby
from operator import itemgetter
import re
from  amt_to_txt  import Number2Words	

class ParticularReport(models.AbstractModel):
   
    _name = 'report.fnet_aea_journal_report.report_credit_move'
    
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
        report = report_obj._get_report_from_name('fnet_aea_journal_report.report_credit_move')
        leave_form=self.env['account.move'].browse(self.ids)
        account_inv = self.env['account.move.line'].search([('id','in',self.ids)])
        for i in leave_form:
			if i.journal_id.code != 'CN':
				raise osv.except_osv(_("Warning!"), _("Only Credit Note Journal Are Allowed ...!! "))
        docargs = {
                'doc_ids': self._ids,
                #~ 'sale':sale_order,
                'doc':leave_form,
                'account':account_inv,
                'doc_model': report.model,
                'docs': self,
            }

        return report_obj.render('fnet_aea_journal_report.report_credit_move', docargs)
