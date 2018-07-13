from openerp import api, models,fields,_


class AccountInvoice(models.Model):
   
    _inherit = "account.invoice"
   
    
    bank_det = fields.Many2one('res.partner.bank',string='Bank Detail')
    test = fields.Many2one('res.bank',string='Test')
    #~ @api.onchange('partner_id')
    #~ def onchange_acc(self):
        #~ text = num2words(1230, lang='en_IN')
        #~ print'1111111111111111111111111111' ,text
        #~ self.env.cr.execute('select id from res_partner_bank where partner_id=%d'%(self.partner_id.id))
        #~ s = self.env.cr.fetchall()
        #~ print'SSSSSSSSSSSSSSSSSSSSs' , s
        #~ for i in range(len(s)):
            #~ print'222222222222222222222' , s[i][0]
            #~ self.bank_det=s[i][0]
            
           
