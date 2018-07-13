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
import base64

class res_partner_inherit(osv.osv):
    _inherit = 'res.partner'
    _columns = {
            
            'file':fields.binary('Bussiness Card'),
            'enquiry_date': fields.float('Enquiry Date Prior', required=True),
            'contact':fields.text('Contact'), 
           
           }
    _defaults = {
           'enquiry_date':2.00,
           }
res_partner_inherit()          
