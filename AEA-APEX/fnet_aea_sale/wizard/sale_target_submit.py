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

from openerp.osv import osv
from openerp.tools.translate import _

class sale_target_submit(osv.osv_memory):
    """
    This wizard will submit the all the selected Sale Target
    """

    _name = "sale.target.submit"
    _description = "Submit the selected Sale Target"

    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        proxy = self.pool['sale.target']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if record.state not in ('draft',):
                raise osv.except_osv(_('Warning!'), _("Selected Sale Target(s) cannot be confirmed as they are not in 'Draft' state."))
            else:
                record.write({'state':'done'})
            record.signal_workflow('submit')
            
        return {'type': 'ir.actions.act_window_close'}




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
