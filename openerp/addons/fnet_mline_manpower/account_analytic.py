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

class account_analytic(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
            
           'employee_line': fields.one2many('analytic.employee.line', 'analytic_id', 'Employee'),
           'leave_lines':fields.many2many('hr.employee.leave', 'employee_analytic_rel', 'account_id', 'leave_id', 'Leave', required=True),
           'sale_id':fields.many2one('sale.order', 'Sale Order'),   
              }
             
    def set_pending(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        vals = {
               'project_id':obj.id,
               'partner_id':obj.partner_id.id,
               'contact_name':obj.sale_id.function,
               'title_id':obj.sale_id.title_id.id,
               'remark':obj.sale_id.remark,
			   'subject':obj.sale_id.subject,
               'lead_id':obj.sale_id.lead_id.id
               }
        sale = self.pool.get('sale.order').create(cr, uid, vals, context=context)
        enq_sr = self.pool.get('sale.enquiry.line').search(cr, uid, [('sale_id', '=', obj.sale_id.id)], context=context)
        for line in self.pool.get('sale.enquiry.line').browse(cr, uid, enq_sr):
            val = {
                  'sale_id':sale,
                  'product_id':line.product_id.id,
                  'description':line.description,
                  'quantity':line.quantity,
                  'uom_id':line.uom_id.id, 
                  'normal_price':line.normal_price,
                  'normal_total':line.normal_total,
                  'ot_price':line.ot_price,
                  'holiday_price':line.holiday_price,
                  }
            self.pool.get('sale.enquiry.line').create(cr, uid, val, context=context)
        return self.write(cr, uid, ids, {'state': 'pending'}, context=context)
        
account_analytic()

class analytic_employee_line(osv.osv):
    _name = 'analytic.employee.line'
    _columns = {
          'analytic_id':fields.many2one('account.analytic.account', 'Employee'),
          'employee_id': fields.many2one('hr.employee', 'Employee'),
           }

analytic_employee_line()
