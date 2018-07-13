# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import tools
from openerp.osv import fields, osv

class lorry_report(osv.osv):
    _name = "lorry.report"
    _description = "Lorry Report"
    _auto = False
    _rec_name = 'date'

    _columns = {
        'date': fields.datetime('Date Order', readonly=True),
    }
    _order = 'date desc'
  
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'expence_report')
        cr.execute("""CREATE or REPLACE VIEW expence_report as (
            SELECT
                 lr.id as id
				 
			FROM lorry_receipt lr
			JOIN lorry_receipt_line lrl ON (lrl.lorry_receipt_id = lr.id)
            )""")

