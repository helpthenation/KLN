# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = { 
         
         'employee': fields.boolean('Employee'),      
               }
res_partner()

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
              }
    def create(self, cr, uid, vals, context=None):
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.partner_id.company_id: 
            user.partner_id.write({'company_id': user.company_id.id, 'employee':True})
        return user_id