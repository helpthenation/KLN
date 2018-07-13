import itertools
import math
from lxml import etree

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

class account_tax_code(models.Model):
        _inherit = 'account.tax'
        
        ref_code=fields.Char(string="Tax  Reference Code")
