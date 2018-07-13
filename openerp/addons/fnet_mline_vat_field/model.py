from openerp import models,fields,api,_
    
    
class res_company(models.Model):
    _inherit='res.company'
    
    vat_number=fields.Char('VAT No')    
    
class res_partner(models.Model):
	  
    _inherit = 'res.partner'
      
    vat_number=fields.Char('VAT No')            
    # OVERRIDE CONCEPT
    
    

