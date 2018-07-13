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

from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class daywise_brs_report(osv.osv):
    _name = "daywise.brs.report"
    _description = "Daywise BRS"
    _auto = False
    _rec_name = 'date'

    _columns={
		'name': fields.char('Name',readonly=True),
        'account_id':fields.many2one('account.account','Account'),
        'company_id':fields.many2one('res.company','Branch'),
        'move_id':fields.many2one('account.move','Journal Lines'),
        'cheque':fields.char('Cheque No'),
        'date':fields.date('Value Date'),
        'reconsile_date':fields.date('Transaction Date'),
        'balance':fields.float('Debit'),
        'credit':fields.float('Credit'),
        'reconcile':fields.boolean('Reconcile'),
        'description':fields.text('Description'),
        'partner_id':fields.many2one('res.partner','Customer Name'),
        'partner_code':fields.related('partner_id','customer_id',type='char',string='Customer ID'),
        'state':fields.selection([
            ('draft', 'Draft'),
            ('progress', 'Progress'),
            ('done', 'Done'),
            ],'Status'), 

    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'daywise_brs_report')
        cr.execute("""create or replace view daywise_brs_report as (
            SELECT 
              dbl.id,
			  db.name, 
			  dbl.description, 
			  dbl.credit, 
			  dbl.company_id, 
			  dbl.reconsile_date, 
			  dbl.cheque, 
			  dbl.date, 
			  dbl.balance, 
			  dbl.partner_id, 
			  dbl.move_id, 
			  dbl.reconcile,
			  aml.account_id,
			  db.state
			FROM
			  daywise_brs_line dbl
			JOIN daywise_brs db on
			  db.id = dbl.daywise_brs_id
			JOIN account_move_line aml on aml.move_id = dbl.move_id
			GROUP BY
			dbl.id,
			  db.name, 
			  dbl.description, 
			  dbl.credit, 
			  dbl.company_id, 
			  dbl.reconsile_date, 
			  dbl.cheque, 
			  dbl.date, 
			  dbl.balance, 
			  dbl.partner_id, 
			  dbl.move_id, 
			  dbl.reconcile,
			  aml.account_id,
			  db.state)""")
