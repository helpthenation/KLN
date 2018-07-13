from openerp import api, models
from openerp.osv import osv
from openerp import api,_

class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_so_quote_buluff'
       
                         
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_so_quote_buluff')
        sale_obj=self.env['sale.order'].search([('id','=',self.id)])
        docargs = {
            'doc_ids': sale_obj,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('fnet_mline_reportz.report_so_quote_buluff', docargs)                                                                                                                                                        
            




            
