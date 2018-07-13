
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

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp



class res_partner_inherit(osv.osv):
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        obj = self.browse(cr, uid, ids)
        s_cr = self.pool.get('scheme.credit')
        s_cr_line = self.pool.get('scheme.credit.line')
        res = {}
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            cr.execute("""SELECT 
                          sum(scl.amount) as val
                    FROM scheme_credit sc
                    JOIN scheme_credit_line scl ON (scl.credit_id = sc.id)
                    WHERE sc.state = 'generate' AND scl.partner_id = '%s' """ % (obj.id))
            line_list = [i for i in cr.dictfetchall()]
            res[order.id] = line_list[0]['val']
        return res
        
    _inherit = 'res.partner'
   
    _columns = {
        'stockist_no':fields.char('Stockist ID', size=64),
        'stockist_id': fields.many2one('stockist.type', 'Stockist Type', required=True),
        'district_id': fields.many2one('res.country.district', 'District'),
        'user_id': fields.many2one('res.users', 'Salesperson', help='The internal user that is in charge of communicating with this contact if any.'),
        'inl_executive_id': fields.many2one('res.users', 'INL Executive/S.O', required=True),
        #~ 'sales_officer_id': fields.many2one('res.users', 'Sales Officer', required=True),
        'credit_note': fields.function(_amount_line, string='Credit Note', digits_compute= dp.get_precision('Account')),
        'tin_vat_no':fields.char('TIN/VAT No', size=50, required=True),
        'cin_no':fields.char('CIN', size=50),
        'cst_no':fields.char('CST No', size=50),
        'pan_no':fields.char('PAN No', size=50),
        'branch_transfer':fields.boolean('Branch'),
        'category_discount':fields.many2one('disc.name','Discount Category'),
        #~ 'transporter_name':fields.boolean('Is a Transporter'),
        'post_cheque_line':fields.one2many('post.date.cheque', 'cheque_id', 'Cheque Line', domain=[('state','in',('open','progress'))]),
               }
    
    _defaults = {
     'stockist_no': lambda obj, cr, uid, context: '/',
     }
    _sql_constraints = [
        ('stockist_no_uniq', 'unique (stockist_no)', 'This Stockist ID already exists !')
    ]
    
    def onchange_stockiest(self, cr, uid, ids, stockist_id, context=None):
        result = {}
        if stockist_id:
            part = self.pool.get('stockist.type').browse(cr, uid, stockist_id)
            if part.name == 'Transporter':
				result['value'] = {"customer":False,}
        return result
            
    def onchange_district(self, cr, uid, ids, district_id=False, state_id=False, country_id=False):
        if district_id:
            district = self.pool.get('res.country.district').browse(cr, uid, district_id)
            return {'value': {'state_id':district.state_id.id, 'country_id': district.country_id.id}}
        return {}
                  
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        cus = vals.get('customer')
        if cus is True:
            if vals.get('stockist_no', '/') == '/':
                vals['stockist_no'] = self.pool.get('ir.sequence').get(cr, uid, 'stokiest.ids', context=context) or '/'
        return super(res_partner_inherit, self).create(cr, uid, vals, context=context)
        
    def name_get(self, cr, uid, ids, context=None): 
        result = []
        for inv in self.browse(cr, uid, ids, context=context):
            result.append((inv.id, "%s - %s" % (inv.name, inv.city or '')))
        return result
        
res_partner_inherit()

class post_date_cheque(osv.osv):
    _name = 'post.date.cheque'
    _columns = {
         'cheque_id':fields.many2one('res.partner', 'Customer'),
         'type': fields.selection([('cheque', 'Cheque'),('dd', 'Demand Draft'), ('neft', 'NEFT')],'Type', required=True),
         'chk_type': fields.selection([('local', 'Local'),('out', 'Outstation')],'Category', required=True),
         'name':fields.char('Check/DD No', size=20, required=True),
         'issue_date':fields.date('Issue Date'),
         'expiry_date':fields.date('Expiry Date'),
         'bank_name':fields.char('Bank Name', size=50),
         'branch_name':fields.char('Branch Name', size=50),
         'amount':fields.float('Amount'),
         'user_id': fields.many2one('res.users', 'User', select=True, track_visibility='onchange'),
         'company_id': fields.many2one('res.company', 'Company', select=1),
         
         'state': fields.selection([('open', 'Open'),('cancel', 'Cancel'), ('bounce', 'Bounce'), ('progress', 'Progress'),('close', 'Closed'),('done', 'Done')],'Status', readonly=True),
         }
         
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'post.date.cheque', context=c),
        'state':'open',
        'type':'cheque',
        'chk_type':'local',
        }

post_date_cheque()

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
         'tin_no':fields.char('TIN No', size=11),
         'cst_no':fields.char('CST No', size=11),
          }

res_company()

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
    
    'sale_manager': fields.boolean('INL Executive/S.O'),
    }
