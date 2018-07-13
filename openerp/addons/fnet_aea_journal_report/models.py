from openerp.osv import fields, osv
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from lxml import etree
class account_move(osv.osv):
    _inherit='account.voucher' 
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    _columns={
            'company_id': fields.many2one('res.company', 'Company',readonly=True)
    }
    _defaults = {
         'company_id': _get_default_company,
    }
