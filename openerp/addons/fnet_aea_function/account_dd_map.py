
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
from openerp.osv import osv,fields
from openerp.tools.translate import _
from openerp.tools.amount_to_text_en import amount_to_text
from lxml import etree

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
  
    _columns = {
        #~ 'amount_in_word_dd' : fields.char("Amount in Word", readonly=True, states={'draft':[('readonly',False)]}),
        #~ 'allow_dd' : fields.related('journal_id', 'allow_dd_writing', type='boolean', string='Allow DD Writing'),
        #~ 'number': fields.char('Number', readonly=True),
    }
  
