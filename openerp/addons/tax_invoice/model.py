from openerp import models,fields,api,_
    
    
class res_partner(models.Model):
    
    
    _inherit='res.partner'
        
        
    tin_number=fields.Char('TIN Number' , size=14)  
    cst_number=fields.Char('CST Number' , size=20)
    pan_number=fields.Char('PAN Number' , size=12 , required=True)
    servicetaxnumber=fields.Char('Service Tax Number' , size=20)
    cin_number=fields.Char('CIN Number' , size=25)
    

    
        
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
