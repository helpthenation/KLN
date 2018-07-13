from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

class sale_entry_line(models.Model):
    
    _inherit = 'sale.entry.line'
    
    @api.multi
    @api.depends('current_stock','amount')
    def _compute_closing_stock(self):
         for rec in self:
             rec.closing_stock=rec.current_stock+rec.sale_stock - rec.amount
    
    
    closing_stock = fields.Float('Closing Stock',readonly=True,compute='_compute_closing_stock',store=True)
