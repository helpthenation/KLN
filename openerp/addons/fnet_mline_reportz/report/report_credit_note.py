from openerp import api, models
from openerp.osv import osv,fields
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import datetime
from openerp.exceptions import ValidationError,Warning

class ParticularReport(models.AbstractModel):
   
    _name = 'report.fnet_mline_reportz.report_credit'
                  
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_credit')
        credit_memo = self.env['account.invoice'].search([('id','=',self.id)])
        if credit_memo.type in ('out_refund', 'in_refund'):
            docargs = {
                'doc_ids': credit_memo,
                'doc_model': report.model,
                'docs': self,
            }      
            return report_obj.render('fnet_mline_reportz.report_credit', docargs)
        else:
            raise ValidationError("Selected invoice is not a refund invoice.")


            
    
