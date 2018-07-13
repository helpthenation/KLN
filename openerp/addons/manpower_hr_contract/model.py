from openerp import models,fields,api,_
from openerp.tools.translate import _

class hr_employee(models.Model):
   
    _inherit = 'hr.employee'

           
           
    def create(self, cr, uid,vals, context=None): 
        r = super(hr_employee,self).create(cr,uid,vals,context=context) 
        cr.execute('''select id from hr_employee where account_id=%d'''  %(vals.get('account_id')))
        s=cr.fetchall()
        cr.execute('''select employee_id from analytic_employee_line where analytic_id=%d'''  %(vals.get('account_id')))
        d=cr.fetchall()
        h=[]
        for i in range(len(d)):
            h.append(d[i][0])
        for i in range(len(s)):
            if s[i][0] not in h:
                res={
                    'employee_id':s[i][0],
                    'analytic_id':vals.get('account_id'),
                    }
                self.pool.get('analytic.employee.line',self).create(cr,uid,res,context=context)
        return r     

        
