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


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    user_id = fields.Many2one(
        comodel_name='res.users', compute='_compute_user_id',
        string='Responsible', store=True)
        
    @api.multi
    @api.depends('requisition_id')
    def _compute_user_id(self):
        for line in self:
            invoices = self.env['purchase.requisition'].search(
                [('id', '=', line.requisition_id.id)])
            print'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',   invoices.user_id[:1] 
            line.user_id = invoices.user_id[:1]
