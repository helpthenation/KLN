from openerp.osv import osv
from openerp import api,_
import math
from openerp.exceptions import ValidationError,Warning

class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.proforma_invoice'
                  
    def order_code(self,obj,doc_id):
        if doc_id.journal_id.type=='sale':
            sale_obj=self.env['sale.order'].search([('name','=',doc_id.origin)])
            for line in sale_obj.order_line:
                if line.product_id == obj.product_id:
                    return line.order_code
        elif doc_id.journal_id.type=='purchase':
            pur_obj=self.env['purchase.order'].search([('name','=',doc_id.origin)])
            for line in pur_obj.order_line:
                if line.product_id == obj.product_id:
                    return line.order_code      
        else:
            return True
            
    def po_no(self,obj):
        if obj:
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            val=[]
            for rec in sale_obj.order_line:
                val.append(rec.purchase_id.name)
            if val:
                return val[0]
            else:
                return True
            
    def delivery_period(self,obj):
        if obj:
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            return sale_obj.delivery_period
            
    def incoterm(self,obj):
        if obj:
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            return sale_obj.incoterm.name            

            
    def product_desc(self,obj):
        if obj:
            product_obj=self.env['product.template'].search([('id','=',obj.product_id.product_tmpl_id.id)])
            return product_obj.description   
            
    def duty_calculation(self,obj):
        if obj:
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            for rec in sale_obj.order_line:
                pur_obj=self.env['purchase.order'].search([('id','=',rec.purchase_id.id)])
                return pur_obj.duty_id.amount * obj.amount_untaxed
            
    def freight_calculation(self,obj):
        if obj:
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            for rec in sale_obj.order_line:
                pur_obj=self.env['purchase.order'].search([('id','=',rec.purchase_id.id)])
                for line in pur_obj.costing_line:
                    if line.costing_id.name=='Freight':
                        return line.amount                
            
                                            
    @api.multi
    def render_html(self,data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.proforma_invoice')
        proforma_invoice=self.env['account.invoice'].search([('id','=',self.id)])  
        if proforma_invoice.type in ('out_invoice', 'in_invoice'): 
            docargs = {                    
                    'doc_ids':proforma_invoice,
                    'doc_model': report.model,
                    'docs': self,
                }
            return report_obj.render('fnet_mline_reportz.proforma_invoice', docargs)
        else:
            raise ValidationError("Selected invoice is a refund invoice.")
            
