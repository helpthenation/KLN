from openerp.osv import osv
from openerp import api,_
import math

class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.delivery_note'
                                                                                                                                                        
    #~ def heading(self,obj):
        #~ if obj:
            #~ if obj.picking_type_id.code=='incoming':
                #~ return 'Incoming Note'
            #~ if obj.picking_type_id.code=='outgoing':
                #~ return 'Delivery Note'
            #~ if obj.picking_type_id.code=='internal':
                #~ return 'Internal Transfer'      
                
    def lp_no(self,obj):
        if obj:
            acc_obj=self.env['account.invoice'].search([('origin','=',obj.origin)])
            return acc_obj.lp_no
            
    def product_desc(self,obj):
        if obj:
            product_obj=self.env['product.template'].search([('id','=',obj.product_id.product_tmpl_id.id)])
            return product_obj.description 
            
    @api.multi
    def render_html(self,data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.delivery_note')
        stock_pick=self.env['stock.picking'].search([('id','=',self.id)])        
        
        docargs = {                    
                'doc_ids':stock_pick,
                'doc_model': report.model,
                'docs': self,
            }
        if stock_pick.picking_type_id.code=='outgoing':
            return report_obj.render('fnet_mline_reportz.grn', docargs)
        else:
            raise osv.except_osv(_('ValidateError'), _('Please choose the valid report!')) 
  

            
