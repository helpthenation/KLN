from openerp.osv import osv
from openerp import api,_
import math
from openerp.exceptions import Warning
class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_costing'


    def get_total_price(self,obj):
        if obj:
            total=0.0
            for rec in obj.product_line:
                total=total+rec.ot_total_price
            return ("%.2f" % round(total,2))


    def get_aed_total(self,obj):
        if obj:
            total=0.0
            for rec in obj.product_line:
                total=total+rec.total_price
            return ("%.2f" % round(total,2))
            
    def get_margin_total(self,obj):
        if obj:
            total=0.0
            for rec in obj.product_line:
                total=total+rec.margin_price
            return ("%.2f" % round(total,2))
            
    def get_margin(self,obj):
        if obj:
            total=0.0
            for rec in obj.product_line:
                val=rec.margin_price - rec.total_price
                total= total + val
            return ("%.2f" % round(total,2))          
            
    #~ def get_customer_total(self,obj):
        #~ if obj:
            #~ total=0.0
            #~ for rec in obj.product_line:
                #~ total=total+rec.ot_total_price
            #~ return ("%.2f" % round(total,2))
        
    
    def exchange_rate(self,obj):
        if obj:
            return ("%.2f" % round(obj.exchange_rate,2))
            
    def double_precision(self,obj):
        if obj:
            return ("%.2f" % round(obj,2))
            
    def four_precision(self,obj):
        if obj:
            return ("%.4f" % round(obj,4))
            
            
    @api.multi
    def render_html(self,data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_costing')
        costing_rec=self.env['purchase.order'].search([('id','=',self.id)])
        docargs = {
                'doc_ids':costing_rec,
                'doc_model': report.model,
                'docs': self,
            }
        return report_obj.render('fnet_mline_reportz.report_costing', docargs)










