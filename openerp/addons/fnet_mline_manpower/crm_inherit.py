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
from datetime import date, datetime
import openerp.addons.decimal_precision as dp

class crm_lead_inherit_hr(osv.osv):
    _inherit = 'crm.lead'
    _description = "Lead/Opportunity"
    _rec_name = 'seq_no'
    _columns =  {
          'seq_no': fields.char('Number', size=64, required=True, readonly=True),
          'client_ref':fields.char('Customer Ref', size=64),
          'date_en': fields.date('Date', readonly=True),
          'remark':fields.html('Notes'),
          'subject':fields.html('Subject'),
          'man_line': fields.one2many('crm.man.line', 'crm_man_id', 'Opprtunity'),
          'waiting_for_approval':fields.boolean('Approve')
                 }
    _defaults = {
           'date_en':date.today().strftime('%Y-%m-%d'),
           'seq_no': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'crm.lead') or '/',
           }
         
    def recruitment(self, cr, uid, ids, context=None):
        obj_br = self.browse(cr, uid, ids)
        obj_sr = self.pool.get('hr.job').search(cr, uid, [('lead_id', '=', obj_br.id)], context=context)
        if obj_sr:
            raise osv.except_osv(_('Invalid Action!'), _('Enquiry Related Recruitment Already Created!'))
        else:
            for prod in obj_br.man_line:
                prod_sr = self.pool.get('hr.job').search(cr, uid, [('product_id', '=', prod.product_id.id)], context=context)
                print prod_sr, "DFGDFSGDXGHDTSG"
                if prod_sr:
                    prod_obj = self.pool.get('hr.job').browse(cr, uid, prod_sr[0])
                    print prod_obj.name
                    val = {
                       'lead_id':obj_br.id,
                       'no_of_recruitment':prod.quantity,
                       'partner_id':obj_br.partner_id.id,
                       'address_id':obj_br.partner_id.id,
                          }
                    self.pool.get('hr.job').write(cr, uid, [prod_obj.id], val, context=context)
                    self.pool.get('hr.job').set_recruit(cr, uid, prod_obj.id, context=context)
                else:
                    vals = {
                       'lead_id':obj_br.id,
                       'name':prod.product_id.name,
                       'product_id':prod.product_id.id,
                       'no_of_recruitment':prod.quantity,
                       'partner_id':obj_br.partner_id.id,
                       'address_id':obj_br.partner_id.id,
                       }
                    rec = self.pool.get('hr.job').create(cr, uid, vals, context=context)
                    self.pool.get('hr.job').set_recruit(cr, uid, rec, context=context)          
        return True
        
    def approve_by_manager(self, cr, uid, ids, context=None):
        stage_id=self.pool.get('crm.case.stage').search(cr,uid,([('name','=','Negotiation')]))
        rec=self.write(cr, uid, ids[0], {'stage_id': stage_id[0],'waiting_for_approval':False})
        
crm_lead_inherit_hr()

class crm_man_line(osv.osv):
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot
        return res
        
    def _amount_ot(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot * 1.25
        return res
        
    def _amount_hol(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot * 1.50
        return res
    
    _name = 'crm.man.line'
   
    _columns = {
           
           'crm_man_id': fields.many2one('crm.lead', 'Opportunity'),
           'product_id': fields.many2one('product.product', 'Category'),
           'description':fields.char('Description'),
           'quantity':fields.float('Quantity'),
           'uom_id':fields.many2one('product.uom', 'Unit of Measure'),
           'normal_price':fields.float('Normal Price'),
           'normal_total': fields.function(_amount_line, string='Normal Total', digits_compute= dp.get_precision('Account')),    
           'ot_price': fields.function(_amount_ot, string='OT Price', digits_compute= dp.get_precision('Account')),    
           'holiday_price': fields.function(_amount_hol, string='Holiday Price', digits_compute= dp.get_precision('Account')),    
               }
   
              
    def product_id_change(self, cr, uid ,ids, prod_id=False, des=False, uom=False, type_line=False):
        result = {}
        product_obj = self.pool.get('product.product')
        product_tmpl = self.pool.get('product.template')
        if prod_id:
            prod_obj = product_obj.browse(cr, uid, prod_id)
            prod_tmpl = product_tmpl.browse(cr, uid, prod_obj.product_tmpl_id.id)
            result['value'] = {'product_id':prod_obj.id,
                               'description':prod_tmpl.description,
                               'uom_id':prod_obj.uom_id.id,
                               'normal_price':prod_obj.list_price,
                               }     
        return result
             
crm_man_line()

class crm_make_sale_inherit(osv.osv_memory):
    _inherit = 'crm.make.sale'
    
    _columns={
            'manager_approval':fields.boolean('Verify',default=True),
    }
    
    def manager_approval_func(self, cr, uid, ids, context=None):
        data = context and context.get('active_ids', []) or []
        case_obj = self.pool.get('crm.lead')
        case_rec=case_obj.browse(cr,uid,data)
        stage_id=self.pool.get('crm.case.stage').search(cr,uid,([('name','=','Waiting for approval')]))
        print stage_id
        rec=case_obj.write(cr, uid, data, {'stage_id': stage_id[0],'waiting_for_approval':True})
        
        
    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context = dict(context or {})
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'origin':case.seq_no,
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.datetime.now(),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    'note': sale_obj.get_salenote(cr, uid, [case.id], partner.id, context=context),
                    'lead_id':case.id,
                    'contact_name':case.contact_name,
                    'function':case.function,
                    'title_id':case.title.id,
                    'remark':case.remark,
                    'subject':case.subject
                    
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
                sale_obj.write(cr, uid, [sale_order.id], {'lead_id':case.id}, context=context)
                for line in case.man_line:
                    vals_line = {
                              'sale_id':sale_order.id,
                              'product_id':line.product_id.id,
                              'description':line.description,
                              'quantity':line.quantity,
                              'uom_id':line.uom_id.id, 
                              'normal_price':line.normal_price,
                              'normal_total':line.normal_total,
                              'ot_price':line.ot_price,
                              'holiday_price':line.holiday_price,
                                }
                    self.pool.get('sale.enquiry.line').create(cr, uid, vals_line, context=context)
            if make.close:
                case_obj.case_mark_won(cr, uid, data, context=context)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value


crm_make_sale_inherit()

class sale_order_inh(osv.osv):
    _inherit = 'sale.order'
    _columns = {
          'remark':fields.html('Notes'),
          'subject':fields.html('Subject'),
          'contact_name':fields.char('Contact Name', size=64),
          'function': fields.char('Function', size=64),
          'title_id':fields.many2one('res.partner.title', 'Title'),
          'lead_id':fields.many2one('crm.lead', 'Enquiry', readonly=True),
          'sale_enq_line':fields.one2many('sale.enquiry.line', 'sale_id', 'Sale Enquiry')
             }
             
    def convert_waiting(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'waiting_date'}, context=context)
    
    def convert_contract(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cont = self.pool.get('account.analytic.account')
        con_sr = cont.search(cr, uid, [('id', '=', obj.project_id.id)], context=context)
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'analytic', 'view_account_analytic_account_form')
        res_id = res and res[1] or False,
        if not con_sr:
            vals = {
                    'sale_id':obj.id,
                    'name':obj.lead_id.name or '/',
                    'date_start':obj.date_order,
                    'type':'contract',
                    'use_timesheets':True,
                    'partner_id':obj.partner_id.id
                   }
            cont_obj = cont.create(cr, uid, vals, context=None)
            self.write(cr, uid, ids, {'project_id':cont_obj}, context=context)
            self.write(cr, uid, ids, {'state':'done'}, context=context)
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.analytic.account',
                #~ 'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': cont_obj or False,
                }
        else:
            self.write(cr, uid, ids, {'state':'done'}, context=context)
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res_id],
                'res_model': 'account.analytic.account',
                #~ 'context': "{'type':'out_invoice'}",
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': con_sr[0] or False,
                }
sale_order_inh()

class sale_enquiry_line(osv.osv):
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot
        return res
        
    def _amount_ot(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot * 1.25
        return res
        
    def _amount_hol(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            normal_tot = line.quantity * line.normal_price
            res[line.id] = normal_tot * 1.50
        return res
    _name = 'sale.enquiry.line'
    _columns = {
           'sale_id': fields.many2one('sale.order', 'Sale Enquiry'),
           'product_id': fields.many2one('product.product', 'Category'),
           'description':fields.char('Description'),
           'quantity':fields.float('Quantity'),
           'uom_id':fields.many2one('product.uom', 'Salary Type'),
           'normal_price':fields.float('Normal Price'),
           'normal_total': fields.function(_amount_line, string='Normal Total', digits_compute= dp.get_precision('Account')),    
           'ot_price': fields.function(_amount_ot, string='OT Price', digits_compute= dp.get_precision('Account')),    
           'holiday_price': fields.function(_amount_hol, string='Holiday Price', digits_compute= dp.get_precision('Account')),
        }
        
    
    def product_id_change(self, cr, uid ,ids, prod_id=False, des=False, uom=False, type_line=False):
        result = {}
        product_obj = self.pool.get('product.product')
        product_tmpl = self.pool.get('product.template')
        if prod_id:
            prod_obj = product_obj.browse(cr, uid, prod_id)
            prod_tmpl = product_tmpl.browse(cr, uid, prod_obj.product_tmpl_id.id)
            result['value'] = {'product_id':prod_obj.id,
                               'description':prod_tmpl.description,
                               'uom_id':prod_obj.uom_id.id,
                               'normal_price':prod_obj.list_price,
                               }     
        return result    
sale_enquiry_line()
