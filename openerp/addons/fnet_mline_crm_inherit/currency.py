# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import re
import time
import math

from openerp.osv import osv, fields
from openerp.tools.translate import _

class res_currency_inherit(osv.osv):
    
    def _current_rate_convert(self, cr, uid, ids, name, arg, context=None):
        return self._get_current_convert_rate(cr, uid, ids, raise_on_no_rate=False, context=context)
        
    def _get_current_convert_rate(self, cr, uid, ids, raise_on_no_rate=True, context=None):
        if context is None:
            context = {}
        res = {}

        date = context.get('date') or time.strftime('%Y-%m-%d')
        for id in ids:
            cr.execute('SELECT convert_rate FROM res_currency_rate '
                       'WHERE currency_id = %s '
                         'AND name <= %s '
                       'ORDER BY name desc LIMIT 1',
                       (id, date))
            if cr.rowcount:
                res[id] = cr.fetchone()[0]
            elif not raise_on_no_rate:
                res[id] = 0
            else:
                currency = self.browse(cr, uid, id, context=context)
                raise osv.except_osv(_('Error!'),_("No currency rate associated for currency '%s' for the given period" % (currency.name)))
        return res
        
        
    _inherit = 'res.currency'
    _columns = {
     
         'rate_convert': fields.function(_current_rate_convert, string='Convert Rate', digits=(12,6)),
               }


class res_currency_rate_inherit(osv.osv):
    _inherit = 'res.currency.rate'
    
    _columns = {
        
        'convert_rate': fields.float('Convert Rate', digits=(12, 6)),
                       
               }
               
    
    def create(self, cr, uid, vals, context=None):
        current = vals['convert_rate']
        vals.update({'rate': 1.00/current})
        return super(res_currency_rate_inherit, self).create(cr, uid, vals, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        current = vals['convert_rate']
        vals.update({'rate': 1.00/current})
        return super(res_currency_rate_inherit, self).write(cr, uid, ids, vals, context=context)
        
    
