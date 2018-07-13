
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
from openerp.exceptions import ValidationError,Warning
class hr_contract_inherit(osv.osv):
    _inherit = 'hr.contract'
    
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):     
            res[order.id] = {
                'net_total': 0.0,
                'gross_total':0.0,
                'normal_price':0.0,
                'ot_price':0.0,
                'holiday_price':0.0,
            }
            val_gross = val_net = val_normal = val_ot = val_hol = 0.0
            for line in order.contract_line:
                val_gross += line.amount
                if line.rule_id.code=="BASIC":
                    val_normal = (line.amount / 30) / 8
                    val_ot = val_normal * 1.25
                    val_hol = val_normal * 1.50
                elif line.rule_id.type == 'remove':
                    val_net += line.amount
                else:
                    print "Success"
            net = val_gross - val_net     
            res[order.id]['net_total'] = val_gross
            res[order.id]['gross_total'] = val_gross
            res[order.id]['normal_price'] = ((val_gross /30) /8)
            res[order.id]['ot_price'] = val_ot
            res[order.id]['holiday_price'] = val_hol            
        return res    
            
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('hr.contract.line').browse(cr, uid, ids, context=context):
            result[line.contract_id.id] = True
        return result.keys()
   
    _columns = {
         'net_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Net',
            store={
                'hr.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line'], 10),
                'hr.contract.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The Net amount."),
            
         'gross_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Gross',
            store={
                'hr.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line'], 10),
                'hr.contract.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The Gross amount."),
         'contract_line': fields.one2many('hr.contract.line', 'contract_id','Contract Line'),
         'normal_price': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Normal Price',
            store={
                'hr.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line'], 10),
                'hr.contract.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The Normal Price"),
         'ot_price': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='OT Price',
            store={
                'hr.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line'], 10),
                'hr.contract.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The OT Price"),
         'holiday_price': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Holiday Price',
            store={
                'hr.contract': (lambda self, cr, uid, ids, c={}: ids, ['contract_line'], 10),
                'hr.contract.line': (_get_order, ['amount'], 10),
            },
            multi='sums', help="The Holiday Price"),
         'gross':fields.float('Gross',required=True),
         'food_allowance':fields.float('Food Allowance'),
         'hra':fields.float('House Rent Allowance'),
         'allowance': fields.selection([
                ('cash', '  Cash Allowance'),
                ('other', '  Other Allowance'),], 'Select An Allowance', required=True),
         'resumption_details_line' :fields.one2many('rejoin.detail','resumption_id','Resumption Detail'),     
               }
    def create(self, cr, uid, values, context=None):
        rule = self.pool.get('mline.payroll.rule')
        contract_lines = self.pool.get('hr.contract.line')
        hra_rule = rule.search(cr, uid, [('code', '=', 'HRA')], context=context)
        basic_rule = rule.search(cr, uid, [('code', '=', 'BASIC')], context=context)        
        food_rule = rule.search(cr, uid, [('code', '=', 'FOOD')], context=context)        
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)        
        cash_rule = rule.search(cr, uid, [('code', '=', 'CSH')], context=context)        
        food=values.get('food_allowance') or 0.00
        hra=values.get('hra') or 0.00
        if context is None:
            context = {}
        new_rec=super(hr_contract_inherit, self).create(cr, uid, values, context=context)
        if values.get('gross'):
            vals={
             'contract_id': new_rec,
             'rule_id':basic_rule[0],
             'amount':values['gross'] * 0.6,          
                }
            contract_lines.create(cr,uid,vals,context=context)
        if values.get('food_allowance'):
            vals={
             'contract_id': new_rec,
             'rule_id':food_rule[0],
             'amount':values['food_allowance'],          
                }
            contract_lines.create(cr,uid,vals,context=context)
        else:
            vals={
             'contract_id': new_rec,
             'rule_id':food_rule[0],
             'amount':0.00,          
                }
            contract_lines.create(cr,uid,vals,context=context)              
        if values.get('hra'):
            vals={
             'contract_id': new_rec,
             'rule_id':hra_rule[0],
             'amount':values['hra'],          
                }
            contract_lines.create(cr,uid,vals,context=context)                        
        else:
            vals={
             'contract_id': new_rec,
             'rule_id':hra_rule[0],
             'amount':0.00,          
                }
            contract_lines.create(cr,uid,vals,context=context)
        if values['allowance'] == 'other':
            vals={
             'contract_id': new_rec,
             'rule_id':oa_rule[0],
             'amount':values['gross'] - (values['gross'] * 0.6) - hra - food
                }
            contract_lines.create(cr,uid,vals,context=context)
        elif values['allowance'] == 'cash':
            vals={
             'contract_id': new_rec,
             'rule_id':cash_rule[0],
             'amount':values['gross'] - (values['gross'] * 0.6) - hra - food 
                }
            contract_lines.create(cr,uid,vals,context=context) 
        return new_rec 
            
                                   
    def onchange_gross(self, cr, uid, ids, gross, context):
        rule = self.pool.get('mline.payroll.rule')
        contract_lines = self.pool.get('hr.contract.line')        
        basic_rule = rule.search(cr, uid, [('code', '=', 'BASIC')], context=context)
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)      
        cash_rule = rule.search(cr, uid, [('code', '=', 'CSH')], context=context)      
        if ids and gross == 0.0:
                raise osv.except_osv(_('Invalid Action!'), _('Gross Amount Cannot Be 0.00. Please Enter A Valid Amount!'))            
        if ids and gross:
            obj = self.browse(cr, uid, ids)
            basic_food_hra=[]
            for record in obj.contract_line:
                if record.rule_id.code == 'BASIC':
                    record.write({'amount': gross * 0.6})
                    record.amount = gross * 0.6
                    basic_food_hra.append(gross * 0.6)
                elif record.rule_id.code == 'HRA':  
                    basic_food_hra.append(record.amount)
                elif record.rule_id.code == 'FOOD': 
                    basic_food_hra.append(record.amount)    
                elif record.rule_id.code == 'OA' or 'CSH':    
                    record.write({'amount':gross - sum(basic_food_hra)})  
                    record.amount = gross - sum(basic_food_hra)     
            cr.execute('''select sum(amount) from hr_contract_line where contract_id=%d'''%(ids[0]))
            line=cr.dictfetchone()
            if line:
                cr.execute('''update  hr_contract set gross_total = %d where id=%d'''%(line['sum'],ids[0]))
                cr.execute('''update  hr_contract set net_total = %d where id=%d'''%(line['sum'],ids[0]))
            nl_price=(gross/30.0)/8
            ot_price=(((gross*0.6)/30.0)/8.0) * 1.25
            ht_price=(((gross*0.6)/30.0)/8.0) * 1.50      
                
            cr.execute('''update hr_contract set normal_price=%d,ot_price=%d,holiday_price=%d where id =%d'''%(nl_price,ot_price,ht_price,ids[0]))   
                
    def onchange_food(self, cr, uid, ids,food_allowance,context): 
        rule = self.pool.get('mline.payroll.rule')
        contract_lines = self.pool.get('hr.contract.line')        
        food_rule = rule.search(cr, uid, [('code', '=', 'FOOD')], context=context)
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)  
        if ids:
            obj = self.browse(cr, uid, ids)
            basic_food_hra=[]
            for record in obj.contract_line:
                if record.rule_id.code == 'BASIC':                    
                    basic_food_hra.append(record.amount)
                elif record.rule_id.code == 'HRA':  
                    basic_food_hra.append(record.amount)
                elif record.rule_id.code == 'FOOD': 
                    record.write({'amount': food_allowance})   
                    basic_food_hra.append(food_allowance) 
                elif record.rule_id.code == 'OA' or 'CSH':    
                    record.write({'amount':obj.gross - sum(basic_food_hra)})  
                    record.amount = obj.gross - sum(basic_food_hra)    
            cr.execute('''select sum(amount) from hr_contract_line where contract_id=%d'''%(ids[0]))
            line=cr.dictfetchone()
            if line:
                cr.execute('''update  hr_contract set gross_total = %d where id=%d'''%(line['sum'],ids[0]))
                cr.execute('''update  hr_contract set net_total = %d where id=%d'''%(line['sum'],ids[0]))                      
    def onchange_hra(self, cr, uid, ids,hra,context):
        rule = self.pool.get('mline.payroll.rule')
        contract_lines = self.pool.get('hr.contract.line')
        hra_rule = rule.search(cr, uid, [('code', '=', 'HRA')], context=context)
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)  
        if ids:
            obj = self.browse(cr, uid, ids)
            basic_food_hra=[]
            for record in obj.contract_line:
                if record.rule_id.code == 'BASIC':                    
                    basic_food_hra.append(record.amount)
                elif record.rule_id.code == 'HRA':  
                    record.write({'amount': hra})
                    basic_food_hra.append(hra)
                elif record.rule_id.code == 'FOOD':                        
                    basic_food_hra.append(record.amount)
                elif record.rule_id.code == 'OA' or 'CSH':    
                    record.write({'amount':obj.gross - sum(basic_food_hra)})  
                    record.amount = obj.gross - sum(basic_food_hra)        
            cr.execute('''select sum(amount) from hr_contract_line where contract_id=%d'''%(ids[0]))
            line=cr.dictfetchone()
            if line:
                cr.execute('''update  hr_contract set gross_total = %d where id=%d'''%(line['sum'],ids[0]))
                cr.execute('''update  hr_contract set net_total = %d where id=%d'''%(line['sum'],ids[0]))                

    def onchange_allowance(self, cr, uid, ids,allowance,context):
        rule = self.pool.get('mline.payroll.rule')
        contract_lines = self.pool.get('hr.contract.line')
        cash_rule = rule.search(cr, uid, [('code', '=', 'CSH')], context=context)
        oa_rule = rule.search(cr, uid, [('code', '=', 'OA')], context=context)  
        if ids and allowance:
            obj = self.browse(cr, uid, ids)
            for record in obj.contract_line:
                if allowance == 'cash':
                    if record.rule_id.code == 'OA': 
                        record.write({'rule_id':cash_rule[0]})
                    elif record.rule_id.code == 'CSH':
                        record.write({'rule_id':cash_rule[0]})    
                if allowance == 'other':
                    if record.rule_id.code == 'OA': 
                        record.write({'rule_id':oa_rule[0]})
                    elif record.rule_id.code == 'CSH':
                        record.write({'rule_id':oa_rule[0]})  

                                                                   
hr_contract_inherit()

class hr_contract_line(osv.osv):
    _name = 'hr.contract.line'
    _columns = { 
       
         'contract_id': fields.many2one('hr.contract', 'Contract'),
         'rule_id':fields.many2one('mline.payroll.rule', 'Rule'),
         'amount':fields.float('Cost', required=True),
             }
hr_contract_line()


class rejoin_detail(osv.osv):
    _name="rejoin.detail"
    
    _columns={
              'resumption_id':fields.many2one('hr.contract','Resumption Details'),
              'rejoining_date':fields.date('Entry Date'),
              'start_date':fields.date('Exits Date'),
              'end_date':fields.date('End date'),
              'type':fields.many2one('hr.holidays.status','Leave Type'),
              'detail_id':fields.many2one('resumption.details','Detail Id')
              }
