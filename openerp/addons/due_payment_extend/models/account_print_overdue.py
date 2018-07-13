# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2014-2016 Openies Services(<http://openies.com>).
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
from openerp.addons.account.report.account_print_overdue import Overdue


class Overdue(Overdue):

    def __init__(self, cr, uid, name, context):
        super(Overdue, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'getLines': self._lines_get,
        })
    
    def _lines_get(self, partner):
        moveline_obj = self.pool['account.move.line']
        movelines = moveline_obj.search(self.cr, self.uid,
                [('partner_id', '=', partner.id),
                    ('account_id.type', 'in', ['receivable', 'payable']),
                    ('state', '<>', 'draft'), ('reconcile_id', '=', False),('blocked', '=', False)])
        return moveline_obj.browse(self.cr, self.uid, movelines)


class report_overdue(osv.AbstractModel):
    _name = 'report.account.report_overdue'
    _inherit = 'report.abstract_report'
    _template = 'account.report_overdue'
    _wrapped_report_class = Overdue



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: