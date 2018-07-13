from openerp.osv import osv
from openerp import api
import math
class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_aea_report.travel_expense_formats'
    
    @api.multi
    def render_html(self,data=None):
        
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_aea_report.travel_expense_formats')
        travel_expense=self.env['travel.expense'].search([('id','=',self.id)])        
        
        docargs = {                    
                'doc_ids':travel_expense,
                'doc_model': report.model,
                'docs': self,
            }
        return report_obj.render('fnet_aea_report.travel_expense_formats', docargs)
  
