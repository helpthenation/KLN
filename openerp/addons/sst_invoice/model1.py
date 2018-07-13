from openerp import models,fields,api,_

class sale_order(models.Model):
   
    _inherit = 'sale.order'  
    
    delivery_terms = fields.Char('Delivery Term')
   
   
