
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
from openerp.osv import fields, osv
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
import time
import math

from lxml import etree


class stockist_type(osv.osv):
    _name = 'stockist.type'
    _columns = {
           'name':fields.char('Name', size=64, required=True),
           'company_id': fields.many2one('res.company', 'Company'),
               }
               

    
stockist_type()

class res_country_district(osv.osv):
    _name = 'res.country.district'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns  = {
           'name':fields.char('Name', size=64, required=True),
           'state_id':fields.many2one('res.country.state', 'State', required=True),
           'country_id':fields.many2one('res.country', 'Country', required=True),
           'company_id': fields.many2one('res.company', 'Company'),
           }
    _defaults = {
        'company_id': _get_default_company
        }

res_country_district()

class lorry_receipt(osv.osv):
    _name = 'lorry.receipt'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for receipt in self.browse(cr, uid, ids, context=context):
            res[receipt.id] = {
                'weight':0.0,
                'no_case':0.0,
            }
            val_case = val_weight = 0.0
            for line in receipt.lorry_receipt_line:
                val_weight += line.weight
                inv = self.pool.get('account.invoice').browse(cr, uid, line.invoice_id.id)
                for inv_line in inv.invoice_line:
                    prd = self.pool.get('product.product').browse(cr, uid, inv_line.product_id.id)
                    prd_line = self.pool.get('product.template').browse(cr, uid, prd.product_tmpl_id.id)
                    val = inv_line.quantity / prd_line.case_qty
                    val1 = math.ceil(val)
                    val_case += val1
            res[receipt.id]['weight'] = val_weight
            res[receipt.id]['no_case'] = val_case
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('lorry.receipt.line').browse(cr, uid, ids, context=context):
            result[line.lorry_receipt_id.id] = True
        return result.keys()
        
    _columns = {
         'name':fields.char('Name', size=64, readonly=True),
         'partner_id':fields.many2one('res.partner', 'Customer',  required=True),
         'tpt_name':fields.many2one('res.partner', 'TPT.Co.Name', required=True),
         'lr_no':fields.char('Vehicle No', size=15),
         'delivery':fields.boolean('Delivery', readonly=True),
         'method_type': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Type', required=True),
         'no_case': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='No of Case',
            store={
                'lorry.receipt': (lambda self, cr, uid, ids, c={}: ids, ['lorry_receipt_line'], 10),
                'lorry.receipt.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="No of cases."),
         
         'weight': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Weight',
            store={
                'lorry.receipt': (lambda self, cr, uid, ids, c={}: ids, ['lorry_receipt_line'], 10),
                'lorry.receipt.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="No of cases."),
         
         'date':fields.date('Date'),
         'dispatch_through':fields.text('Dispatch Through'),
         'company_id': fields.many2one('res.company', 'Company'),
         'lorry_receipt_line': fields.one2many('lorry.receipt.line', 'lorry_receipt_id', 'Lorry Receipt Line'),
         'state': fields.selection([('draft', 'Draft'),('done', 'Done')],'Status', readonly=True, track_visibility='always'),
         
         }
    _defaults = {
        'company_id': _get_default_company,
        'date': time.strftime("%Y-%m-%d"),
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'lorry.receipt') or '/', 
        'state':'draft',
        }

    def onchange_partner_invoice_id(self, cr, uid, ids, partner_id, context=None):
        result = {}
        list_of_dict=[]
        if partner_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            cr.execute("""select 
                                 ai.id as invoice_id,
                                 ai.date_invoice as date,
                                 ai.del_method as part,
                                 sum(ail.quantity) as product_qty,
                                 sum(ail.quantity * pt.weight) as weight  
                            from account_invoice ai
                            join account_invoice_line ail on (ail.invoice_id = ai.id)
                            join product_product pp on (pp.id = ail.product_id)
                            join product_template pt on (pt.id = pp.product_tmpl_id)
                            where ai.company_id = '%s' and ai.partner_id = '%s' and ai.state = 'open' and ai.type = 'out_invoice' 
                                  and ai.del_method is not null and ai.dispatch is False
                            group by ai.id, ai.date_invoice
                            order by 2 """ % (part.company_id.id, part.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"invoice_id":fid['invoice_id'],"del_method":fid['part'],"date":fid['date'], "product_qty":fid['product_qty'],"weight":fid['weight']})
            result['value'] = {'lorry_receipt_line':list_of_dict,}
        return result
        
        
    def done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        self.write(cr, uid, obj.id, {'delivery':True}, context=context)
        for order in obj.lorry_receipt_line:
            self.pool.get('account.invoice').write(cr, uid, order.invoice_id.id, {'dispatch':True}, context=context)
        return self.write(cr, uid, obj.id, {'state':'done'}, context=context)
        
lorry_receipt()

class lorry_receipt_line(osv.osv):
    _name = 'lorry.receipt.line'
    _columns = {
         
         'lorry_receipt_id':fields.many2one('lorry.receipt', 'Lorry Receipt'),
         'invoice_id':fields.many2one('account.invoice', 'Invoice No'),
         'date':fields.date('Date'),
         'del_method': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Delivery Method'),
         'product_qty':fields.float('Quantity'),
         'weight':fields.float('Weight'),        
           }
           
lorry_receipt_line()

class cheque_details(osv.osv):
    _name = 'cheque.details'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'vou_amount': 0.0,
            }
            vou_amount = 0.0
            for line in order.cheque_details_line:
                vou_amount += line.open_amount
            res[order.id]['vou_amount'] = vou_amount
        return res
    
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('cheque.details.line').browse(cr, uid, ids, context=context):
            result[line.cheque_details_id.id] = True
        return result.keys()
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, track_visibility='always', readonly=True),
        'voucher_id':fields.many2one('account.voucher', 'Voucher', readonly=True),
        'cheque_id':fields.many2one('post.date.cheque', 'Check/DD No', readonly=True),
        'user_id':fields.many2one('res.users', 'User', track_visibility='always', readonly=True),
        'cus_type': fields.selection([('customer', 'Customer'),('supplier', 'Supplier')], 'Type', readonly=True),
        'type': fields.selection([('cheque', 'Cheque'),('dd', 'Demand Draft'), ('neft', 'NEFT')],'Type', readonly=True),
        'date':fields.date('Date', readonly=True),
        'bounce_date':fields.date('Bounce Date', readonly=True),
        'close_date':fields.date('Close Date'),
        'bounce_amount':fields.float('Bank Charge on Bounce', readonly=True), 
        'description':fields.text('Bounce Reason', readonly=True),
        'dd':fields.boolean('DD', readonly=True),
        'against_id':fields.many2one('post.date.cheque', 'Against Check/DD No', readonly=True),
        'amount':fields.float('Cheque/DD Amount', readonly=True),
        'vou_amount': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Voucher Amount',
            store={
                'cheque.details': (lambda self, cr, uid, ids, c={}: ids, ['cheque_details_line'], 10),
                'cheque.details.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The Net amount."),
        'cheque_details_line': fields.one2many('cheque.details.line', 'cheque_details_id', 'Cheque Details Line', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'state': fields.selection([('draft', 'Draft'),('progress', 'Progress'),('cancel', 'Cancel'),('bounce', 'Bounce'), ('done', 'Done')],'Status', readonly=True, track_visibility='always'),
        }
        
    _defaults = {
        'company_id': _get_default_company,
        'state':'draft',
        'date': time.strftime("%Y-%m-%d"),
        'user_id': lambda obj, cr, uid, context: uid,
        }
    
    def set_to_draft(self,cr,uid,ids,context=None):
        obj = self.browse(cr, uid, ids)
        chk = self.pool.get('post.date.cheque')
        chk_sr = chk.search(cr, uid, [('cheque_id', '=', obj.partner_id.id), ('id', '=', obj.cheque_id.id)], context=context)
        chk.write(cr, uid, chk_sr[0], {'state':'open'}, context=context)
        return self.write(cr, uid, ids, {'state':'draft'}, context=context)
        
    def cancel(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        chk = self.pool.get('post.date.cheque')
        chk_sr = chk.search(cr, uid, [('cheque_id', '=', obj.partner_id.id), ('id', '=', obj.cheque_id.id)], context=context)
        chk.write(cr, uid, chk_sr[0], {'state':'cancel'}, context=context)
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        
    def bounce(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        chk = self.pool.get('post.date.cheque')
        chk_sr = chk.search(cr, uid, [('cheque_id', '=', obj.partner_id.id), ('id', '=', obj.cheque_id.id)], context=context)
        chk.write(cr, uid, chk_sr[0], {'state':'bounce'}, context=context)
        return self.write(cr, uid, ids, {'state':'bounce'}, context=context)
        
    def progress(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        chk = self.pool.get('post.date.cheque')
        chk_sr = chk.search(cr, uid, [('cheque_id', '=', obj.partner_id.id), ('id', '=', obj.cheque_id.id)], context=context)
        chk.write(cr, uid, chk_sr[0], {'state':'progress'}, context=context)
        return self.write(cr, uid, ids, {'state':'progress'}, context=context)
        
    def done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        date = time.strftime("%Y-%m-%d")
        chk = self.pool.get('post.date.cheque')
        chk_sr = chk.search(cr, uid, [('cheque_id', '=', obj.partner_id.id), ('id', '=', obj.cheque_id.id)], context=context)
        chk.write(cr, uid, chk_sr[0], {'state':'done', 'amount':obj.amount}, context=context)
        return self.write(cr, uid, ids, {'state':'done', 'close_date':date}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        chk_details = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in chk_details:
            if s['state'] not in ['draft', 'cancel', 'progress', 'done', 'bounce']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete this Details. Its all history of DD/Bank/Cheque Detals!'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
    #~ def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        #~ """
            #~ Add domain 'allow_check_writting = True' on journal_id field and remove 'widget = selection' on the same
            #~ field because the dynamic domain is not allowed on such widget
        #~ """
        #~ if not context: context = {}
        #~ res = super(cheque_details, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        #~ doc = etree.XML(res['arch'])
        #~ nodes = doc.xpath("//field[@name='type']")
        #~ if context.get('type'):
            #~ for node in nodes:
                #~ if context['type'] == 'dd':
                    #~ node.set('domain', "[('type', '=', 'dd'), ('cus_type','=', 'customer')]")
            #~ res['arch'] = etree.tostring(doc)
        #~ return res
        
cheque_details()

class cheque_details_line(osv.osv):
    _name = 'cheque.details.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
         'cheque_details_id': fields.many2one('cheque.details', 'Cheque Details'),
         'invoice_id':fields.many2one('account.invoice', 'Invoice No'),
         'journal_line_id':fields.many2one('account.move.line', 'Journal Items'),
         'original_amount':fields.float('Original Amount'),
         'open_amount':fields.float('Open Balance'),
         'amount':fields.float('Paid Amount'),
         'company_id': fields.many2one('res.company', 'Company'),
         }
         
    _defaults = {
        'company_id': _get_default_company,
        }

cheque_details_line()

