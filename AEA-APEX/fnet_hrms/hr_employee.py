# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _
#~ from odoo.exceptions import UserError
import time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    target_line = fields.One2many('sale.target.line', 'employee_id', 'Employee')
    
    #~ @api.multi
    #~ def target_sale(self):
        #~ val = self.env['hr.employee'].search([('target_line','>',0)])
        #~ for line in val:
            #~ for i in line.target_line:
                #~ i.write({'target_amount':i.target_amount})
            

class SaleTargetLine(models.Model):
    _name = 'sale.target.line'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Sales Target'

    @api.model
    def _default_currency(self):
        return self.user_id.company_id.currency_id

    @api.depends('target_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.date_from and line.date_from:
                self.env.cr.execute('''
                SELECT COALESCE(SUM(CASE WHEN ai.type = 'out_invoice' THEN ail.price_subtotal ELSE -ail.price_subtotal END),'0') AS amount
                FROM account_invoice ai
                LEFT JOIN account_invoice_line ail on (ail.invoice_id=ai.id)
				LEFT JOIN product_product pp on (ail.product_id=pp.id)
				LEFT JOIN product_template pt on (pp.product_tmpl_id=pt.id)
				LEFT JOIN product_category pc on (pt.categ_id=pc.id)
				LEFT JOIN res_partner rpp on (ai.partner_id=rpp.id)
                JOIN account_move am ON (am.id = ai.move_id)
                WHERE ai.user_id = %s AND ai.date_invoice >= %s 
                AND pc.type= %s
                AND ai.date_invoice <= %s AND ai.state in ('open','paid')
                AND rpp.customer=True AND rpp.supplier=False 
                AND ai.type in ('out_invoice','out_refund') ''', (line.user_id.id,line.date_from,line.type,line.date_to))
                res = self.env.cr.fetchall()
                #~ self.env.cr.execute('''
                #~ SELECT COALESCE(SUM(CASE WHEN ai.type = 'out_invoice' THEN aml.amount_residual ELSE -aml.amount_residual END),'0') AS amount
                #~ FROM account_invoice ai
                #~ JOIN account_move am ON (am.id = ai.move_id)
                #~ JOIN account_move_line aml ON (aml.move_id = am.id)
                #~ WHERE ai.user_id = %s AND ai.date_invoice >= %s AND ai.date_invoice <= %s AND ai.state ='open'
                #~ AND ai.type in ('out_invoice','out_refund') AND aml.user_type_id = 1 ''', (line.user_id.id,line.date_from,line.date_to))
                #~ res1 = self.env.cr.fetchall()
                line.update({
                    'target_achived': res[0][0],
                    'target_balance':line.target_amount - res[0][0],
                    #~ 'outstanding':res1[0][0],
                })

    @api.depends('target_balance')
    def _compute_balance(self):
        target = self.env['sale.target.line']
        for line in self:
            if line.date_from and line.date_from:
                value = target.search([('user_id','=',line.user_id.id),('date_from','<',line.date_from)], limit=1,order='date_from desc')
                line.update({
                    'last_balance': value.target_balance,
                })


    employee_id = fields.Many2one('hr.employee', 'Employee')
    user_id = fields.Many2one('res.users', related='employee_id.user_id', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',default=_default_currency, track_visibility='always')
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    type = fields.Selection([
        ('normal', 'Product'),('cloud','Cloud EYE'),('tech','Technical Support Group'),('db','Database'),('odoo','Odoo'),('can','CAN'),('tod','TOD'),('rental','Rental'),('tec','TEC'),('top','TOP'),('tor','TOR'),('tos','TOS'),
        ('aws', 'AWS')], 'Category Type', default='normal',
        help="A category of the view type is a virtual category that can be used as the parent of another category to create a hierarchical structure.")
    target_amount = fields.Float('Target', required=True)
    #~ last_balance = fields.Monetary(compute='_compute_balance', string='Last Month Balance', readonly=True, store=True,track_visibility='onchange',)
    target_achived = fields.Float(compute='_compute_amount', string='Achieved', readonly=True, store=True)
    target_balance = fields.Float(compute='_compute_amount', string='Target Balance', readonly=True)
    #~ outstanding = fields.Monetary(compute='_compute_amount', string='Outstanding', readonly=True, store=True)
    
