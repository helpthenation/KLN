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
#~ import itertools
from lxml import etree
#~ from openerp import models, fields, api, _

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
from datetime import date, datetime
from datetime import datetime, timedelta
    
class crm_lead_inherit(osv.osv):
    _inherit = 'crm.lead'
    _rec_name = 'seq_no'
    _description = "Lead/Opportunity"
    _columns =  {
         
         'seq_no': fields.char('Number', size=64, required=True, readonly=True),
         'partner_id':fields.many2one('res.partner', 'Customer', required=True),
         'client_order_ref': fields.char('Customer Ref', size=64,required=False),
         'lead':fields.boolean('lead'),
         'date': fields.date('Date'),
         'submission_date':fields.date('Closing Date'),
         'product_line': fields.one2many('crm.lead.line', 'crm_lead_id', 'Opprtunity'),
         'state': fields.selection([
            ('new', 'New'),
            ('request', 'Call For Bid Rised'),
            ('pur_request', 'Purchase Request Rised'),
            ('so_quote', 'SO Quote Rised'),
            ('sale_confirm', 'Sale Order Confirmed'),
            ('done', 'done'),
            ], 'Status', readonly=True),          
                }
    _defaults = {
                'state':'new',
                'lead':False,
                'date':date.today().strftime('%Y-%m-%d'),
                #~ 'seq_no': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'crm.lead') or '/',
                'seq_no': lambda obj, cr, uid, context: '/',
                }
     
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('seq_no', '/') == '/':
            vals['seq_no'] = self.pool.get('ir.sequence').get(cr, uid, 'crm.lead', context=context) or '/'
        return super(crm_lead_inherit, self).create(cr, uid, vals, context=context) 
        
                  
    def _supplier_get(self, cr, uid, lead_line, context=None):
        res = []
        if lead_line.product_id.product_tmpl_id.seller_ids:
            cr.execute(''' SELECT 
                                ps.name 
                       FROM
                                product_product pp
                       LEFT JOIN 
                                product_supplierinfo ps
                       ON 
                                ps.product_tmpl_id = pp.product_tmpl_id
                       WHERE
                                pp.id = '%s' ''' % (lead_line.product_id.id))
            sup_ids = cr.fetchall()
            for sup_id in sup_ids:
                sup = self.pool.get('res.partner').browse(cr, uid, sup_id)
                res.append(sup.id)
        return res


    
    def create_rfq(self, cr, uid, ids, context=None):
        enq_bro = self.browse(cr, uid, ids)
        vals = {
                'lead_seq_id':enq_bro.id,
                #~ 'date_end':enq_bro.submission_date,
                   }
        request_sr = self.pool.get('purchase.requisition').search(cr, uid, [('lead_seq_id', '=', enq_bro.id)], context=context)
        if request_sr:
            raise osv.except_osv(_('Invalid Action!'), _('Enquiry Related Request Already Created!'))
        else:
            req = self.pool.get('purchase.requisition').create(cr, uid, vals, context=None)
            for lead_line in enq_bro.product_line:
                res = self._supplier_get(cr, uid, lead_line, context=None)
                vals_line = {
                    'requisition_id':req,
                    'lead_line_id':lead_line.id,
                    'product_id':lead_line.product_id.id,
                    'item_no':lead_line.item_no,
                    'product_uom_id':lead_line.uom_id.id,
                    'part_no':lead_line.part_no,
                    'make_no':lead_line.make_no,
                    'product_qty':lead_line.quantity,
                    'partner_ids': [(6, 0, res)] or False,
                    }

                self.pool.get('purchase.requisition.line').create(cr, uid, vals_line, context=None)
        return self.write(cr, uid, ids, {'state': 'request'}, context=context)
        
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_name': partner.parent_id.name if partner.parent_id else partner.name,
                'contact_name': partner.name if partner.parent_id else False,
                'title': partner.title and partner.title.id or False,
                'street': partner.street,
                'street2': partner.street2,
                'city': partner.city,
                'state_id': partner.state_id and partner.state_id.id or False,
                'country_id': partner.country_id and partner.country_id.id or False,
                'email_from': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'fax': partner.fax,
                'zip': partner.zip,
                'function': partner.function,
            }
        return {'value': values}
    
crm_lead_inherit()

class crm_lead_line(osv.osv):
    _name = 'crm.lead.line'
    _columns = {
           
           'item_no':fields.char('Item No'),
           'crm_lead_id': fields.many2one('crm.lead', 'Opportunity'),
           'product_id': fields.many2one('product.product', 'Product'),
           'advanced':fields.many2one('cutomer.product.line', 'Advanced'),
           'description':fields.char('Description'),
           'part_no':fields.char('Part No', size=64),
           'make_no':fields.char('Make', size=64),
           'quantity':fields.float('Quantity'),
           'uom_id':fields.many2one('product.uom', 'Unit of Measure'),
               }
    def product_id_change(self, cr, uid ,ids, prod_id=False, des=False, uom=False):
        result = {}
        product_obj = self.pool.get('product.product')
        if prod_id:
            prod_obj = product_obj.browse(cr, uid, prod_id)
            result['value'] = {'product_id':prod_obj.id,
                               'description':prod_obj.description,
                               'part_no':prod_obj.product_tmpl_id.part_no,
                               'make_no':prod_obj.product_tmpl_id.make_no,
                               'uom_id':prod_obj.uom_id.id}
        return result
        
    def advanced_change(self, cr, uid, ids, advanced=False, product_id=False):
        domain = {}
        product_obj = self.pool.get('product.product')
        if advanced:
            print advanced
            line = self.pool.get('cutomer.product.line').browse(cr, uid, advanced)
            tmpl = self.pool.get('product.template').search(cr, uid, [('id', '=', line.product_cust_id.id)])
            prod = self.pool.get('product.product').search(cr, uid, [('product_tmpl_id', '=', tmpl[0])])
            obj_br = self.pool.get('product.product').browse(cr, uid, prod[0])
            domain['value'] = {'product_id':obj_br.id}
        return domain 
        
crm_lead_line()


