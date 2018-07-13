{
    'name' : 'OpenERP Pet Store',
    'version': '1.0',
    'summary': 'Sell pet toys',
    'category': 'Tools',
    'description':
        """
OpenERP Pet Store
=================

A wonderful application to sell pet toys.
        """,
    'data': [
        "petstore.xml",
    ],
    'js':['static/src/js/petstore.js'],
    'depends' : ['sale_stock'],
    'qweb': ['static/src/xml/petstore.xml'],
    'application': True,
    'installable':True,
}
