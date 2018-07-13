# -*- coding: utf-8 -*-

from openerp import api, fields, models


#~ class purchase_detail(models.Model):
    #~ _inherit = 'purchase.order'
    #~ qty = fields.Float('Total Qty')
    #~ rec_qty = fields.Float('Received Qty')
    #~ billed_qty = fields.Float('Billed Qty')
    
class purchase_details_inherit(models.Model):
    _inherit = 'purchase.order.line'
    
    @api.depends('invoice_lines.invoice_id.state')
    def _compute_qty_invoiced(self):
        uom_obj = self.env['product.uom']
        for line in self:
            qty = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ['cancel']:
                    qty +=uom_obj._compute_qty(inv_line.uos_id.id,inv_line.quantity, line.product_uom.id)                        
            line.qty_invoiced = qty

    @api.depends('order_id.state', 'move_ids.state')
    def _compute_qty_received(self):
        uom_obj = self.env['product.uom']
        for line in self:
            if line.order_id.state not in ['purchase', 'done']:
                line.qty_received = 0.0
                continue
            if line.product_id.type not in ['consu', 'product']:
                line.qty_received = line.product_qty
                continue
            total = 0.0
            for move in line.move_ids:
                print'$$$$$$$$$$$$$$$$$$$$$$$',move.state,move.product_uom
                if move.state == 'done':
                    if move.product_uom.id != line.product_uom.id:
                        total += uom_obj._compute_qty(move.product_uom.id,move.product_uom_qty, line.product_uom.id)
                    else:
                        total += move.product_uom_qty
            print'@@@@@@@@@@@@@@@@@@@@@@@@',uom_obj._compute_qty(move.product_uom.id,move.product_uom_qty, line.product_uom.id)
            line.qty_received = total    
            
    #~ @api.multi
    #~ @api.depends('product_qty', 'qty_received','qty_invoiced')
    #~ def _get_details(self):
       #~ for rec in self:
           #~ self.env.cr.execute("""select pol.product_qty as product_qty , pol.qty_received as qty_received, 
                                           #~ pol.order_id as order_id,po.name as name, pol.qty_invoiced as qty_invoiced
                                           #~ from purchase_order_line as pol
                                           #~ join purchase_order as po on pol.order_id = po.id
                                           #~ where pol.id = %d"""%(rec.ids[0]))
           #~ s = self.env.cr.dictfetchall()
           #~ print'FFFFFFFFFFFFFFFFFFFFFFFFFFF',s
           #~ self.env.cr.execute(""" select sum(product_qty) as product_qty,sum(qty_received) as qty_received,sum(qty_invoiced)  as qty_invoiced from purchase_order_line
                                   #~ where order_id =%d"""%(s[0]['order_id']))
           #~ z =self.env.cr.dictfetchall()
           #~ print'SSSSSSSSSSSSSSSSSSSSSSSS',z
           #~ d = z[0]['product_qty']
           #~ e = z[0]['qty_received']
           #~ f = z[0]['qty_invoiced']
           #~ g = s[0]['name']
           #~ if f == None:
               #~ self.env.cr.execute(""" update purchase_order
                                       #~ set qty= %d,
                                       #~ rec_qty = %d,
                                       #~ billed_qty = 0.00
                                       #~ where name = '%s'"""%(d,e,g))  
           #~ else:
               #~ self.env.cr.execute(""" update purchase_order
                                       #~ set qty= %d,
                                       #~ rec_qty = %d,
                                       #~ billed_qty = %d
                                       #~ where name = '%s'"""%(d,e,f,g))  
                               
    qty_invoiced = fields.Float(compute='_compute_qty_invoiced', string="Billed Qty", store=True)
    qty_received = fields.Float(compute='_compute_qty_received', string="Received Qty", store=True)        
    #~ pay_sub = fields.Float(compute='_get_details', store=True)
