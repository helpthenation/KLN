# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
import time
from dateutil import relativedelta
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
import xlsxwriter
import StringIO
import base64
import os
class stock_ledger_summary(osv.osv_memory):
    _name = 'stock.ledger.summary'


    def _get_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def _get_default_company(self, cr, uid, context=None):
        company_list=[]
        company_ids = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if company_ids==1:
            val=self.pool.get('res.company').search(cr, uid,[])
            rec=[i for i in val if i!=company_ids ]
            company_list.extend(rec)
        else:
            company_list.append(company_ids)
        return company_list

    _description = 'Stock Ledger Summary'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'company_ids':fields.many2many('res.company', 'company_report_stock_ledger', 'stock_id', 'company_id1', 'Company'),
        'from_date': fields.datetime('From Date', required=True),
        'to_date': fields.datetime('To Date', required=True),
        'landscape': fields.boolean("Landscape Mode"),
        'filedata' : fields.binary('Download file', readonly=True),
        'filename' : fields.char('Filename', size=64, readonly=True),
    }

    _defaults = {
         'company_id':_get_company,
         'company_ids': _get_default_company,
         'from_date': lambda *a: time.strftime('%Y-%m-01 00:00:00'),
         'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
         'landscape': True,

    }
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        return result

    def _print_report(self, cr, uid, ids, data, context=None):
        return self.pool['report'].get_action(cr, uid, [], 'fnet_aea_sale_report.report_stock_ledger', data=data, context=context)

    def wiz_print_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['landscape','from_date', 'to_date','company_ids'], context=context)[0]
        data['form'].update(self.read(cr, uid, ids, ['landscape'])[0])
        for field in ['company_ids']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        if data['form']['landscape'] is False:
            data['form'].pop('landscape')
        else:
            context['landscape'] = data['form']['landscape']

        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)


    def wiz_print_report_excel(self, cr, uid, ids, context=None):
        form_data = self.read(cr, uid, ids, ['from_date','to_date','company_ids'], context=context)[0]
        com = 'company_ids' in form_data and [form_data['company_ids']] or []
        from_d = 'from_date' in form_data and [form_data['from_date']] or []
        from_date1 = datetime.strptime(from_d[0], "%Y-%m-%d %H:%M:%S")
        from_date1 += timedelta(hours=5, minutes=30)
        to_d = 'to_date' in form_data and [form_data['to_date']] or []
        to_date1 = datetime.strptime(to_d[0], "%Y-%m-%d %H:%M:%S")
        to_date1 += timedelta(hours=5, minutes=30)
        from_date=from_date1.strftime("%Y.%m.%d %H:%M:%S")
        to_date=to_date1.strftime("%Y.%m.%d %H:%M:%S")
        output = StringIO.StringIO()
        url = os.path.dirname(os.path.realpath('excel_reports'))
        workbook = xlsxwriter.Workbook(url + 'Stock and Ledger Summary.xls')
        worksheet = workbook.add_worksheet()
        format_head = workbook.add_format({
            'bold': 1,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
        })
        table_head = workbook.add_format({
            'bold': 1,
            'border': 1,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
        })
        product_head = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'left',
        })
        content_format = workbook.add_format({
            #~ 'align': 'left',
            'font_size': 10,
            'valign': 'vcenter', })
        cum_total = workbook.add_format({
            'align': 'left',
            'bold': 1,
            'font_size': 12,
            'valign': 'vcenter',
        })
        cum_total_value = workbook.add_format({
            'align': 'right',
            'bold': 1,
            'font_size': 12,
            'valign': 'vcenter',
        })

        product_cum_total = workbook.add_format({
            'align': 'left',
            'bold': 1,
            'font_size': 10,
            'valign': 'vcenter',
        })

        product_cum_value = workbook.add_format({
            'align': 'right',
            'bold': 1,
            'font_size': 10,
            'valign': 'vcenter',
        })
        productline_cum_value = workbook.add_format({
            'align': 'right',
            'font_size': 10,
            'valign': 'vcenter',
        })

        where=''
        company = self.pool.get('res.users')._get_company(cr, uid, context=context)
        company_name = self.pool.get('res.company').browse(cr, uid, company,context=context)
        if len(com[0]) < 2:

            where+=" pc.company_id=%d"%form_data['company_ids'][0]
        else:
            where+=" pc.company_id in %s"%(tuple(com[0]),)
        print where
        if company!=1:
            cr.execute("""select distinct pc.name as name,pc.id as categ_id from product_template pt
                                    left join product_category pc on pc.id=pt.categ_id
                            where %s and pc.category_code!='TRND'"""% (where))
            category_list = [i for i in cr.dictfetchall()]
            print "11111111111111",category_list

            worksheet.merge_range('F2:I2',company_name.city +" Branch"  ,format_head)
        else:
            cr.execute("""select distinct pc.name as name from product_template pt
                                        left join product_category pc on pc.id=pt.categ_id
                                where %s and pc.category_code!='TRND'"""% (where))
            category_list = [i for i in cr.dictfetchall()]
        worksheet.merge_range('F3:I3','STOCK &LEDGER SUMMARY ',format_head)
        worksheet.merge_range('F4:I4',"for  "+ str(from_date) +" to "+str(to_date),format_head)
        na = self.pool.get('res.company').browse(cr, uid, company,context=context)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            print na1
        else:
            na1 = 'Apex Agencies'
            print na1,time.strftime('%d-%m-%Y %H:%M:%S')

        if company!=1:
            worksheet.merge_range('A1:N1', na1 + " "+ str( company_name.state_id.name ),format_head)
        else:
            worksheet.merge_range('A1:N1', na1,format_head)

        worksheet.merge_range('A1:N1', na1 + " "+ str( company_name.state_id.name ),format_head)
        worksheet.merge_range('M4:N4', time.strftime('%d-%m-%Y %H:%M:%S'), format_head)
        worksheet.set_column('A:A',5)
        worksheet.set_column('B:B',15)
        worksheet.set_column('C:C',35)
        worksheet.set_column('D:D',5)
        worksheet.set_column('E:E',15)
        worksheet.set_column('F:F',15)
        worksheet.set_column('G:G',15)
        worksheet.set_column('H:H',15)
        worksheet.set_column('I:I',15)
        worksheet.set_column('J:J',15)
        worksheet.set_column('K:K',15)
        worksheet.set_column('L:L',15)
        worksheet.set_column('M:M',15)
        worksheet.set_column('N:N',15)


        worksheet.write('A6', "S.No", table_head)
        worksheet.write('B6', "Pr.Code", table_head)
        worksheet.write('C6', "Product", table_head)
        worksheet.write('D6', "UOM", table_head)
        worksheet.write('E6', "Opn.QTY", table_head)
        worksheet.write('F6', "Pur QTY", table_head)
        worksheet.write('G6', "Branch Tfr IN", table_head)
        worksheet.write('H6', "Sales Rtn. QTY", table_head)
        worksheet.write('I6', "Sales QTY", table_head)
        worksheet.write('J6', "Branch Tfr OUT", table_head)
        worksheet.write('K6', "Pur Rtn. QTY", table_head)
        worksheet.write('L6', "Outward. QTY", table_head)
        worksheet.write('M6', "On Hand", table_head)
        worksheet.write('N6', "Value", table_head)

        n = 7
        tsv_opening = tsv_purchase_quant = tsv_sale_quant = tsv_sale_ret = tsv_branch_in = tsv_branch_out = 0
        tsv_pur_ret = tsv_outward = tsv_onhand_quant = tsv_qty_value = 0

        for pc in category_list:

            where = ''
            open_where = ''
            in_where = ''
            query_product = ''

            if len(com[0]) < 2:
                where+=" AND sh.company_id=%d"%form_data['company_ids'][0]
                open_where+=" AND sh.company_id=%d"%form_data['company_ids'][0]
                in_where+=" AND pc.company_id=%d"%form_data['company_ids'][0]

            else:
                where+=" AND sh.company_id in %s"%(tuple(com[0]),)
                open_where+=" AND sh.company_id in %s"%(tuple(com[0]),)
                in_where+=" AND pc.company_id in %s"%(tuple(com[0]),)
            if type(pc['name']) is int:
                where +=" AND pc.id=%d"%(val)
                open_where +=" AND pc.id=%d"%(val)
                in_where +=" AND pc.id=%d"%(val)
            else:
                where +=" AND pc.name='%s'"%(pc['name'])
                open_where +=" AND pc.name='%s'"%(pc['name'])
                in_where +=" AND pc.name='%s'"%(pc['name'])


            where += " AND sh.date between '%s' and '%s'"%(from_date,to_date)
            open_where += " AND sh.date <'%s'"%(from_date)
            cr.execute("""SELECT product_name,code,
                                sum(CASE WHEN opening_qty is not null THEN opening_qty ELSE 0 END) as opening_qty,
                                sum(CASE WHEN purchase_qty is not null  THEN purchase_qty ELSE 0 END) as purchase_qty,
                                sum(CASE WHEN sale_qty is not null  THEN sale_qty ELSE 0 END) as sale_qty,
                                sum(CASE WHEN sale_return is not null  THEN sale_return ELSE 0 END) as sale_return,
                                sum(CASE WHEN purchase_return is not null  THEN purchase_return ELSE 0 END) as purchase_return,
                                sum(CASE WHEN branch_purchase is not null  THEN branch_purchase ELSE 0 END) as branch_purchase,
                                sum(CASE WHEN branch_sale is not null  THEN branch_sale ELSE 0 END) as branch_sale,
                                sum(CASE WHEN inventry_loss is not null THEN inventry_loss ELSE 0 END) as inventry_loss,
                                sum(CASE WHEN on_hand is not null THEN on_hand ELSE 0 END) as on_hand,
                                sum(case WHEN on_hand !=0 THEN on_hand*(COALESCE(price,0)) ELSE 0 END) as value
                                FROM
                                (SELECT open.product_name as product_name,
                                    CASE WHEN open.code is not null THEN open.code
                                        WHEN incoming.code is not null THEN incoming.code
                                    WHEN outgoing.code is not null THEN outgoing.code
                                    WHEN sale_re.code is not null THEN sale_re.code
                                    WHEN pur_re.code is not null THEN pur_re.code
                                    WHEN inter_in.code is not null THEN inter_in.code ELSE inter_out.code END as code,
                                    open.product_id as product_id,
                                    open.quantity as opening_qty,
                                    incoming.incoming as purchase_qty,
                                    outgoing.outgoing as sale_qty,
                                    sale_re.sale_return as sale_return,
                                    pur_re.purchase_return as purchase_return,
                                    inter_in.branch_purchase as branch_purchase,
                                    inter_out.branch_sale as branch_sale,
                                    invent_loss.inventry_loss as inventry_loss,
                                    (select cost from product_price_history where product_template_id = open.template_id and datetime <= '%s'
                                            and cost > 0 order by datetime DESC limit 1) as price,
                                    (COALESCE((open.quantity),0)+COALESCE((incoming.incoming),0)
                                    +COALESCE((sale_re.sale_return),0)+COALESCE((outgoing.outgoing),0)
                                    +COALESCE((pur_re.purchase_return),0)+COALESCE((inter_in.branch_purchase),0)
                                    +COALESCE((inter_out.branch_sale),0)+COALESCE((invent_loss.inventry_loss),0)) as on_hand
                                   -- ((COALESCE((open.cost),0)+COALESCE((incoming.cost),0)
                                  --  +COALESCE((sale_re.cost),0))+COALESCE((outgoing.cost),0)
                                   -- +COALESCE((pur_re.cost),0)+COALESCE((inter_out.cost),0)+COALESCE((inter_in.cost),0))as cost,
                                    --((COALESCE((open.value),0)+COALESCE((incoming.value),0)
                                   -- +COALESCE((sale_re.value),0))+COALESCE((outgoing.value),0)
                                   -- +COALESCE((pur_re.value),0)+COALESCE((inter_out.value),0)+COALESCE((inter_in.value),0)+COALESCE((invent_loss.inventry_loss),0))as value
                                FROM
                                ((SELECT DISTINCT product_temp.product_id as product_id,product_temp.product_temp_id as template_id,
                                        product_temp.code as code,
                                        product_temp.product as product_name,
                                        CASE WHEN opening.quantity is not null THEN opening.quantity ELSE 0 END as quantity
                                FROM
                                    (SELECT pp.id as product_id,pt.name as product,pp.default_code as code,pt.id as product_temp_id
                                    from product_template pt
                                    LEFT JOIN product_product pp ON (pp.product_tmpl_id=pt.id)
                                    LEFT JOIN product_category pc ON (pc.id=pt.categ_id)
                                        where pt.type='product' %s) product_temp full outer join
                                    (SELECT pt.name as product_name,sh.product_id as product_id,pp.default_code as code,sum(sh.quantity) as quantity
                                 FROM stock_history sh
                                    LEFT JOIN product_product pp ON pp.id= sh.product_id
                                    LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                    LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                    LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                    LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                    LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                    LEFT JOIN res_company rc ON rc.id=sh.company_id
                                    WHERE  sm.state ='done' AND pt.type='product' --and (spt.code in ('incoming','outgoing','internal') or sm.picking_type_id is null)
                                    %s
                                     GROUP BY pt.name,sh.product_id,pp.default_code  ORDER BY product_name)
                                     opening ON (product_temp.product_id=opening.product_id) ORDER BY product_id) open
                                LEFT JOIN
                                (SELECT product_id,code,
                                        product,
                                        incoming,
                                        (incoming * (SELECT cost FROM product_price_history
                                                    WHERE product_template_id = templ_id AND datetime <= now()
                                                    AND cost > 0 ORDER BY datetime DESC limit 1)) as value
                                FROM
                                (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as incoming,templ_id
                                    FROM
                                        (SELECT sh.product_id as product_id,pp.default_code as code,pt.id as templ_id,
                                        pt.name as product,
                                        (SELECT sum(sh1.quantity) FROM stock_history sh1
                                            LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                            LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                        WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                            AND sm1.origin_returned_move_id is not null) as quants,
                                        sum(sh.quantity) as qty
                                        FROM stock_history sh
                                        LEFT JOIN product_product pp ON pp.id= sh.product_id
                                        LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                        LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                        LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                        LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                        LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                        LEFT JOIN res_company rc ON rc.id=sh.company_id
                                        LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                        WHERE sm.state='done' AND pt.type='product' AND spt.code ='incoming'
                                        AND rp.branch_transfer is False AND sm.origin_returned_move_id is null
                                        --and sp.actual_return is False
                                         %s
                                        GROUP BY sh.product_id,pt.name,pp.default_code,sp.name,pt.id,sp.group_id) as foo
                                    GROUP BY product_id,product,code,templ_id) as foo) incoming on (incoming.product_id=open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,
                                        product,
                                        outgoing
                                FROM
                                    (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as outgoing,templ_id
                                        FROM
                                        (SELECT sh.product_id as product_id,pp.default_code as code,pt.id as templ_id,
                                            pt.name as product,
                                            (SELECT sum(sh1.quantity) FROM stock_history sh1
                                            LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                            LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                        WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                            AND sm1.origin_returned_move_id is not null) as quants,
                                            sum(sh.quantity) as qty
                                        FROM stock_history sh
                                        LEFT JOIN product_product pp ON pp.id= sh.product_id
                                        LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                        LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                        LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                        LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                        LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                        LEFT JOIN res_company rc ON rc.id=sh.company_id
                                        LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                        WHERE sp.state='done' AND pt.type='product' AND spt.code ='outgoing'
                                            AND rp.branch_transfer is False AND sm.origin_returned_move_id is null
                                            --and sp.actual_return is False
                                             %s
                                        GROUP BY sh.product_id,pt.name,pp.default_code,sp.name,pt.id,sp.group_id) as foo
                                    GROUP BY product_id,product,code,templ_id) as foo) outgoing on (outgoing.product_id=open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as sale_return
                                FROM
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,pt.id as templ_id,
                                    (SELECT sum(sh1.quantity) FROM stock_history sh1
                                    LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                    LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                    WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                    AND sm1.origin_returned_move_id is not null) as quants,
                                    sum(sh.quantity) as qty
                                FROM stock_history sh
                                LEFT JOIN product_product pp ON pp.id= sh.product_id
                                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                LEFT JOIN res_company rc ON rc.id=sh.company_id
                                LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                WHERE spt.code ='incoming' AND pt.type='product' AND sm.state='done'
                                AND sp.actual_return is True
                                AND sm.origin_returned_move_id is not null
                                 %s
                                GROUP BY sh.product_id,pt.id,pt.name,pp.default_code,sp.group_id) as sale_return
                                GROUP BY product_id,product,code,templ_id) sale_re ON (sale_re.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as purchase_return
                                FROM
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    (SELECT sum(sh1.quantity) FROM stock_history sh1
                                    LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                    LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                    WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                    AND sm1.origin_returned_move_id is not null) as quants,
                                    sum(sh.quantity) as qty
                                 FROM stock_history sh
                                LEFT JOIN product_product pp ON pp.id= sh.product_id
                                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                LEFT JOIN res_company rc ON rc.id=sh.company_id
                                LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                WHERE spt.code in ('outgoing') AND pt.type='product' AND sm.state='done' AND sp.actual_return is True
                                AND sm.origin_returned_move_id is not null
                                 %s
                                GROUP BY sh.product_id,pt.name,pp.default_code,sp.group_id) as pur_return
                                GROUP BY product_id,product,code) pur_re ON (pur_re.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as branch_purchase
                                FROM
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    (SELECT sum(sh1.quantity) FROM stock_history sh1
                                    LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                    LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                    WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                    AND sm1.origin_returned_move_id is not null) as quants,
                                    sum(sh.quantity) as qty
                                 FROM stock_history sh
                                LEFT JOIN product_product pp ON pp.id= sh.product_id
                                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                LEFT JOIN res_company rc ON rc.id=sh.company_id
                                LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                WHERE spt.code in ('incoming') AND pt.type='product' AND sm.state='done' AND rp.branch_transfer is True
                                AND sp.actual_return is False
                                AND sm.origin_returned_move_id is null
                                %s
                                GROUP BY sh.product_id,pt.name,pp.default_code,sp.group_id) as inter_return
                                GROUP BY product_id,product,code) inter_in ON (inter_in.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as inventry_loss
                                 FROM stock_history sh
                                LEFT JOIN product_product pp ON pp.id= sh.product_id
                                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                --LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                --LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                LEFT JOIN res_company rc ON rc.id=sh.company_id
                                LEFT JOIN res_partner rp ON (rp.id=sm.partner_id)
                                WHERE  pt.type='product' AND sm.state='done' --AND rp.branch_transfer is True
                                AND sm.picking_type_id is null
                                 %s
                                GROUP BY sh.product_id,pt.name,pp.default_code) invent_loss ON (invent_loss.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as branch_sale
                                FROM
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as qty,
                                    (SELECT sum(sh1.quantity) FROM stock_history sh1
                                    LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                    LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                    WHERE sp1.group_id=sp.group_id AND sh1.product_id=sh.product_id
                                    AND sm1.origin_returned_move_id is not null) as quants
                                 FROM stock_history sh
                                LEFT JOIN product_product pp ON pp.id= sh.product_id
                                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                                LEFT JOIN product_category pc ON pc.id=pt.categ_id
                                LEFT JOIN stock_move sm ON sm.id=sh.move_id
                                LEFT JOIN stock_picking sp ON sp.id=sm.picking_id
                                LEFT JOIN stock_picking_type spt ON spt.id=sp.picking_type_id
                                LEFT JOIN res_company rc ON rc.id=sh.company_id
                                LEFT JOIN res_partner rp ON (rp.id=sp.partner_id)
                                WHERE spt.code in ('outgoing') AND pt.type='product' AND sm.state='done' AND rp.branch_transfer is True
                                 AND sp.actual_return is False
                                 AND sm.origin_returned_move_id is null
                                  %s
                                GROUP BY sh.product_id,pt.name,pp.default_code,sp.group_id) as in_out
                                GROUP BY product_id,product,code) inter_out
                                ON (inter_out.product_id= open.product_id))) as foo
                                WHERE opening_qty!=0 or (purchase_qty!=0 or
                                    sale_qty !=0 or
                                    sale_return !=0 or
                                    purchase_return !=0 or
                                    branch_purchase !=0 or
                                    branch_sale !=0) group by product_name,code
                                    ORDER BY product_name
                            """ % (to_date,in_where,open_where,where,where,where,where,where,where,where))
            line_list = [i for i in cr.dictfetchall()]
            #~ print line_list
            np = 1
            m = 0
            opening = purchase_quant = sale_quant = sale_ret = branch_in = branch_out = pur_ret= onhand_quant = outward=qty_value=0
            if len(line_list):
                worksheet.merge_range('A'+str(n)+":"+'N'+str(n),pc['name'],product_head)
            for dt in line_list:
                n += 1
                worksheet.write('A'+str(n), np, content_format)
                worksheet.write('B'+str(n), dt['code'], content_format)
                worksheet.write('C'+str(n), dt['product_name'], content_format)
                worksheet.write('D'+str(n), 'PCS', content_format)
                worksheet.write('E'+str(n), dt['opening_qty'], productline_cum_value)
                opening +=  dt['opening_qty']
                worksheet.write('F'+str(n), dt['purchase_qty'], productline_cum_value)
                purchase_quant += dt['purchase_qty']
                worksheet.write('H'+str(n), dt['branch_purchase'], productline_cum_value)
                branch_in +=  dt['branch_purchase']
                worksheet.write('G'+str(n), dt['sale_return'], productline_cum_value)
                sale_ret +=  dt['sale_return']
                worksheet.write('I'+str(n), -dt['sale_qty'], productline_cum_value)
                sale_quant += dt['sale_qty']
                worksheet.write('J'+str(n), -dt['branch_sale'], productline_cum_value)
                branch_out += dt['branch_sale']
                worksheet.write('K'+str(n), -dt['purchase_return'], productline_cum_value)
                pur_ret +=  dt['purchase_return']
                if dt['inventry_loss'] > 0:
                    worksheet.write('L'+str(n), dt['inventry_loss'], productline_cum_value)
                else:
                    worksheet.write('L'+str(n), -dt['inventry_loss'], productline_cum_value)
                outward += dt['inventry_loss']

                if  dt['on_hand'] is not None:
                    worksheet.write('M'+str(n), dt['on_hand'], productline_cum_value)
                    onhand_quant +=  dt['on_hand']
                if dt['on_hand'] != 0:
                    worksheet.write('N'+str(n), '%.2f' % dt['value'], productline_cum_value)
                    qty_value +=  dt['value']
                elif dt['on_hand'] == 0:
                    worksheet.write('N'+str(n), 0.00, productline_cum_value)

                np += 1
            n += 1
            if len(line_list):
                worksheet.write('C'+str(n), "** TOTAL for the Product Group **", product_cum_total)
                worksheet.write('E'+str(n), opening, product_cum_value)
                worksheet.write('F'+str(n), purchase_quant, product_cum_value)
                worksheet.write('G'+str(n), branch_in, product_cum_value)
                worksheet.write('H'+str(n), sale_ret, product_cum_value)
                worksheet.write('I'+str(n), -(sale_quant), product_cum_value)
                worksheet.write('J'+str(n), -(branch_out), product_cum_value)
                worksheet.write('K'+str(n), -(pur_ret), product_cum_value)
                if outward > 0:
                    worksheet.write('L'+str(n), outward, product_cum_value)
                else:
                    worksheet.write('L'+str(n), -(outward), product_cum_value)

                worksheet.write('M'+str(n), onhand_quant, product_cum_value)
                worksheet.write('N'+str(n), '%.2f' %qty_value, product_cum_value)

            tsv_opening += opening
            tsv_purchase_quant += purchase_quant
            tsv_branch_in += branch_in
            tsv_sale_ret += sale_ret
            tsv_sale_quant +=sale_quant
            tsv_branch_out += branch_out
            tsv_pur_ret += pur_ret
            tsv_outward += outward
            tsv_onhand_quant += onhand_quant
            tsv_qty_value += qty_value

            n += 1

        worksheet.write('C'+str(n), "** Total Stock Value for the Unit **", cum_total)
        worksheet.write('E'+str(n), tsv_opening, cum_total_value)
        worksheet.write('F'+str(n), tsv_purchase_quant, cum_total_value)
        worksheet.write('G'+str(n), tsv_branch_in, cum_total_value)
        worksheet.write('H'+str(n), tsv_sale_ret, cum_total_value)
        worksheet.write('I'+str(n), -tsv_sale_quant, cum_total_value)
        worksheet.write('J'+str(n), tsv_pur_ret, cum_total_value)
        worksheet.write('K'+str(n), pur_ret, cum_total_value)
        worksheet.write('L'+str(n), tsv_outward, cum_total_value)
        worksheet.write('M'+str(n), tsv_onhand_quant, cum_total_value)
        worksheet.write('N'+str(n), '%.2f' % tsv_qty_value, cum_total_value)

        workbook.close()
        fp = open(url + 'Stock and Ledger Summary.xls','rb+')
        data= fp.read()
        out = base64.encodestring(data)
        self.write(cr,uid,ids,{'filedata':out,'filename':'Stock and Ledger Summary.xls'}, context=context)
        current_id = self.read(cr, uid, ids, ['id'],context=context)[0]['id']
        return {
            'name': 'Stock and Ledger Summary',
            'res_model': 'stock.ledger.summary',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'res_id': current_id,
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
