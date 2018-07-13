# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import models, fields, api


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'
   
    invoice_no = fields.Char(string='Supplier Invoice No',compute='_compute_invoice_ref', store=True)
    inv_pay_ref = fields.Char(string='Payment Reference',compute='_compute_invoice_ref', store=True)
        
    @api.multi
    @api.depends('move_line_id')
    def _compute_invoice_ref(self):
        for line in self:
            if line.move_line_id.invoice:
               line.invoice_no  =  line.move_line_id.invoice.supplier_invoice_number
               line.inv_pay_ref  =  line.move_line_id.invoice.reference
   
