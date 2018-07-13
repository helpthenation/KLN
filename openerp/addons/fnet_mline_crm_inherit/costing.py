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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_costing(osv.osv):
    _name = 'purchase.costing'
    _columns = {
          'name': fields.char('Name', size=64, required=True),
          'active':fields.boolean('Active'),
            }
    _defaults = {
            'active':True,
            }
purchase_costing()

class costing_duty(osv.osv):
    _name = 'costing.duty'
    _columns = {
           'name': fields.char('Name', size=64, required=True),
           'amount': fields.float('Value',digits_compute= dp.get_precision('Cost'), required=True),
           'active':fields.boolean('Active'),
               }
                        
    _defaults = {
            'active':True,
            }
    
costing_duty()

class costing_margin(osv.osv):
    _name = 'costing.margin'
    _columns = {
           'name': fields.char('Name', size=64, required=True),
           'amount': fields.float('Value', required=True),
           'active':fields.boolean('Active'),
               }
                        
    _defaults = {
            'active':True,
            }
    
costing_margin()
