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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from datetime import datetime
from openerp.tools.float_utils import float_compare

class purchase_order_inherit(osv.osv):
    _inherit = 'purchase.order'
    _columns = {
           'history_line':fields.one2many('history.order.line', 'purchase_history_id', 'History', readonly=True),
           'costing_line':fields.one2many('purchase.costing.line', 'purchase_costing_id', 'Costing'),
           'product_line':fields.one2many('purchase.product.line', 'purchase_product_id', 'Product'),
           'cost_history_line':fields.one2many('cost.history.line', 'purchase_cost_history_id', 'Cost History'),
           'currency_cost_id':fields.many2one('res.currency', 'Currency', readonly=True),
           'exchange_rate':fields.float('Exchange Rate'),
           'lead_id':fields.many2one('crm.lead', 'Enquiry', readonly=True),
           'contact_name':fields.char('Contact Name', size=64),
           'function': fields.char('Function', size=64),
           'title_id':fields.many2one('res.partner.title', 'Title'),
           'cnf_amount': fields.float('CNF', readonly=True),
           'duty_amount':fields.float('Duty', readonly=True),
           'cost_amount': fields.float('Cost', digits_compute= dp.get_precision('Cost') ,readonly=True),
           'duty_id': fields.many2one('costing.duty', 'Duty'),
           'margin_id': fields.many2one('costing.margin', 'Margin'),
           'note_document': fields.html('Documents'),
           'subject': fields.html('Subject'),
           'signature': fields.html('Signature'),
           'delivery_period':fields.char('Delivery Period'),
           'shipping_method':fields.char('Shipping Method'),
           'vendor_payment_term':fields.char('Payment Term'),
           'validity':fields.integer('Validity'),
           'offer' : fields.float('Offer',digits=(16, 0), readonly = True),
           #~ 'po_sale_ids': fields.many2many('sale.order','sale_po_rel', 'po_id', 'sale_id', 'Job Number'),
           'cost_status': fields.selection([('draft', 'Load Currency'),
                                           ('progress', 'Progress'),
                                           ('convertion', 'Convertion'),
                                           ('margin', 'Margin'),
                                           ('done', 'Done')],'Status'),
           'duty_exempted':fields.boolean('Duty Exempted'),
           'is_merged_po':fields.boolean('Merged PO'),
           'user_id': fields.related('lead_id', 'user_id', type='many2one', relation='res.users', string='Responsible',store=True),
        
              }
    _defaults = {
                'cost_status':'draft',
                'offer': 1,
                'cost_amount':1.00,
                'duty_exempted':True,
                'is_merged_po':False
                }

    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        """Collects require data from purchase order line that is used to create invoice line
        for that purchase order line
        :param account_id: Expense account of the product of PO line if any.
        :param browse_record order_line: Purchase order line browse record
        :return: Value for fields of invoice lines.
        :rtype: dict
        """
        return {
            'name': order_line.name,
            'account_id': account_id,
            'price_unit': order_line.price_unit or 0.0,
            'quantity': order_line.product_qty,
            'product_id': order_line.product_id.id or False,
            'uos_id': order_line.product_uom.id or False,
            'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            'account_analytic_id': order_line.account_analytic_id.id or False,
            'purchase_line_id': order_line.id,
            'item_no':order_line.item_no,
        }
    # picking create

    def action_picking_create(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids):
            picking_vals = {
                'picking_type_id': order.picking_type_id.id,
                'partner_id': order.partner_id.id,
                'date': order.date_order,
                'origin': order.name,
                'request_id':order.requisition_id.id,
                'lead_id':order.lead_id.id,
            }
            picking_id = self.pool.get('stock.picking').create(cr, uid, picking_vals, context=context)
            self._create_stock_moves(cr, uid, order, order.order_line, picking_id, context=context)
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, group_id, context=None):
        ''' prepare the stock move data from the PO line. This function returns a list of dictionary ready to be used in stock.move's create()'''
        print'%%%%%%%%%%%%%%%%%%%%%%%',order_line.item_no
        product_uom = self.pool.get('product.uom')
        price_unit = order_line.price_unit
        if order_line.taxes_id:
            taxes = self.pool['account.tax'].compute_all(cr, uid, order_line.taxes_id, price_unit, 1.0,
                                                             order_line.product_id, order.partner_id)
            price_unit = taxes['total']
        if order_line.product_uom.id != order_line.product_id.uom_id.id:
            price_unit *= order_line.product_uom.factor / order_line.product_id.uom_id.factor
        if order.currency_id.id != order.company_id.currency_id.id:
            #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
        res = []
        if order.location_id.usage == 'customer':
            name = order_line.product_id.with_context(dict(context or {}, lang=order.dest_address_id.lang)).display_name
        else:
            name = order_line.name or ''
        move_template = {
            'name': name,
            'product_id': order_line.product_id.id,
            'product_uom': order_line.product_uom.id,
            'product_uos': order_line.product_uom.id,
            'date': order.date_order,
            'date_expected': fields.date.date_to_datetime(self, cr, uid, order_line.date_planned, context),
            'location_id': order.partner_id.property_stock_supplier.id,
            'location_dest_id': order.location_id.id,
            'picking_id': picking_id,
            'partner_id': order.dest_address_id.id,
            'move_dest_id': False,
            'state': 'draft',
            'purchase_line_id': order_line.id,
            'company_id': order.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': order.picking_type_id.id,
            'group_id': group_id,
            'procurement_id': False,
            'origin': order.name,
            'route_ids': order.picking_type_id.warehouse_id and [(6, 0, [x.id for x in order.picking_type_id.warehouse_id.route_ids])] or [],
            'warehouse_id':order.picking_type_id.warehouse_id.id,
            'invoice_state': order.invoice_method == 'picking' and '2binvoiced' or 'none',
            'item_no':order_line.item_no,
        }

        diff_quantity = order_line.product_qty
        for procurement in order_line.procurement_ids:
            procurement_qty = product_uom._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, to_uom_id=order_line.product_uom.id)
            tmp = move_template.copy()
            tmp.update({
                'product_uom_qty': min(procurement_qty, diff_quantity),
                'product_uos_qty': min(procurement_qty, diff_quantity),
                'move_dest_id': procurement.move_dest_id.id,  #move destination is same as procurement destination
                'group_id': procurement.group_id.id or group_id,  #move group is same as group of procurements if it exists, otherwise take another group
                'procurement_id': procurement.id,
                'invoice_state': procurement.rule_id.invoice_state or (procurement.location_id and procurement.location_id.usage == 'customer' and procurement.invoice_state=='2binvoiced' and '2binvoiced') or (order.invoice_method == 'picking' and '2binvoiced') or 'none', #dropship case takes from sale
                'propagate': procurement.rule_id.propagate,
            })
            diff_quantity -= min(procurement_qty, diff_quantity)
            res.append(tmp)
        #if the order line has a bigger quantity than the procurement it was for (manually changed or minimal quantity), then
        #split the future stock move in two because the route followed may be different.
        if float_compare(diff_quantity, 0.0, precision_rounding=order_line.product_uom.rounding) > 0:
            move_template['product_uom_qty'] = diff_quantity
            move_template['product_uos_qty'] = diff_quantity
            res.append(move_template)
        return res

    #~ # invoi
    #~ def _prepare_inv_line(self, cr, uid, ids, account_id, order_line, context=None):
        #~ obj = self.browse(cr, uid, ids)
        #~ if obj.cost_amount > 0.00:
            #~ """Collects require data from purchase order line that is used to create invoice line
            #~ for that purchase order line
            #~ :param account_id: Expense account of the product of PO line if any.
            #~ :param browse_record order_line: Purchase order line browse record
            #~ :return: Value for fields of invoice lines.
            #~ :rtype: dict
            #~ """
            #~ return {
            #~ 'name': order_line.name,
            #~ 'account_id': account_id,
            #~ 'price_unit': order_line.price_unit * obj.cost_amount or 0.0,
            #~ 'quantity': order_line.product_qty,
            #~ 'product_id': order_line.product_id.id or False,
            #~ 'uos_id': order_line.product_uom.id or False,
            #~ 'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            #~ 'account_analytic_id': order_line.account_analytic_id.id or False,
            #~ 'purchase_line_id': order_line.id,
                 #~ }
        #~ else:
            #~ """Collects require data from purchase order line that is used to create invoice line
            #~ for that purchase order line
            #~ :param account_id: Expense account of the product of PO line if any.
            #~ :param browse_record order_line: Purchase order line browse record
            #~ :return: Value for fields of invoice lines.
            #~ :rtype: dict
            #~ """
            #~ return {
            #~ 'name': order_line.name,
            #~ 'account_id': account_id,
            #~ 'price_unit': order_line.price_unit or 0.0,
            #~ 'quantity': order_line.product_qty,
            #~ 'product_id': order_line.product_id.id or False,
            #~ 'uos_id': order_line.product_uom.id or False,
            #~ 'invoice_line_tax_id': [(6, 0, [x.id for x in order_line.taxes_id])],
            #~ 'account_analytic_id': order_line.account_analytic_id.id or False,
            #~ 'purchase_line_id': order_line.id,
                 #~ }

    #~ def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        #~ """Prepare the dict of values to create the new invoice for a
           #~ purchase order. This method may be overridden to implement custom
           #~ invoice generation (making sure to call super() to establish
           #~ a clean extension chain).

           #~ :param browse_record order: purchase.order record to invoice
           #~ :param list(int) line_ids: list of invoice line IDs that must be
                                      #~ attached to the invoice
           #~ :return: dict of value to create() the invoice
        #~ """
        #~ journal_ids = self.pool['account.journal'].search(
                            #~ cr, uid, [('type', '=', 'purchase'),
                                      #~ ('company_id', '=', order.company_id.id)],
                            #~ limit=1)
        #~ if not journal_ids:
            #~ raise osv.except_osv(
                #~ _('Error!'),
                #~ _('Define purchase journal for this company: "%s" (id:%d).') % \
                    #~ (order.company_id.name, order.company_id.id))
        #~ return {
            #~ 'name': order.partner_ref or order.name,
            #~ 'reference': order.partner_ref or order.name,
            #~ 'account_id': order.partner_id.property_account_payable.id,
            #~ 'type': 'in_invoice',
            #~ 'request_id':order.requisition_id.id,
            #~ 'lead_id':order.lead_id.id,
            #~ 'partner_id': order.partner_id.id,
            #~ 'currency_id': order.currency_id.id,
            #~ 'journal_id': len(journal_ids) and journal_ids[0] or False,
            #~ 'invoice_line': [(6, 0, line_ids)],
            #~ 'origin': order.name,
            #~ 'fiscal_position': order.fiscal_position.id or False,
            #~ 'payment_term': order.payment_term_id.id or False,
            #~ 'company_id': order.company_id.id,
        #~ }


    #~ def action_invoice_create(self, cr, uid, ids, context=None):
        #~ """Generates invoice for given ids of purchase orders and links that invoice ID to purchase order.
        #~ :param ids: list of ids of purchase orders.
        #~ :return: ID of created invoice.
        #~ :rtype: int
        #~ """
        #~ context = dict(context or {})

        #~ inv_obj = self.pool.get('account.invoice')
        #~ inv_line_obj = self.pool.get('account.invoice.line')

        #~ res = False
        #~ uid_company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        #~ for order in self.browse(cr, uid, ids, context=context):
            #~ context.pop('force_company', None)
            #~ if order.company_id.id != uid_company_id:
                #~ #if the company of the document is different than the current user company, force the company in the context
                #~ #then re-do a browse to read the property fields for the good company.
                #~ context['force_company'] = order.company_id.id
                #~ order = self.browse(cr, uid, order.id, context=context)

            #~ # generate invoice line correspond to PO line and link that to created invoice (inv_id) and PO line
            #~ inv_lines = []
            #~ for po_line in order.order_line:
                #~ if po_line.state == 'cancel':
                    #~ continue
                #~ acc_id = self._choose_account_from_po_line(cr, uid, po_line, context=context)
                #~ inv_line_data = self._prepare_inv_line(cr, uid, ids, acc_id, po_line, context=context)
                #~ inv_line_id = inv_line_obj.create(cr, uid, inv_line_data, context=context)
                #~ inv_lines.append(inv_line_id)
                #~ po_line.write({'invoice_lines': [(4, inv_line_id)]})

            #~ # get invoice data and create invoice
            #~ inv_data = self._prepare_invoice(cr, uid, order, inv_lines, context=context)
            #~ inv_id = inv_obj.create(cr, uid, inv_data, context=context)

            #~ # compute the invoice
            #~ inv_obj.button_compute(cr, uid, [inv_id], context=context, set_total=True)

            #~ # Link this new invoice to related purchase order
            #~ order.write({'invoice_ids': [(4, inv_id)]})
            #~ res = inv_id
        #~ return res

    def load_currency(self, cr, uid, ids, context=None):
        copy_of_cost=[]
        obj = self.browse(cr, uid, ids)
        self.write(cr, uid, ids, {'currency_cost_id':obj.currency_id.id,'exchange_rate':obj.currency_id.rate_convert})
        cr.execute("SELECT id FROM purchase_costing WHERE active='true'")
        line_list = [i[0] for i in cr.fetchall()]
        line = [li for li in obj.costing_line]
        for cost in line_list:
            if not line:
                vals = {'purchase_costing_id':obj.id,'costing_id':cost}
                cost_cr = self.pool.get('purchase.costing.line').create(cr, uid, vals, context=context)
                copy_of_cost.append(cost_cr)
            else:
                for copy1 in copy_of_cost:
                    self.pool.get('purchase.costing.line').write(cr, uid, copy1, {'purchase_costing_id':line.id,'costing_id':line.costing_id.id})
        for product_line in obj.order_line:
            vals = {'purchase_product_id':obj.id,
                    'purchase_line_id':product_line.id,
                    'product_id':product_line.product_id.id,
                    'item_no':product_line.item_no,
                    'order_code':product_line.order_code,
                    'color':product_line.color,
                    'product_qty':product_line.product_qty,
                    'part_no':product_line.part_no,
                    'make_no':product_line.make_no,
                    'ot_unit_price':product_line.price_unit,
                    'ot_total_price':product_line.price_subtotal,
                    }
            self.pool.get('purchase.product.line').create(cr, uid, vals, context=context)
        return self.write(cr, uid, ids, {'cost_status':'progress'})


    def calculate_conversion(self, cr, uid, ids, context=None):
        total = []
        freight_total = []
        purchase_id = self.browse(cr, uid, ids)
        if purchase_id.amount_total <> 0.00:
            if purchase_id.state <> 'done':
                total += [prod_line.ot_total_price for prod_line in purchase_id.product_line]
                freight_total += [prod_line.freight_price for prod_line in purchase_id.product_line]
                fr_sr = self.pool.get('purchase.costing').search(cr, uid, [('name', '=', 'Freight')], context=context)
                fr = self.pool.get('purchase.costing.line').search(cr, uid, [('purchase_costing_id', '=', purchase_id.id),('costing_id', '=', fr_sr[0])], context=context)
                self.pool.get('purchase.costing.line').write(cr, uid, fr[0], {'amount':sum(freight_total)}, context=context)
                duty_amt = [cost_line.amount for cost_line in purchase_id.costing_line if cost_line.duty_applicable is True]
                duty = (sum(duty_amt) + sum(total)) * purchase_id.duty_id.amount
                cnf_amt = [cost_line.amount for cost_line in purchase_id.costing_line]
                cnf = sum(cnf_amt) + duty + sum(total)
                cost = cnf / sum(total)
                self.write(cr, uid, ids, {'duty_amount':duty, 'cnf_amount':cnf, 'cost_amount':cost})
        else:
            raise osv.except_osv(_('Error!'), _("You can not Calculating this process. Only for confirm. Because Product price is Zero"))
        return True
        #~
    #~ def calculate_conversion(self, cr, uid, ids, context=None):
        #~ total = []
        #~ purchase_id = self.browse(cr, uid, ids)
        #~ if purchase_id.state == 'draft':
            #~ total += [prod_line.ot_total_price for prod_line in purchase_id.product_line]
            #~ duty_amt = [cost_line.amount for cost_line in purchase_id.costing_line if cost_line.duty_applicable is True]
            #~ duty = (sum(duty_amt) + sum(total)) * purchase_id.duty_id.amount
            #~ cnf_amt = [cost_line.amount for cost_line in purchase_id.costing_line]
            #~ cnf = sum(cnf_amt) + duty + sum(total)
            #~ cost = cnf / sum(total)
            #~ self.write(cr, uid, ids, {'duty_amount':duty, 'cnf_amount':cnf, 'cost_amount':cost})
        #~ else:
            #~ raise osv.except_osv(_('Error!'), _("First Give Product Price For Purchase Line Item. After Calculating This Process"))
        #~ return True

    def cal_confirm(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'cost_status':'convertion'})



    def draft(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('purchase.product.line')
        cost_obj = self.pool.get('purchase.costing.line')
        obj_br = self.browse(cr, uid, ids)
        prod = [prod_line.id for prod_line in obj_br.product_line]
        cost = [cost_line.id for cost_line in obj_br.costing_line]
        prod_obj.unlink(cr, uid, prod, context=context)
        #~ cost_obj.unlink(cr, uid, cost, context=context)
        self.write(cr, uid, ids, {'cnf_amount': 0.00, 'duty_amount': 0.00, 'cost_amount':0.00})
        return self.write(cr, uid, ids, {'cost_status':'draft'})

    def gen_process(self, cr, uid, ids, context=None):
        purchase_id = self.browse(cr, uid, ids)
        for prod_line in purchase_id.product_line:
            ot_tot_price = prod_line.ot_unit_price * prod_line.product_qty
            aed_unit = prod_line.ot_unit_price * purchase_id.cost_amount *purchase_id.exchange_rate
            aed_total = aed_unit * prod_line.product_qty
            self.pool.get('purchase.product.line').write(cr, uid, prod_line.id, {'ot_total_price':ot_tot_price,'unit_price':aed_unit, 'total_price':aed_total}),
            margin = (aed_unit * purchase_id.margin_id.amount) + aed_unit
            margin_total = margin * prod_line.product_qty
            self.pool.get('purchase.product.line').write(cr, uid, prod_line.id, {'margin':round(margin,2), 'margin_price':margin_total}),
        return True


    def _prepare_history_product_line(self, cr, uid, margin, prod, prod_line, context=None):
        print'FFFFFFFFFFFFFFFFFFFFFFFF',prod_line
        res = {
              'history_product_id':prod,
              'product_id':prod_line.product_id.id,
              'product_qty':prod_line.product_qty,
              'ot_unit_price':prod_line.ot_unit_price,
              'part_no':prod_line.part_no,
              'make_no':prod_line.make_no,
              'ot_total_price':prod_line.ot_total_price,
              'unit_price':prod_line.unit_price,
              'total_price':prod_line.total_price,
              'margin_id':margin,
              'margin':prod_line.margin,
              'margin_price':prod_line.margin_price,
              'item_no':prod_line.item_no,

              }
        return res

    def done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        vals = {
            'purchase_cost_history_id':obj.id,
            'offer':'OFFER ' + str(int(obj.offer)),
            'currency_cost_id':obj.currency_cost_id.id,
            'exchange_rate':obj.exchange_rate,
            'cnf_amount':obj.cnf_amount,
            'duty_amount':obj.duty_amount,
            'cost_amount':obj.cost_amount,
            'duty_id':obj.duty_id.id,
            'margin_id':obj.margin_id.id,

               }
        prod = self.pool.get('cost.history.line').create(cr, uid, vals, context=context)
        for prod_line in obj.product_line:
            prod_vals = self._prepare_history_product_line(cr, uid, obj.margin_id.id,  prod, prod_line, context=context)
            self.pool.get('history.product.line').create(cr, uid, prod_vals, context=context)
            so_vals = {'so_id':obj.requisition_id.id, 'order_code':prod_line.order_code, 'purchase_id':obj.id, 'partner_id':obj.partner_id.id, 'offer':'OFFER ' + str(int(obj.offer)), 'ot_unit_price':prod_line.ot_unit_price, 'purchase_line_id':prod_line.purchase_line_id.id}
            pr_sr = self.pool.get('request.so.line').search(cr, uid, [('product_id', '=', prod_line.product_id.id), ('purchase_id', '=', obj.id)], context=context)
            old_pr = [sale.id for sale in self.pool.get('request.so.line').browse(cr, uid, pr_sr) if sale.unit_price == prod_line.unit_price]
            self.pool.get('request.so.line').unlink(cr, uid, old_pr, context=context)
            call_so = self.pool.get('request.so.line').create(cr, uid, so_vals, context=context)
            self.pool.get('request.so.line').write(cr, uid, [call_so], self._prepare_history_product_line(cr, uid, obj.margin_id.id, prod, prod_line, context=context), context=context)
        for cost_line in obj.costing_line:
            cost_vals = {
                     'history_costing_id':prod,
                     'costing_id':cost_line.costing_id.id,
                     'amount':cost_line.amount,
                     'duty_applicable':cost_line.duty_applicable,

                        }
            self.pool.get('history.costing.line').create(cr, uid, cost_vals, context=context)
        obj.offer += 1
        return self.write(cr, uid, ids, {'cost_status':'done'})

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order_inherit, self).wkf_confirm_order(cr, uid, ids, context=context)
        obj = self.browse(cr, uid, ids)
        val = self.pool.get('ir.sequence').get(cr, uid, 'purchase.confirm', context=context) or '/'
        #~ if obj.requisition_id.id:
        sale_id=self.pool.get('sale.order').search(cr,uid,[('request_id','=',obj.requisition_id.id),('state', 'not in', ('draft','send'))])
        val1=""
        user_obj = self.pool.get('res.users')
        company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
        if not obj.is_merged_po:
            if obj.requisition_id.id:
                if sale_id and company_id != 4:
                    sale_rec=self.pool.get('sale.order').browse(cr,uid,sale_id[0])
                    val1= val 
                elif sale_id  and company_id == 4:
                    sale_rec=self.pool.get('sale.order').browse(cr,uid,sale_id[0])
                    val1= val        
                else:
                    raise osv.except_osv(_('Invalid Action!'), _('Sale quote is not confirmed order'))             
            else:
                val1= val 
        else:
            if company_id != 4:
                val1= val 
            elif company_id == 4:
                val1= val        
            else:
                raise osv.except_osv(_('Invalid Action!'), _('Sale quote is not confirmed order'))                      
        self.write(cr, uid, ids, {'name':val1},context=context)
        return res

purchase_order_inherit()

class history_order_line(osv.osv):
    _name = 'history.order.line'
    _columns = {
            'purchase_history_id':fields.many2one('purchase.order', 'History', readonly=True),
            'product_id': fields.many2one('product.product', 'Product'),
            'name': fields.char('Description', size=64),
            'uom_id': fields.many2one('product.uom', 'Unit of Measure'),
            'product_qty': fields.char('Quantity'),
            'part_no': fields.char('Part No', size=64),
            'make_no': fields.char('Make', size=64),
            'item_no':fields.char('Item No'),
              }
history_order_line()

class purchase_order_line_inherit(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {

            'part_no':fields.char('Part No', size=64),
            'make_no':fields.char('Make', size=64),
            'color':fields.boolean('Color'),
            'request_id':fields.many2one('purchase.requisition', 'Call for bid'),
            'order_code':fields.char('Order Code', size=64),
            'item_no':fields.char('Item No'),
               }

    def onchange_product_uom(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        """
        onchange handler of product_uom.
        """
        if context is None:
            context = {}
        if not uom_id:
            return {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        context = dict(context, purchase_uom_check=True)
        return self.onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state, context=context)

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft', context=None):
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}
        res = {'value': {'price_unit': price_unit or 0.0, 'name': name or '', 'product_uom' : uom_id or False}}
        if not product_id:
            return res

        product_product = self.pool.get('product.product')
        product_uom = self.pool.get('product.uom')
        res_partner = self.pool.get('res.partner')
        product_pricelist = self.pool.get('product.pricelist')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        # - check for the presence of partner_id and pricelist_id
        #if not partner_id:
        #    raise osv.except_osv(_('No Partner!'), _('Select a partner in purchase order to choose a product.'))
        #if not pricelist_id:
        #    raise osv.except_osv(_('No Pricelist !'), _('Select a price list in the purchase order form before choosing a product.'))

        # - determine name and notes based on product in partner lang.
        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)
        #call name_get() with partner in the context to eventually match name and description in the seller_ids field
        if not name or not uom_id:
            # The 'or not uom_id' part of the above condition can be removed in master. See commit message of the rev. introducing this line.
            dummy = product_product.name_get(cr, uid, product_id, context=context_partner)[0]
            if product.description_purchase:
                name = product.description_purchase
            res['value'].update({'name': name})

        # - set a domain on product_uom
        res['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}

        # - check that uom and product uom belong to the same category
        product_uom_po_id = product.uom_po_id.id
        if not uom_id:
            uom_id = product_uom_po_id

        if product.uom_id.category_id.id != product_uom.browse(cr, uid, uom_id, context=context).category_id.id:
            if context.get('purchase_uom_check') and self._check_product_uom_group(cr, uid, context=context):
                res['warning'] = {'title': _('Warning!'), 'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure.')}
            uom_id = product_uom_po_id

        res['value'].update({'product_uom': uom_id})

        # - determine product_qty and date_planned based on seller info
        if not date_order:
            date_order = fields.datetime.now()


        supplierinfo = False
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Unit of Measure')
        for supplier in product.seller_ids:
            if partner_id and (supplier.name.id == partner_id):
                supplierinfo = supplier
                if supplierinfo.product_uom.id != uom_id:
                    res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier only sells this product by %s') % supplierinfo.product_uom.name }
                min_qty = product_uom._compute_qty(cr, uid, supplierinfo.product_uom.id, supplierinfo.min_qty, to_uom_id=uom_id)
                if float_compare(min_qty , qty, precision_digits=precision) == 1: # If the supplier quantity is greater than entered from user, set minimal.
                    if qty:
                        res['warning'] = {'title': _('Warning!'), 'message': _('The selected supplier has a minimal quantity set to %s %s, you should not purchase less.') % (supplierinfo.min_qty, supplierinfo.product_uom.name)}
                    qty = min_qty
        dt = self._get_date_planned(cr, uid, supplierinfo, date_order, context=context).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        qty = qty or 1.0
        res['value'].update({'date_planned': date_planned or dt})
        if qty:
            res['value'].update({'product_qty': qty})

        price = price_unit
        if price_unit is False or price_unit is None:
            # - determine price_unit and taxes_id
            if pricelist_id:
                date_order_str = datetime.strptime(date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                price = product_pricelist.price_get(cr, uid, [pricelist_id],
                        product.id, qty or 1.0, partner_id or False, {'uom': uom_id, 'date': date_order_str})[pricelist_id]
            else:
                price = product.standard_price

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        res['value'].update({'price_unit': price, 'taxes_id': taxes_ids})
        res['value'].update({'part_no': product.part_no, 'make_no': product.make_no})

        return res

    product_id_change = onchange_product_id
    product_uom_change = onchange_product_uom

purchase_order_line_inherit()

class purchase_costing_line(osv.osv):
    _name = 'purchase.costing.line'
    _columns = {

             'purchase_costing_id': fields.many2one('purchase.order', 'Purchase'),
             'costing_id': fields.many2one('purchase.costing', 'Charges'),
             'amount': fields.float('Amount'),
             'duty_applicable': fields.boolean('Duty Applicable'),
             'item_no':fields.char('Item No'),
               }

purchase_costing_line()

class purchase_product_line(osv.osv):
    _name = 'purchase.product.line'
    _columns = {

             'purchase_product_id': fields.many2one('purchase.order', 'Purchase'),
             'purchase_line_id': fields.many2one('purchase.order.line', 'Purchase Line'),
             'product_id': fields.many2one('product.product', 'Product'),
             'product_qty': fields.float('Quantity'),
             'color': fields.boolean('Color'),
             'ot_unit_price': fields.float('Unit Price'),
             'part_no':fields.char('Part No', size=64),
             'make_no':fields.char('Make', size=64),
             'ot_total_price': fields.float('Total Price'),
             'unit_price': fields.float('AED Unit Price'),
             'total_price': fields.float('AED Total Price'),
             'margin': fields.float('Unit Sale Price'),
             'freight_price':fields.float('Freight Charges'),
             'margin_price': fields.float('Customer Price'),
             'order_code':fields.char('Order Code', size=64),
             'item_no':fields.char('Item No'),
               }


purchase_product_line()

class cost_history_line(osv.osv):
    _name = 'cost.history.line'
    _columns = {
             'purchase_cost_history_id': fields.many2one('purchase.order', 'Purchase'),
             'offer':fields.char('Offer', size=64, readonly=True),
             'currency_cost_id':fields.many2one('res.currency', 'Currency', readonly=True),
             'exchange_rate':fields.float('Exchange Rate', readonly=True),
             'cnf_amount': fields.float('CNF', readonly=True),
             'duty_amount':fields.float('Duty', readonly=True),
             'cost_amount': fields.float('Cost', digits_compute= dp.get_precision('Cost') ,readonly=True),
             'duty_id': fields.many2one('costing.duty', 'Duty', readonly=True),
             'margin_id': fields.many2one('costing.margin', 'Margin', readonly=True),
             'tab_costing_line':fields.one2many('history.costing.line', 'history_costing_id', 'Costing' ,readonly=True),
             'tab_product_line':fields.one2many('history.product.line', 'history_product_id', 'Product' ,readonly=True),

               }

cost_history_line()

class history_costing_line(osv.osv):
    _name = 'history.costing.line'
    _columns = {
             'history_costing_id': fields.many2one('cost.history.line', 'Cost History'),
             'costing_id': fields.many2one('purchase.costing', 'Charges'),
             'amount': fields.float('Amount'),
             'duty_applicable': fields.boolean('Duty Applicable'),
               }
history_costing_line()

class history_product_line(osv.osv):
    _name = 'history.product.line'
    _columns = {
            'history_product_id': fields.many2one('cost.history.line', 'Product History'),
            'product_id': fields.many2one('product.product', 'Product'),
            'product_qty': fields.float('Quantity'),
            'ot_unit_price': fields.float('Unit Price'),
            'part_no':fields.char('Part No', size=64),
            'make_no':fields.char('Make', size=64),
            'ot_total_price': fields.float('Total Price'),
            'unit_price': fields.float('AED Unit Price'),
            'total_price': fields.float('AED Total Price'),
            'margin_id': fields.many2one('costing.margin', 'Margin'),
            'margin': fields.float('Unit Sale Price'),
            'margin_price': fields.float('Customer Price'),
            'item_no':fields.integer('Item No'),

               }
history_product_line()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
           'request_id':fields.many2one('purchase.requisition', 'Call for bid')
              }
stock_picking()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = {
          'request_id':fields.many2one('purchase.requisition', 'Call for bid')
              }
account_invoice()
