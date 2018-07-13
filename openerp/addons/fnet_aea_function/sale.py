
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
from openerp import SUPERUSER_ID
from openerp.tools.translate import _


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns={
    
    'com_type': fields.selection([('tn', 'TN'),('ka', 'KA'),('kl', 'KL'),('ob', 'OB'),('os', 'OS'),('ap', 'AP'),('tl', 'TL'),], 'Company'),
    }
    
class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True),
        'del_method': fields.selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Type', required=True),
        'tpt_name':fields.many2one('res.partner', 'TPT.Co.Name'),
        }
        
    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, context=None):
        result = {}
        if prod_categ_id:
            term = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            result['value'] = {'payment_term':term.payment_term.id,}
            return result
    
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_id = self.pool['account.invoice'].default_get(cr, uid, ['journal_id'], context=context)['journal_id']
        if not journal_id:
            raise osv.except_osv(_('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_invoice_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_id,
            'category_id': order.prod_categ_id.id,
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_invoice_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'user_id': order.user_id and order.user_id.id or False,
            'section_id' : order.section_id.id,
            'del_method' : order.del_method,
            'tpt_name' : order.tpt_name.id,
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals
        
    def action_button_confirm(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        if not context:
            context = {}
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'order_confirm')
        if context.get('send_email'):
            self.force_quotation_send(cr, uid, ids, context=context)
        if (-obj.cust_credit)<obj.amount_total:
            y=0.0
            y=obj.amount_total-(obj.cust_credit)
            if obj.cust_credit <= 0:
                yy=obj.amount_total + obj.cust_credit
                raise osv.except_osv(_(' Warning!'),_("Since The Customer Doesn't  Have Sufficient \n  %s" %(str(obj.cust_credit)))  )
            raise osv.except_osv(_(' Warning!'),_('Total Amount Should Not Exceed Then Receivable Amount \n Exceded Amount is %s' %(str(y)))  )
        for line in obj.order_line:
            prod = self.pool.get('product.product').browse(cr, uid, line.product_id.id)
            val = prod.qty_available - line.product_uom_qty
            if val < 0.00 and prod.type != 'service':
                raise osv.except_osv(_('Product Warning!'),
                        _('"%s" Quantity is not available. Only "%s" is Available') % (prod.name_template,prod.qty_available))
         
        return True

    def onchange_del_method(self, cr, uid, ids, del_method, partner_id, context=None):
        if del_method:
            dis = self.pool.get('delivery.method').search(cr, uid, [('method_type','=', del_method)], context=context)
            if dis:
                dis_var = self.pool.get('delivery.method').browse(cr, uid,dis[0])
                return {'value': {'tpt_name':dis_var.partner_id.id or False}}
                
    def action_view_delivery(self, cr, uid, ids, context=None):
        result=super(sale_order, self).action_view_delivery(cr, uid, ids, context=context)
        pick_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            pick_ids += [picking.id for picking in so.picking_ids]        
        obj = self.browse(cr, uid, ids)[0]
        self.pool.get('stock.picking').write(cr, uid, pick_ids, {'date':obj.date_order}, context=context)
        return result                
    
sale_order()

class sale_order_line_inh(osv.osv):
    
    _inherit = 'sale.order.line'
    
    _columns = {
           'mrp_price':fields.float('MRP Price'),
               }
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        """Prepare the dict of values to create the new invoice line for a
           sales order line. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record line: sale.order.line record to invoice
           :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
           :return: dict of values to create() the invoice line
        """
        res = {}
        if not line.invoiced:
            if not account_id:
                if line.product_id:
                    account_id = line.product_id.property_account_income.id
                    if not account_id:
                        account_id = line.product_id.categ_id.property_account_income_categ.id
                    if not account_id:
                        raise osv.except_osv(_('Error!'),
                                _('Please define income account for this product: "%s" (id:%d).') % \
                                    (line.product_id.name, line.product_id.id,))
                else:
                    prop = self.pool.get('ir.property').get(cr, uid,
                            'property_account_income_categ', 'product.category',
                            context=context)
                    account_id = prop and prop.id or False
            uosqty = self._get_line_qty(cr, uid, line, context=context)
            uos_id = self._get_line_uom(cr, uid, line, context=context)
            pu = 0.0
            if uosqty:
                pu = round(line.price_unit * line.product_uom_qty / uosqty,
                        self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price'))
            fpos = line.order_id.fiscal_position or False
            account_id = self.pool.get('account.fiscal.position').map_account(cr, uid, fpos, account_id)
            if not account_id:
                raise osv.except_osv(_('Error!'),
                            _('There is no Fiscal Position defined or Income category account defined for default properties of Product categories.'))
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'mrp_price': line.mrp_price,
                'uos_id': uos_id,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }

        return res           
    
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,discounts=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang', False)
        if not partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = False
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        partner = partner_obj.browse(cr, uid, partner_id)
        lang = partner.lang
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)

        if uid == SUPERUSER_ID and context.get('company_id'):
            taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == context['company_id'])
        else:
            taxes = product_obj.taxes_id
        part_obj=self.pool.get('res.partner').browse(cr, uid,partner_id)
        company_id=self.pool.get('res.company')._company_default_get(cr,uid,'sale.order.line')
        com_obj=self.pool.get('res.company').browse(cr, uid,company_id)
        news=[]
        if part_obj.state_id.code and com_obj.state_id.code  != False:
            if  part_obj.state_id.code != com_obj.state_id.code:
                for i in taxes:
                    if i.ref_code == '3':
                        news.append(i.ids[0])
            elif part_obj.state_id.code == com_obj.state_id.code:   
                for i in taxes:
                    if i.ref_code != '3':
                        news.append(i.ids[0]) 
            tax_obj=self.pool.get('account.tax').browse(cr, uid,news)    
            taxes=tax_obj
        else:
            taxes=taxes        
        
        result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            ctx = dict(
                context,
                uom=uom or result.get('product_uom'),
                date=date_order,
            )
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, ctx)[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                price = self.pool['account.tax']._fix_tax_included_price(cr, uid, price, taxes, result['tax_id'])
                result.update({'price_unit': price})
                result.update({'mrp_price': product_obj.mrp_price})
                result.update({'discounts': product_obj.discount_price})
                if context.get('uom_qty_change', False):
                    values = {'price_unit': price}
                    if result.get('product_uos_qty'):
                        values['product_uos_qty'] = result['product_uos_qty']
                    return {'value': values, 'domain': {}, 'warning': False}
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        if result:
            result.update({'gross_amount':result['product_uos_qty'] * result['price_unit']})
            result.update({'disc_price_unit': result['price_unit'] - result['discounts']})
            result.update({'product_discount': result['product_uos_qty'] * result['discounts']})
        return {'value': result, 'domain': domain, 'warning': warning}
   
sale_order_line_inh()



