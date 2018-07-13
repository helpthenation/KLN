from openerp import models, fields, api
from openerp.tools import amount_to_text

class AccountVoucher(models.Model):
    _inherit = "account.voucher"    
    _description = "Account Voucher"

    @api.multi
    def amount_to_text(self, amount, currency):
       amount_in_word=str(amount_to_text(amount)).upper() 
       amount_in_word=amount_in_word.replace('EURO','')
       if currency == 'AED':
          amount_in_word=amount_in_word.replace('CENTS','Fills')
          amount_in_word=amount_in_word.replace('CENT','Fills')
       amount_in_word=amount_in_word+str(' Only')
       return amount_in_word.title()

class AccountMove(models.Model):
    _inherit = "account.move"    
    _description = "Account Move"

    @api.multi
    def amount_to_text(self, amount, currency):
       amount_in_word=str(amount_to_text(amount)).upper() 
       amount_in_word=amount_in_word.replace('EURO','')
       if currency == 'AED':
          amount_in_word=amount_in_word.replace('CENTS','Fills')
          amount_in_word=amount_in_word.replace('CENT','Fills')
       amount_in_word=amount_in_word+str(' Only')
       return amount_in_word.title()
