#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta
import time
from openerp import api,models

class stock_ledger_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(stock_ledger_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({

                'get_product_category': self._get_product_category,
                'get_product':self._get_product,
                'get_com':self._get_com,

        })



    def _get_product_category(self, data,company):
        
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_d = 'from_date' in data['form'] and [data['form']['from_date']] or []
        from_date1 = datetime.strptime(from_d[0], "%Y-%m-%d %H:%M:%S")
        from_date1 += timedelta(hours=5, minutes=30)
        to_d = 'to_date' in data['form'] and [data['form']['to_date']] or []
        to_date1 = datetime.strptime(to_d[0], "%Y-%m-%d %H:%M:%S")
        to_date1 += timedelta(hours=5, minutes=30)
        from_date=from_date1.strftime("%Y.%m.%d %H:%M:%S")
        to_date=to_date1.strftime("%Y.%m.%d %H:%M:%S")
      
        where=''

        if len(com[0]) < 2:

            where+=" pc.company_id=%d"%data['form']['company_ids'][0]
        else:
            where+=" pc.company_id in %s"%(tuple(com[0]),)
        if company!=1:
            self.cr.execute("""select distinct pc.name as name,pc.id as categ_id from product_template pt
                                    left join product_category pc on pc.id=pt.categ_id
                            where %s and pc.category_code!='TRND'"""% (where))
            category_list = [i for i in self.cr.dictfetchall()]

            return category_list
        else:   
            self.cr.execute("""select distinct pc.name as name from product_template pt
                                        left join product_category pc on pc.id=pt.categ_id
                                where %s and pc.category_code!='TRND'"""% (where))
            category_list = [i for i in self.cr.dictfetchall()]

            return category_list

    def _get_product(self,data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_d = 'from_date' in data['form'] and [data['form']['from_date']] or []
        from_date1 = datetime.strptime(from_d[0], "%Y-%m-%d %H:%M:%S")
        from_date1 += timedelta(hours=5, minutes=30)
        to_d = 'to_date' in data['form'] and [data['form']['to_date']] or []
        to_date1 = datetime.strptime(to_d[0], "%Y-%m-%d %H:%M:%S")
        to_date1 += timedelta(hours=5, minutes=30)
        from_date=from_date1.strftime("%Y.%m.%d %H:%M:%S")
        to_date=to_date1.strftime("%Y.%m.%d %H:%M:%S")
        where=''
        open_where=''
        in_where=''
        query_product=''
        if len(com[0]) < 2:
            where+=" AND sh.company_id=%d"%data['form']['company_ids'][0]
            open_where+=" AND sh.company_id=%d"%data['form']['company_ids'][0]
            in_where+=" AND pc.company_id=%d"%data['form']['company_ids'][0]
            
        else:
            where+=" AND sh.company_id in %s"%(tuple(com[0]),)
            open_where+=" AND sh.company_id in %s"%(tuple(com[0]),)
            in_where+=" AND pc.company_id in %s"%(tuple(com[0]),)
        if type(val) is int:
            where +=" AND pc.id=%d"%(val)
            open_where +=" AND pc.id=%d"%(val)
            in_where +=" AND pc.id=%d"%(val)
        else:
            where +=" AND pc.name='%s'"%(val)
            open_where +=" AND pc.name='%s'"%(val)
            in_where +=" AND pc.name='%s'"%(val)
        where+=" AND sh.date between '%s' and '%s'"%(from_date,to_date)
        open_where+=" AND sh.date <'%s'"%(from_date)
        self.cr.execute("""SELECT product_name,code,
                                sum(CASE WHEN opening_qty is not null THEN opening_qty ELSE 0 END) as opening_qty,
                                sum(CASE WHEN purchase_qty is not null  THEN purchase_qty ELSE 0 END) as purchase_qty,
                                sum(CASE WHEN sale_qty is not null  THEN sale_qty ELSE 0 END) as sale_qty,
                                sum(CASE WHEN sale_return is not null  THEN sale_return ELSE 0 END) as sale_return,
                                sum(CASE WHEN purchase_return is not null  THEN purchase_return ELSE 0 END) as purchase_return,
                                sum(CASE WHEN branch_purchase is not null  THEN branch_purchase ELSE 0 END) as branch_purchase,
                                sum(CASE WHEN branch_sale is not null  THEN branch_sale ELSE 0 END) as branch_sale,
                                sum(CASE WHEN on_hand is not null THEN on_hand ELSE 0 END) as on_hand,
                                sum(case WHEN on_hand !=0 THEN value ELSE 0 END) as value
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
                                    (COALESCE((open.quantity),0)+COALESCE((incoming.incoming),0)
                                    +COALESCE((sale_re.sale_return),0)+COALESCE((outgoing.outgoing),0)
                                    +COALESCE((pur_re.purchase_return),0)+COALESCE((inter_in.branch_purchase),0)
                                    +COALESCE((inter_out.branch_sale),0))as on_hand,
                                   -- ((COALESCE((open.cost),0)+COALESCE((incoming.cost),0)
                                  --  +COALESCE((sale_re.cost),0))+COALESCE((outgoing.cost),0)
                                   -- +COALESCE((pur_re.cost),0)+COALESCE((inter_out.cost),0)+COALESCE((inter_in.cost),0))as cost,
                                    ((COALESCE((open.value),0)+COALESCE((incoming.value),0)
                                    +COALESCE((sale_re.value),0))+COALESCE((outgoing.value),0)
                                    +COALESCE((pur_re.value),0)+COALESCE((inter_out.value),0)+COALESCE((inter_in.value),0))as value
                            FROM
                            ((SELECT DISTINCT product_temp.product_id as product_id,
                                            product_temp.code as code,
                                            product_temp.product as product_name,
                                            CASE WHEN opening.quantity is not null THEN opening.quantity ELSE 0 END as quantity,
                                            CASE WHEN opening.cost is not null THEN opening.cost ELSE 0 END as cost,
                                            CASE WHEN opening.value is not null THEN opening.value ELSE 0 END as value
                                FROM
                                    (SELECT pp.id as product_id,pt.name as product,pp.default_code as code 
                                        from product_template pt
                                        LEFT JOIN product_product pp ON (pp.product_tmpl_id=pt.id)
                                        LEFT JOIN product_category pc ON (pc.id=pt.categ_id)
                                            where pt.type='product' %s) product_temp full outer join
                                    (SELECT pt.name as product_name,sh.product_id as product_id,pp.default_code as code,
                                            sum(sh.quantity*sh.price_unit_on_quant) as cost,
                                            sum(sh.quantity*(select cost from product_price_history where product_template_id = pt.id and datetime <= now()
                                                        and cost > 0 order by datetime DESC limit 1)) as value,sum(sh.quantity) as quantity
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
                                                                            WHERE sp1.origin=sp.name AND sh1.product_id=sh.product_id) as quants,
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
                                            GROUP BY sh.product_id,pt.name,pp.default_code,sp.name,pt.id) as foo
                                        GROUP BY product_id,product,code,templ_id) as foo) incoming on (incoming.product_id=open.product_id)
                                LEFT JOIN
                                (SELECT product_id,code,
                                            product,
                                            outgoing,
                                            (outgoing * (SELECT cost FROM product_price_history
                                                                    WHERE product_template_id = templ_id AND datetime <= now()
                                                                    AND cost > 0 ORDER BY datetime DESC limit 1)) as value
                                FROM
                                    (SELECT product_id,code,product,sum(COALESCE((qty),0)+COALESCE((quants),0)) as outgoing,templ_id
                                            FROM
                                                (SELECT sh.product_id as product_id,pp.default_code as code,pt.id as templ_id,
                                                    pt.name as product,
                                                    (SELECT sum(sh1.quantity) FROM stock_history sh1
                                                                                    LEFT JOIN stock_move sm1 ON sh1.move_id=sm1.id
                                                                                    LEFT JOIN stock_picking sp1 ON sp1.id=sm1.picking_id
                                                                                WHERE sp1.origin=sp.name AND sh1.product_id=sh.product_id) as quants,
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
                                                GROUP BY sh.product_id,pt.name,pp.default_code,sp.name,pt.id) as foo
                                        GROUP BY product_id,product,code,templ_id) as foo) outgoing on (outgoing.product_id=open.product_id)
                                LEFT JOIN
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as sale_return,
                                    sum(sh.quantity*sh.price_unit_on_quant) as cost,
                                    sum(sh.quantity*(select cost from product_price_history where product_template_id = pt.id and datetime <= now()
                                                                        and cost > 0 order by datetime DESC limit 1)) as value
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
                                GROUP BY sh.product_id,pt.name,pp.default_code) sale_re ON (sale_re.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as purchase_return,
                                    sum(sh.quantity*sh.price_unit_on_quant) as cost,
                                    sum(sh.quantity*(select cost from product_price_history where product_template_id = pt.id and datetime <= now()
                                                                        and cost > 0 order by datetime DESC limit 1)) as value
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
                                GROUP BY sh.product_id,pt.name,pp.default_code) pur_re ON (pur_re.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as branch_purchase,
                                    sum(sh.quantity*sh.price_unit_on_quant) as cost,
                                    sum(sh.quantity*(select cost from product_price_history where product_template_id = pt.id and datetime <= now()
                                                                        and cost > 0 order by datetime DESC limit 1)) as value
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
                               GROUP BY sh.product_id,pt.name,pp.default_code) inter_in ON (inter_in.product_id= open.product_id)
                                LEFT JOIN
                                (SELECT
                                    sh.product_id as product_id,pp.default_code as code,
                                    pt.name as product,
                                    sum(sh.quantity) as branch_sale,
                                    sum(sh.quantity*sh.price_unit_on_quant) as cost,
                                    sum(sh.quantity*(select cost from product_price_history where product_template_id = pt.id and datetime <= now()
                                                                        and cost > 0 order by datetime DESC limit 1)) as value
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
                                GROUP BY sh.product_id,pt.name,pp.default_code) inter_out
                            ON (inter_out.product_id= open.product_id))) as foo WHERE opening_qty!=0 or (purchase_qty!=0 or
                                    sale_qty !=0 or
                                    sale_return !=0 or
                                    purchase_return !=0 or
                                    branch_purchase !=0 or
                                    branch_sale !=0) group by product_name,code  
                                    ORDER BY product_name
                        """ % (in_where,open_where,where,where,where,where,where,where))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list

    def _get_com(self,val):
        na = self.pool.get('res.company').browse(self.cr, self.uid, val)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            return na1
        else:
            na1 = 'Apex Agencies'
            return na1

class wrapped_stock_ledger_summary(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_stock_ledger'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_stock_ledger'
    _wrapped_report_class = stock_ledger_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
