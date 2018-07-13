#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.report import report_sxw


class invoice_report1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(invoice_report1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_dc_number': self._get_dc_number,
        })
        self.context = context
        
    def _get_dc_number(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        stock_move=self.pool['stock.move']
        stock_id=stock_move.search(self.cr,self.uid,[('origin','=',inv_br_obj.origin)])
        stock_move_obj=stock_move.browse(self.cr,self.uid,stock_id,context=self.context)
        val=''
        for rec in stock_move_obj:
            val= rec.picking_id.name + ','
        return val
    


class wrapped_report_invoice(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.baluff_invoice'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_reportz.baluff_invoice'
    _wrapped_report_class = invoice_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
