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
import openerp.addons.decimal_precision as dp

class duty_amount(osv.osv_memory):
    _name = "duty.amount"
    _description = "Change Duty Amount"
    _columns = {
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Product Price'), required=True),
    }

    def change_amount(self, cr, uid, ids, context=None):
        total = []
        active_ids = context and context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        purchase_id = self.pool.get('purchase.order').browse(cr, uid, active_ids)
        total += [prod_line.ot_total_price for prod_line in purchase_id.product_line]
        cnf_amt = [cost_line.amount for cost_line in purchase_id.costing_line]
        cnf = sum(cnf_amt) + data.amount + sum(total)
        cost = cnf / sum(total)
        self.pool.get('purchase.order').write(cr, uid, active_ids, {'duty_amount':data.amount, 'cnf_amount':cnf, 'cost_amount':cost})
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
