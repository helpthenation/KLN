from openerp.osv import fields, osv

class petstore_homepage(osv.osv):
    _name = "petstore.homepage"
    _columns={
        'name':fields.char('Name',size=64)
    }
