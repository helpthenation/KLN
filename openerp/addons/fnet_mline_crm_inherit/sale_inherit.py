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
from openerp import api, tools
from openerp import SUPERUSER_ID

class sale_order_inherit(osv.osv):
    _inherit = 'sale.order'
    _columns = {
             'lead_id': fields.many2one('crm.lead', 'Enquiry Ref', readonly=True), 
             'request_id': fields.many2one('purchase.requisition', 'Call for Bid', readonly=True),
             'offer_id': fields.many2one('quote.offer', 'Offer'),
             'subject':fields.html('Subject'),
             'contact_name':fields.char('Contact Name', size=64),
             'function': fields.char('Function', size=64),
             'title_id':fields.many2one('res.partner.title', 'Title'),
             'remark':fields.html('Remarks'),
             'note_document':fields.html('Remarks'),
             'signature':fields.html('Signature'),
             'covering_remark':fields.html('Covering Remarks'),
             'cancel_remark':fields.text('Cancel Reason', states={'cancel': [('required', True)]}),
             #~ 'delivery_time': fields.char('Delivery', size=64),
             'delivery_period':fields.char('Delivery Period'),
             #~ 'job_id':fields.char('Job ID',readonly=True),
             'lpo_no':fields.char('L.P.O No'),
             'validity':fields.integer('Validity'),
             'validity_new':fields.char('Validity'),
             'parent_so':fields.many2one('sale.order','Sale Quotation'),
             
              }
              
    #~ _defaults={
             #~ 'job_id': lambda obj, cr, uid, context: '/',
     #~ }
    #~ 
    #~ def create(self, cr, uid, vals, context=None):
        #~ if context is None:
            #~ context = {}
        #~ if vals.get('job_id', '/') == '/':
            #~ vals['job_id'] = self.pool.get('ir.sequence').get(cr, uid, 'job_id', context=context) or '/'
        #~ new_id = super(sale_order_inherit, self).create(cr, uid, vals, context=context)
        #~ return new_id
        
    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').next_by_code(
                cr, uid, 'sale.quotations') or '/'
        return super(sale_order_inherit, self).create(cr, uid, vals, context=context)

    #~ def action_wait(self, cr, uid, ids, context=None):
        #~ print'TESSSSSSSSSSSSSSSSSS'
        #~ if super(sale_order_inherit, self).action_wait(cr, uid, ids, context=context):
            #~ for sale in self.browse(cr, uid, ids, context=None):
                #~ quo = sale.name
                #~ self.write(cr, uid, [sale.id], {
                    #~ 'origin': quo,
                    #~ 'name': self.pool.get('ir.sequence').next_by_code(
                        #~ cr, uid, 'sale.order')
                #~ })
        #~ return True    
        
    def button_confirm_quote(self,cr,uid,ids,context=None):
        b=self.pool.get('sale.order').browse(cr,uid,ids)
        c=b.lead_id
        if c:
            lead_obj=self.pool.get('crm.lead').browse(cr,uid,c.id)
            d=self.pool.get('crm.case.stage').search(cr, uid, [('sequence', '=',3)], context=None)
            if d:
             lead_obj.write({'stage_id':d[0]})
        self.write(cr, uid, ids, {'state': 'sent'}) 
        
    def button_reset_to_draft(self,cr,uid,ids,context=None):
        self.write(cr, uid, ids, {'state': 'draft'}) 
        
    def action_button_confirm(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        #~ job_id= self.pool.get('ir.sequence').get(cr, uid, 'job_id', context=context) or '/'
        #~ self.write(cr, uid, ids, {'job_id': job_id})
        for sale in self.browse(cr, uid, ids, context=None):
                quo = sale.name
                self.write(cr, uid, [sale.id], {
                    'origin': quo,
                    'name': self.pool.get('ir.sequence').next_by_code(
                        cr, uid, 'sale.order')
                })
        new_id = super(sale_order_inherit, self).action_button_confirm(cr, uid, ids, context=context)
        b=self.pool.get('sale.order').browse(cr,uid,ids)
        c=b.lead_id
        if c:
            lead_obj=self.pool.get('crm.lead').browse(cr,uid,c.id)
            d=self.pool.get('crm.case.stage').search(cr, uid, [('sequence', '=',4)], context=None)
            if d:
             lead_obj.write({'stage_id':d[0]})        
        return True
    
    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        if states is None:
            states = ['confirmed', 'done', 'exception']
        res = False
        sale_order=self.browse(cr,uid,ids)
        invoices = {}
        invoice_ids = []
        invoice = self.pool.get('account.invoice')
        obj_sale_order_line = self.pool.get('sale.order.line')
        partner_currency = {}
        # If date was specified, use it as date invoiced, usefull when invoices are generated this month and put the
        # last day of the last month as invoice date
        if date_invoice:
            context = dict(context or {}, date_invoice=date_invoice)
        for o in self.browse(cr, uid, ids, context=context):
            currency_id = o.pricelist_id.currency_id.id
            if (o.partner_id.id in partner_currency) and (partner_currency[o.partner_id.id] <> currency_id):
                raise osv.except_osv(
                    _('Error!'),
                    _('You cannot group sales having different currencies for the same partner.'))

            partner_currency[o.partner_id.id] = currency_id
            lines = []
            for line in o.order_line:
                if line.invoiced:
                    continue
                elif (line.state in states):
                    lines.append(line.id)
            created_lines = obj_sale_order_line.invoice_line_create(cr, uid, lines)
            if created_lines:
                invoices.setdefault(o.partner_invoice_id.id or o.partner_id.id, []).append((o, created_lines))
        if not invoices:
            for o in self.browse(cr, uid, ids, context=context):
                for i in o.invoice_ids:
                    if i.state == 'draft':
                        return i.id
        for val in invoices.values():
            if grouped:
                res = self._make_invoice(cr, uid, val[0][0], reduce(lambda x, y: x + y, [l for o, l in val], []), context=context)
                invoice_ref = ''
                origin_ref = ''
                for o, l in val:
                    invoice_ref += (o.client_order_ref or o.name) + '|'
                    origin_ref += (o.origin or o.name) + '|'
                    self.write(cr, uid, [o.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (o.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [o.id], context=context)
                #remove last '|' in invoice_ref
                if len(invoice_ref) >= 1:
                    invoice_ref = invoice_ref[:-1]
                if len(origin_ref) >= 1:
                    origin_ref = origin_ref[:-1]
                invoice.write(cr, uid, [res], {'origin': origin_ref, 'name': invoice_ref})
            else:
                for order, il in val:
                    res = self._make_invoice(cr, uid, order, il, context=context)
                    invoice_ids.append(res)
                    self.write(cr, uid, [order.id], {'state': 'progress'})
                    cr.execute('insert into sale_order_invoice_rel (order_id,invoice_id) values (%s,%s)', (order.id, res))
                    self.invalidate_cache(cr, uid, ['invoice_ids'], [order.id], context=context)
                    invoice.write(cr, uid, [res], {'lpo_no':sale_order.lpo_no})
        return res
        
    def action_ship_create(self, cr, uid, ids, context=None):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """

        context = dict(context or {})
        context['lang'] = self.pool['res.users'].browse(cr, uid, uid).lang
        procurement_obj = self.pool.get('procurement.order')
        sale_line_obj = self.pool.get('sale.order.line')
        for order in self.browse(cr, uid, ids, context=context):
            proc_ids = []
            vals = self._prepare_procurement_group(cr, uid, order, context=context)
            if not order.procurement_group_id:
                group_id = self.pool.get("procurement.group").create(cr, uid, vals, context=context)
                order.write({'procurement_group_id': group_id})

            for line in order.order_line:
                if line.state == 'cancel':
                    continue
                #Try to fix exception procurement (possible when after a shipping exception the user choose to recreate)
                if line.procurement_ids:
                    #first check them to see if they are in exception or not (one of the related moves is cancelled)
                    procurement_obj.check(cr, uid, [x.id for x in line.procurement_ids if x.state not in ['cancel', 'done']])
                    line.refresh()
                    #run again procurement that are in exception in order to trigger another move
                    except_proc_ids = [x.id for x in line.procurement_ids if x.state in ('exception', 'cancel')]
                    procurement_obj.reset_to_confirmed(cr, uid, except_proc_ids, context=context)
                    proc_ids += except_proc_ids
                elif sale_line_obj.need_procurement(cr, uid, [line.id], context=context):
                    if (line.state == 'done') or not line.product_id:
                        continue
                    vals = self._prepare_order_line_procurement(cr, uid, order, line, group_id=order.procurement_group_id.id, context=context)
                    ctx = context.copy()
                    ctx['procurement_autorun_defer'] = True
                    proc_id = procurement_obj.create(cr, uid, vals, context=ctx)
                    proc_ids.append(proc_id)
            #Confirm procurement order such that rules will be applied on it
            #note that the workflow normally ensure proc_ids isn't an empty list
            procurement_obj.run(cr, uid, proc_ids, context=context)

            #if shipping was in exception and the user choose to recreate the delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
            if order.picking_ids:
                #~ print'DDDDDDDDDDDDDDDDDD',order.picking_ids.move_lines
                order.picking_ids.write({'lpo_no':order.lpo_no})            
                
        return True        
sale_order_inherit()

class sale_order_line_inherit(osv.osv):
    _inherit = 'sale.order.line'
    _columns = { 
              'item_no':fields.char('Item No'),
              'part_no': fields.char('Part No', size=64),
              'make_no': fields.char('Make', size=64),
              'offer_id': fields.many2one('quote.offer', 'Offer'),
              'sale_call_id': fields.many2one('request.so.line', 'Call for Sale'),
              'purchase_id': fields.many2one('purchase.order', 'Purchase Quote', readonly=True),   
              'order_code':fields.char('Order Code', size=64),  
              'uom':fields.char('UOM'),
              }
              
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
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
        result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes, context=context)

        if not flag:
            #~ result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] =product_obj.description_sale
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
        return {'value': result, 'domain': domain, 'warning': warning}

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
            #~ print'LINEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',line.uom
            res = {
                'name': line.name,
                'sequence': line.sequence,
                'origin': line.order_id.name,
                'account_id': account_id,
                'price_unit': pu,
                'quantity': uosqty,
                'discount': line.discount,
                'uos_id': uos_id,
                'item_no':line.item_no,
                'uom':line.uom,
                'product_id': line.product_id.id or False,
                'invoice_line_tax_id': [(6, 0, [x.id for x in line.tax_id])],
                'account_analytic_id': line.order_id.project_id and line.order_id.project_id.id or False,
            }
        #~ cr.execute("""select sol.uom as uom
                                #~ FROM stock_move sm
                                #~ LEFT JOIN procurement_order po
                                #~ ON sm.procurement_id = po.id 
                                #~ LEFT JOIN sale_order_line sol
                                #~ ON po.sale_line_id = sol.id
                                #~ where  sol.id = %d"""%(line.id))
        #~ val=cr.dictfetchone()          
        #~ print'OOOOOOOOOOOOOOOOOOOOOOOOO',val        
        #~ res.update({'uom':val['uom']})
        #~ print'RESSSSSSSSSSSSSSSSSSSSSSSSSSSS',res
        return res        
sale_order_line_inherit()

class mail_compose_message(osv.TransientModel):
    _inherit = 'mail.compose.message'
    
    _columns = {
        'mail_cc': fields.many2many('res.partner','mail_compose_message_res_partner_cc_rel','wizard_id', 'partner_id', 'CC'),
        'mail_bcc': fields.many2many('res.partner','mail_compose_message_res_partner_bcc_rel','wizard_id', 'partner_id', 'BCC'),
    }
    
    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        """Generate the values that will be used by send_mail to create mail_messages
        or mail_mails. """
        results = dict.fromkeys(res_ids, False)
        rendered_values, default_recipients = {}, {}
        mass_mail_mode = wizard.composition_mode == 'mass_mail'
        # render all template-based value at once
        if mass_mail_mode and wizard.model:
            rendered_values = self.render_message_batch(cr, uid, wizard, res_ids, context=context)
        # compute alias-based reply-to in batch
        reply_to_value = dict.fromkeys(res_ids, None)
        if mass_mail_mode and not wizard.no_auto_thread:
            reply_to_value = self.pool['mail.thread'].message_get_reply_to(cr, uid, res_ids, default=wizard.email_from, context=dict(context, thread_model=wizard.model))
        for res_id in res_ids:
            # static wizard (mail.message) values
            mail_values = {
                'subject': wizard.subject,
                'body': wizard.body or '',
                'parent_id': wizard.parent_id and wizard.parent_id.id,
                'partner_ids': [partner.id for partner in wizard.partner_ids],
                'mail_cc': [cc.id for cc in wizard.mail_cc],
                'mail_bcc': [bcc.id for bcc in wizard.mail_bcc],
                'attachment_ids': [attach.id for attach in wizard.attachment_ids],
                'author_id': wizard.author_id.id,
                'email_from': wizard.email_from,
                'record_name': wizard.record_name,
                'no_auto_thread': wizard.no_auto_thread,
            }
            # mass mailing: rendering override wizard static values
            if mass_mail_mode and wizard.model:
                # always keep a copy, reset record name (avoid browsing records)
                mail_values.update(notification=True, model=wizard.model, res_id=res_id, record_name=False)
                # auto deletion of mail_mail
                if 'mail_auto_delete' in context:
                    mail_values['auto_delete'] = context.get('mail_auto_delete')
                # rendered values using template
                email_dict = rendered_values[res_id]
                mail_values['partner_ids'] += email_dict.pop('partner_ids', [])
                mail_values['mail_cc'] += email_dict.pop('mail_cc', [])
                mail_values['mail_bcc'] += email_dict.pop('mail_bcc', [])
                mail_values.update(email_dict)
                if not wizard.no_auto_thread:
                    mail_values.pop('reply_to')
                    if reply_to_value.get(res_id):
                        mail_values['reply_to'] = reply_to_value[res_id]
                if wizard.no_auto_thread and not mail_values.get('reply_to'):
                    mail_values['reply_to'] = mail_values['email_from']
                # mail_mail values: body -> body_html, partner_ids -> recipient_ids
                mail_values['body_html'] = mail_values.get('body', '')
                mail_values['recipient_ids'] = [(4, id) for id in mail_values.pop('partner_ids', [])]

                # process attachments: should not be encoded before being processed by message_post / mail_mail create
                mail_values['attachments'] = [(name, base64.b64decode(enc_cont)) for name, enc_cont in email_dict.pop('attachments', list())]
                attachment_ids = []
                for attach_id in mail_values.pop('attachment_ids'):
                    new_attach_id = self.pool.get('ir.attachment').copy(cr, uid, attach_id, {'res_model': self._name, 'res_id': wizard.id}, context=context)
                    attachment_ids.append(new_attach_id)
                mail_values['attachment_ids'] = self.pool['mail.thread']._message_preprocess_attachments(
                    cr, uid, mail_values.pop('attachments', []),
                    attachment_ids, 'mail.message', 0, context=context)
            results[res_id] = mail_values
        return results
        
class mail_mail(osv.osv):        
    _inherit = 'mail.mail'

    _columns = {
        'email_bcc': fields.char('Bcc', help='Blind carbon copy message recipients'),
    }
    
class mail_message(osv.osv):        
    _inherit = 'mail.message'

    _columns = {
        'mail_cc': fields.many2many('res.partner', string='CC'),
        'mail_bcc': fields.many2many('res.partner', string='Bcc'),

    }
    
class mail_thread(osv.AbstractModel):
    
    _inherit = 'mail.thread'
    
    
    @api.cr_uid_ids_context
    def message_post(self, cr, uid, thread_id, body='', subject=None, type='notification',
                     subtype=None, parent_id=False, attachments=None, context=None,
                     content_subtype='html', **kwargs):
        """ Post a new message in an existing thread, returning the new
            mail.message ID.

            :param int thread_id: thread ID to post into, or list with one ID;
                if False/0, mail.message model will also be set as False
            :param str body: body of the message, usually raw HTML that will
                be sanitized
            :param str type: see mail_message.type field
            :param str content_subtype:: if plaintext: convert body into html
            :param int parent_id: handle reply to a previous message by adding the
                parent partners to the message in case of private discussion
            :param tuple(str,str) attachments or list id: list of attachment tuples in the form
                ``(name,content)``, where content is NOT base64 encoded

            Extra keyword arguments will be used as default column values for the
            new mail.message record. Special cases:
                - attachment_ids: supposed not attached to any document; attach them
                    to the related document. Should only be set by Chatter.
            :return int: ID of newly created mail.message
        """
        if context is None:
            context = {}
        if attachments is None:
            attachments = {}
        mail_message = self.pool.get('mail.message')
        ir_attachment = self.pool.get('ir.attachment')
        assert (not thread_id) or \
                isinstance(thread_id, (int, long)) or \
                (isinstance(thread_id, (list, tuple)) and len(thread_id) == 1), \
                "Invalid thread_id; should be 0, False, an ID or a list with one ID"
        if isinstance(thread_id, (list, tuple)):
            thread_id = thread_id[0]

        # if we're processing a message directly coming from the gateway, the destination model was
        # set in the context.
        model = False
        if thread_id:
            model = context.get('thread_model', False) if self._name == 'mail.thread' else self._name
            if model and model != self._name and hasattr(self.pool[model], 'message_post'):
                del context['thread_model']
                return self.pool[model].message_post(cr, uid, thread_id, body=body, subject=subject, type=type, subtype=subtype, parent_id=parent_id, attachments=attachments, context=context, content_subtype=content_subtype, **kwargs)

        #0: Find the message's author, because we need it for private discussion
        author_id = kwargs.get('author_id')
        if author_id is None:  # keep False values
            author_id = self.pool.get('mail.message')._get_default_author(cr, uid, context=context)

        # 1: Handle content subtype: if plaintext, converto into HTML
        if content_subtype == 'plaintext':
            body = tools.plaintext2html(body)

        # 2: Private message: add recipients (recipients and author of parent message) - current author
        #   + legacy-code management (! we manage only 4 and 6 commands)
        partner_ids = set()
        kwargs_partner_ids = kwargs.pop('partner_ids', [])
        for partner_id in kwargs_partner_ids:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                partner_ids.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                partner_ids |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                partner_ids.add(partner_id)
            else:
                pass  # we do not manage anything else
        mail_cc = set()
        kwargs_mail_cc = kwargs.pop('mail_cc', [])
        for partner_id in kwargs_mail_cc:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                mail_cc.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                mail_cc |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                mail_cc.add(partner_id)
            else:
                pass 
                
        mail_bcc = set()
        kwargs_mail_bcc = kwargs.pop('mail_bcc', [])
        for partner_id in kwargs_mail_bcc:
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 4 and len(partner_id) == 2:
                mail_bcc.add(partner_id[1])
            if isinstance(partner_id, (list, tuple)) and partner_id[0] == 6 and len(partner_id) == 3:
                mail_bcc |= set(partner_id[2])
            elif isinstance(partner_id, (int, long)):
                mail_bcc.add(partner_id)
            else:
                pass 
                
        if parent_id and not model:
            parent_message = mail_message.browse(cr, uid, parent_id, context=context)
            private_followers = set([partner.id for partner in parent_message.partner_ids])
            if parent_message.author_id:
                private_followers.add(parent_message.author_id.id)
            private_followers -= set([author_id])
            partner_ids |= private_followers

        # 3. Attachments
        #   - HACK TDE FIXME: Chatter: attachments linked to the document (not done JS-side), load the message
        attachment_ids = self._message_preprocess_attachments(cr, uid, attachments, kwargs.pop('attachment_ids', []), model, thread_id, context)

        # 4: mail.message.subtype
        subtype_id = False
        if subtype:
            if '.' not in subtype:
                subtype = 'mail.%s' % subtype
            subtype_id = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, subtype)

        # automatically subscribe recipients if asked to
        if context.get('mail_post_autofollow') and thread_id and partner_ids:
            partner_to_subscribe = partner_ids
            if context.get('mail_post_autofollow_partner_ids'):
                partner_to_subscribe = filter(lambda item: item in context.get('mail_post_autofollow_partner_ids'), partner_ids)
            self.message_subscribe(cr, uid, [thread_id], list(partner_to_subscribe), context=context)

        # _mail_flat_thread: automatically set free messages to the first posted message
        if self._mail_flat_thread and model and not parent_id and thread_id:
            message_ids = mail_message.search(cr, uid, ['&', ('res_id', '=', thread_id), ('model', '=', model), ('type', '=', 'email')], context=context, order="id ASC", limit=1)
            if not message_ids:
                message_ids = message_ids = mail_message.search(cr, uid, ['&', ('res_id', '=', thread_id), ('model', '=', model)], context=context, order="id ASC", limit=1)
            parent_id = message_ids and message_ids[0] or False
        # we want to set a parent: force to set the parent_id to the oldest ancestor, to avoid having more than 1 level of thread
        elif parent_id:
            message_ids = mail_message.search(cr, SUPERUSER_ID, [('id', '=', parent_id), ('parent_id', '!=', False)], context=context)
            # avoid loops when finding ancestors
            processed_list = []
            if message_ids:
                message = mail_message.browse(cr, SUPERUSER_ID, message_ids[0], context=context)
                while (message.parent_id and message.parent_id.id not in processed_list):
                    processed_list.append(message.parent_id.id)
                    message = message.parent_id
                parent_id = message.id

        values = kwargs
        values.update({
            'author_id': author_id,
            'model': model,
            'res_id': model and thread_id or False,
            'body': body,
            'subject': subject or False,
            'type': type,
            'parent_id': parent_id,
            'attachment_ids': attachment_ids,
            'subtype_id': subtype_id,
            'partner_ids': [(4, pid) for pid in partner_ids],
            'mail_cc': [(4, pid) for pid in mail_cc],
            'mail_bcc': [(4, pid) for pid in mail_bcc],
        })
        
        # Avoid warnings about non-existing fields
        for x in ('from', 'to', 'cc'):
            values.pop(x, None)
        # Post the message
        msg_id = mail_message.create(cr, uid, values, context=context)

        # Post-process: subscribe author, update message_last_post
        if model and model != 'mail.thread' and thread_id and subtype_id:
            # done with SUPERUSER_ID, because on some models users can post only with read access, not necessarily write access
            self.write(cr, SUPERUSER_ID, [thread_id], {'message_last_post': fields.datetime.now()}, context=context)
        message = mail_message.browse(cr, uid, msg_id, context=context)
        if message.author_id and model and thread_id and type != 'notification' and not context.get('mail_create_nosubscribe'):
            self.message_subscribe(cr, uid, [thread_id], [message.author_id.id], context=context)
        return msg_id       
