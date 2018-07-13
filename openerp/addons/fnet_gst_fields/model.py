from openerp import models,fields,api,_
    
    
class res_company(models.Model):
	
    
    
    _inherit='res.company'
        
        
    gst_number=fields.Char('GSTIN Number' , size=20)  
    location_code  = fields.Char('Location Code',size=3)
    

class product_category(models.Model):
	  
    _inherit = 'product.category'
      
    hsn_code = fields.Char('HSN Code')    
    
class res_partner(models.Model):
	  
    _inherit = 'res.partner'
      
    gst_number=fields.Char('GSTIN Number' , size=20)            
    # OVERRIDE CONCEPT
    
class account_move(models.Model):

    _inherit= 'account.move'

    sac_no=fields.Char('SAC No', size=21) 

