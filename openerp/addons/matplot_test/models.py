# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
import base64
from openerp import models, fields, api
import matplotlib.pyplot as plt
import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
class matplot_test(models.Model): 
    _name='matplot.test'
    abin = fields.Binary(compute='plotfig')

    @api.multi
    def plotfig(self):
        x = [2,4,6,8,10]
        x2 = [1,3,5,7,9]
        y = [4,7,4,7,3]
        y2 = [5,3,2,6,2]

        plt.bar(x, y, label="One", color='m')
        plt.bar(x2, y2, label="Two", color='g')

        plt.xlabel('bar number')
        plt.ylabel('bar height')
        plt.title('Bar Chart Tutorial')
        plt.legend()
        plt.savefig('/home/iswasu-8/Desktop/pic.png')
        pic_data = open('/home/iswasu-8/Desktop/pic.png','rb').read()
        self.write({'abin':base64.encodestring(pic_data )})
        #~ plt.savefig('home\iswasu-8\a1.png')
        #~ pic_data = open('home\iswasu-8\a1.png', 'rb').read()
        #~ self.write({'abin': base64.encodestring(pic_data)})
        #~ pic_data = StringIO()
        #~ plt.savefig(pic_data)
        #~ print'pic_data',pic_data
        #~ self.abin=base64.encodestring(pic_data)
        #~ os.remove(tem)

