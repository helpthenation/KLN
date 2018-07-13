from openerp import api, models
from openerp.osv import osv
from openerp import api,_

class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_po_buluff'
       
    def order_code(self,obj):
        if obj:
            enq_obj=self.env['crm.lead'].search([('id','=',obj.order_id.lead_id.id)])
            for rec in enq_obj.product_line:
                if rec.product_id.id==obj.product_id.id:
                    return rec.advanced.reference
                else:
                    return True
                    
            
    def shipping_method(self,obj,value):
        if value=='ship':
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            if sale_obj.picking_policy=='direct':
                return 'Deliver each product when available'
            else:
                return 'Deliver all product at once'
        elif value=='incoterm':
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            return sale_obj.incoterm.name
        elif value=='delivery':
            sale_obj=self.env['sale.order'].search([('name','=',obj.origin)])
            return sale_obj.delivery_period
            
    def  get_job(self,obj):
        s=' '
        self.env.cr.execute("""
                    SELECT distinct aaa.name
                    FROM purchase_order_line pol
                    JOIN account_analytic_account aaa ON pol.account_analytic_id = aaa.id 
                    JOIN purchase_order po ON pol.order_id = po.id
                    WHERE po.id = %d"""%(obj.id))
        q=self.env.cr.fetchall()
        if len(q) >= 1:
            for i in range(len(q)):         
                 s+=str(q[i][0])+ ", "  
            s1=s.rindex(',')      
            s2=s[:s1] +' '  
            return s2
        else:
            return None                  
                   
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_po_buluff')
        pur_obj=self.env['purchase.order'].search([('id','=',self.id)])
        docargs = {
            'doc_ids': pur_obj,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('fnet_mline_reportz.report_po_buluff', docargs)                                                                                                                                                        
            




            
