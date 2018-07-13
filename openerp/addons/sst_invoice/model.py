from openerp import models,fields,api,_
    
    
class res_company(models.Model):
	
    
    
    _inherit='res.company'
        
        
    tin_number=fields.Char('TIN Number' , size=14)  
    cst_number=fields.Char('CST Number' , size=20)
    off_street = fields.Char('Street')
    off_street1 = fields.Char('Street2')
    off_country = fields.Many2one('res.country','Country')
    off_state = fields.Many2one('res.country','State')
    off_zip = fields.Char('ZIP',size=24)
    off_city = fields.Char('City')
    

class product_category(models.Model):
	  
    _inherit = 'product.template'
      
    code = fields.Char('Code')        
    # OVERRIDE CONCEPT
    
    
    ''' 
   
    @api.multi
    def name_get(self):
 
        res = super(res_partner, self).name_get()
        data = []
        for name in self:
            display_value = ''
            display_value += name.name or ""
            display_value += ',' 
            display_value += name.phone or ""
            
            data.append((name.id, display_value))
        return data
    '''

